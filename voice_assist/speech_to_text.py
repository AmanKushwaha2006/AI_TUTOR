import os
import queue
import sounddevice as sd
import vosk
import json

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

def callback(indata, frames, time, status):
    """Callback function to put audio data into a queue."""
    if status:
        print(f"⚠️ Audio status: {status}", flush=True)
    q.put(bytes(indata))

def speech_to_text():
    """Captures audio and converts it to text using Vosk (offline)."""
    global stop_listening
    stop_listening = False

    vosk_model = get_model()
    if not vosk_model:
        return ""

    print("\n🎤 Listening (Vosk)...", flush=True)

    try:
        with sd.RawInputStream(samplerate=sample_rate, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(vosk_model, sample_rate)

            while True:
                if stop_listening:
                    return ""

                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        return text
                # Optionally, handle partial results
                # else:
                    # print("Cannot recognize speech yet...", flush=True)
    except Exception as e:
        print(f"\nAn error occurred: {e}", flush=True)
        return ""

def stop_speech_recognition():
    """Sets the global flag to stop recognition."""
    global stop_listening
    stop_listening = True
    print("🛑 Speech recognition stopped by user", flush=True)

# Test Run
if __name__ == "__main__":
    print("Transcribed Text:", speech_to_text())
