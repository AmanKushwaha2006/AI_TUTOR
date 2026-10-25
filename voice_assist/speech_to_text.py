import os
import queue
import sounddevice as sd
import vosk
import json

import time

# Path to the Vosk model
MODEL_PATH = "vosk-model-en-in-0.5"

# Global variable to control stopping and lazy loaded model
stop_listening = False
model = None
sample_rate = 16000
q = queue.Queue()

def get_model():
    """Lazy loads the Vosk model so app startup is not blocked if model is missing."""
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            print(f"\n[Voice] Vosk model not found at '{MODEL_PATH}'.", flush=True)
            print("[Voice] To enable voice input, download from https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip and extract to the project root.", flush=True)
            return None
        model = vosk.Model(MODEL_PATH)
    return model

def callback(indata, frames, time_info, status):
    """Callback function to put audio data into a queue."""
    if status:
        print(f"⚠️ Audio status: {status}", flush=True)
    q.put(bytes(indata))

def speech_to_text():
    """
    Captures audio and accumulates phrases until stop_speech_recognition() is called
    or a maximum duration is reached. Does not cut off on intermediate pauses.
    """
    global stop_listening
    stop_listening = False

    vosk_model = get_model()
    if not vosk_model:
        return ""

    # Clear any leftover audio in queue
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break

    print("\n🎤 Listening (Vosk)... Speak your full sentence and press Stop when finished.", flush=True)

    recognized_phrases = []

    try:
        with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(vosk_model, sample_rate)
            rec.SetWords(True)

            start_time = time.time()
            max_duration = 60.0  # Max 60 seconds listening safety cap

            while not stop_listening:
                if time.time() - start_time > max_duration:
                    print("⏱️ Max recording duration reached (60s)", flush=True)
                    break

                try:
                    data = q.get(timeout=0.1)
                except queue.Empty:
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        recognized_phrases.append(text)
                        print(f"🗣️ Heard phrase: '{text}'", flush=True)

            # Drain any remaining audio data in queue collected right before stopping
            while not q.empty():
                try:
                    data = q.get_nowait()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip()
                        if text:
                            recognized_phrases.append(text)
                except queue.Empty:
                    break

            # Extract any remaining final words
            final_result = json.loads(rec.FinalResult())
            final_text = final_result.get("text", "").strip()
            if final_text:
                recognized_phrases.append(final_text)
                print(f"🗣️ Final phrase: '{final_text}'", flush=True)

    except Exception as e:
        print(f"\n❌ Error during speech recognition: {e}", flush=True)

    full_sentence = " ".join(recognized_phrases).strip()
    print(f"✅ Full Transcribed Sentence: '{full_sentence}'", flush=True)
    return full_sentence

def stop_speech_recognition():
    """Sets the global flag to stop recognition and return the full sentence."""
    global stop_listening
    stop_listening = True
    print("🛑 Speech recognition stopped by user", flush=True)

# Test Run
if __name__ == "__main__":
    print("Transcribed Text:", speech_to_text())
