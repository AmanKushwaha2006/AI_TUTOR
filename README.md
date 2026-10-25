# 🎓 ORION: AI Tutor - Voice-Enabled Intelligent Multi-Agent Learning Assistant

[![GitHub Repository](https://img.shields.io/badge/GitHub-AmanKushwaha2006%2FAI__TUTOR-blue?logo=github)](https://github.com/AmanKushwaha2006/AI_TUTOR)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen?logo=python)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%20%7C%20LangGraph%20%7C%20LangChain-orange)](https://github.com/langchain-ai/langgraph)
[![LLM Provider](https://img.shields.io/badge/LLM-Groq%20Cloud-purple)](https://groq.com/)
[![Local Embeddings](https://img.shields.io/badge/Embeddings-Ollama%20(mxbai--embed--large)-black)](https://ollama.com/)

**ORION (The Voice of Knowledge)** is an intelligent, multimodal AI tutor application built using **Flask**, **LangGraph**, **LangChain**, and high-speed **Groq LLMs**. 

It features an autonomous **multi-agent pipeline** (Researcher, Drafter, Verifier, Enhancer), personalized long-term and short-term memory with **Mem0**, local document understanding via **RAG (FAISS + Ollama embeddings)**, offline Indian-English speech recognition via **Vosk**, and clean, human-readable list-wise formatting.

---

## 🌟 Key Features

### 🧠 1. Multi-Agent LangGraph Architecture
Unlike simple single-prompt bots, ORION routes queries through a multi-agent state graph:
- **Memory Retrieval Agent**: Pulls relevant short-term context and long-term user memories via Mem0.
- **Researcher Agent**: Intelligently searches through uploaded PDF documents (RAG) or conducts multi-source live web research (Tavily, Wikipedia, ArXiv, Web Scraper).
- **Drafter Agent**: Formulates a detailed first-pass educational response.
- **Verifier Agent**: Validates the draft against research evidence to eliminate hallucinations.
- **Enhancer Agent**: Refines tone into structured, clear, human-friendly bullet lists without cluttered or unreadable tables.

### 📄 2. Dual Operation Modes (RAG vs. Live Web)
- **Document Mode (RAG Enabled)**: Upload single or multiple PDFs. ORION extracts, chunks, and embeds them into a local FAISS vector store using local Ollama embeddings (`mxbai-embed-large`), answering questions specifically grounded in your documents.
- **Web Research Mode**: When no documents are uploaded, ORION autonomously searches the live web using Tavily AI, Wikipedia, and ArXiv to find up-to-date facts and learning materials.

### 🎙️ 3. Voice-Enabled Learning (Offline & Low Latency)
- **Speech-to-Text**: High-accuracy offline speech recognition powered by the **Vosk Indian-English model** (`vosk-model-en-in-0.5`), requiring no external speech API quotas.
- **Text-to-Speech**: Seamless spoken responses using `pyttsx3` with real-time audio controls.

### 📝 4. Human-Readable, List-Wise Formatting
- Built-in `marked.js` markdown renderer converts responses into clean, scannable bullet points, bold key terms, and highlighted concepts.
- Strict anti-bloat prompting ensures information is presented simply and directly without unreadable raw ASCII tables.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Modern Glassmorphism & Micro-animations), JavaScript, Marked.js |
| **Backend Framework** | Flask (Python) |
| **Orchestration** | LangGraph, LangChain Classic Agents |
| **LLM Inference** | Groq Cloud (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`) |
| **Embeddings** | Ollama local embedding daemon (`mxbai-embed-large:latest`, 1024-dim) |
| **Vector Database** | FAISS (Facebook AI Similarity Search) |
| **Memory System** | Mem0 (`mem0ai`) cloud memory platform |
| **Web Research Tools** | Tavily AI Search, Wikipedia API, ArXiv API, BeautifulSoup4, SerpAPI |
| **Speech-to-Text (STT)**| Vosk Offline Speech Recognition (`vosk-model-en-in-0.5`) |
| **Text-to-Speech (TTS)**| `pyttsx3` |

---

## 📁 Project Structure

```plaintext
AI_TUTOR/
├── agents/                       # LangGraph agent definitions
│   ├── agent_utils.py            # Groq LLM client configuration & rate-limit wrappers
│   ├── drafter.py                # Educational draft synthesis agent
│   ├── enhancer.py               # Tone, clarity, and list-wise formatting enhancer
│   ├── researcher.py             # ReAct research agent (Tavily, ArXiv, Wikipedia, RAG)
│   ├── summarizer.py             # Research extraction and summarization agent
│   └── verifier.py               # Hallucination check & verification agent
│
├── graph/                        # LangGraph workflow orchestration
│   ├── helper_functions/         # Prompts, truncation, and logging utilities
│   ├── graph_builder.py          # StateGraph assembly & conditional edge routing
│   └── nodes.py                  # Agent graph node wrappers
│
├── RAG/                          # Retrieval-Augmented Generation pipeline
│   └── rag_pipeline.py           # PyPDF text extraction, character splitting & FAISS indexing
│
├── state/                        # Context & Memory management
│   ├── context.py                # TypedDict state schema for LangGraph
│   └── memory.py                 # Mem0 short-term & long-term memory manager
│
├── tools/                        # Search & scraping utilities
│   ├── arxiv.py                  # Scientific paper search
│   ├── open_link.py              # Automated browser link opener
│   ├── rag_tool.py               # Document retrieval tool wrapper
│   ├── tavily.py                 # Real-time Tavily search tool
│   ├── web_scraper.py            # BeautifulSoup4 HTML scraper
│   └── wikipedia.py              # Wikipedia encyclopedic summary search
│
├── voice_assist/                 # Speech integration
│   ├── speech_to_text.py         # Vosk microphone audio recognition
│   └── text_to_speech.py         # pyttsx3 voice synthesis & thread manager
│
├── testFrontend/FlaskApp/        # Web Application UI
│   ├── static/
│   │   ├── script.js             # UI events, mic recording, Marked.js parsing
│   │   └── style.css             # Responsive theme, typography, chat bubbles
│   └── templates/
│       └── index.html            # Main tutor chat interface
│
├── app.py                        # Root entry point to run Flask web app (Port 5500)
├── main.py                       # CLI interface to run ORION in terminal mode
├── tutor.py                      # Core execution pipeline runner
├── requirements.txt              # Complete Python package dependencies
├── .env.example                  # Template for required environment variables
└── README.md                     # Project documentation
```

---

## 🚀 Complete Step-by-Step Setup Guide

Follow these steps exactly to set up and run the project smoothly on your local machine:

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.10+** (Tested on Python 3.11, 3.12, 3.13)
- **Git**
- **Microphone & Speaker** (for voice interaction)

---

### 2. Clone the Repository
Clone the repository to your local directory:
```bash
git clone https://github.com/AmanKushwaha2006/AI_TUTOR.git
cd AI_TUTOR
```

---

### 3. Create & Activate a Virtual Environment

It is strongly recommended to use a dedicated virtual environment:

- **Windows (PowerShell)**:
  ```powershell
  python -m venv env
  .\env\Scripts\Activate.ps1
  ```
  > *Note: If PowerShell shows an `Execution_Policies` restriction, run:*
  > `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` *and then activate.*

- **Windows (Command Prompt - cmd.exe)**:
  ```cmd
  python -m venv env
  env\Scripts\activate.bat
  ```

- **macOS / Linux / Git Bash**:
  ```bash
  python3 -m venv env
  source env/bin/activate
  ```

---

### 4. Install All Python Dependencies
Run `pip` to install all required libraries:
```bash
pip install -r requirements.txt
```

---

### 5. Install & Set Up Ollama (for Local Document Embeddings)

ORION uses **Ollama** locally to generate embeddings for document chunks during PDF uploads:

1. Download and install Ollama from [https://ollama.com/download](https://ollama.com/download).
2. Start the Ollama background service:
   ```bash
   ollama serve
   ```
3. In a new terminal window, pull the high-performance `mxbai-embed-large` embedding model:
   ```bash
   ollama pull mxbai-embed-large
   ```
4. Verify that Ollama is running at `http://127.0.0.1:11434`.

---

### 6. Download the Vosk Speech Model

For fast offline Indian-English speech-to-text recognition:

1. Download the lightweight model zip file:
   👉 **[vosk-model-en-in-0.5.zip](https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip)** (~36 MB)
2. Extract the downloaded folder directly into the root directory of the project:
   ```plaintext
   AI_TUTOR/
   ├── vosk-model-en-in-0.5/
   │   ├── am/
   │   ├── conf/
   │   ├── graph/
   │   └── ivector/
   ├── app.py
   └── ...
   ```

---

### 7. Configure Environment Variables (`.env`)

Create your `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```
*(On Windows PowerShell, use: `Copy-Item .env.example .env`)*

Open `.env` and fill in your API credentials:

```env
# 1. Groq API Key (Required for LLM Agents)
# Get your free key at: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_groq_api_key_here

# 2. Tavily Search API Key (Required for live web search)
# Get your free key at: https://app.tavily.com/
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# 3. Mem0 Memory API Key (Required for personalized user memory)
# Get your free key at: https://app.mem0.ai/dashboard/api-keys
MEM_AI_API_KEY=m0-your_mem0_api_key_here

# 4. SerpAPI Key (Optional fallback search)
# Get from: https://serpapi.com/
SERP_API_KEY=your_serp_api_key_here

# Model Overrides (Optional defaults)
GROQ_LARGE_MODEL="openai/gpt-oss-120b"
GROQ_FAST_MODEL="openai/gpt-oss-20b"
```

---

### 8. Run the Application

Launch the full web application:
```bash
python app.py
```

Once started, open your web browser and navigate to:
👉 **[http://localhost:5500](http://localhost:5500)**

*(Alternatively, to run ORION in terminal/CLI mode, execute `python main.py`)*

---

## 💡 How to Use ORION

1. **Ask Any Question**: Type your topic (e.g., *"Explain Photosynthesis"*, *"What are the recent updates in Quantum Computing?"*) or click the 🎙️ **Microphone icon** to speak.
2. **Upload Documents (PDF RAG)**: Click **Upload PDFs** or select a folder. ORION will extract text, create embeddings, and switch the status dot to green (**PDFs loaded - RAG enabled**). Now, any question you ask will prioritize facts from your uploaded document.
3. **Listen to Responses**: ORION can automatically vocalize responses via the offline text-to-speech engine. Click **Stop Speech** anytime to pause audio.

---

## 🔧 Troubleshooting & Tips

- **PowerShell Activation Error (`Activate.ps1 cannot be loaded`)**:
  Run this command in PowerShell before activating:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
- **Port 5500 Already in Use**:
  If port 5500 is occupied, you can change the port number in the last line of `app.py`:
  ```python
  app.run(host="0.0.0.0", port=5500, debug=True)
  ```
- **Ollama Connection Refused**:
  Make sure `ollama serve` is running in the background and `ollama list` displays `mxbai-embed-large:latest`.
- **Speech Recognition Model Not Found**:
  Verify that the folder name in your root directory is strictly named `vosk-model-en-in-0.5`.

---

## 👤 Author & Contributions

- **Created by**: **Aman Kushwaha** ([@AmanKushwaha2006](https://github.com/AmanKushwaha2006))
- **Repository**: [https://github.com/AmanKushwaha2006/AI_TUTOR](https://github.com/AmanKushwaha2006/AI_TUTOR)

Contributions, feature suggestions, and stars are welcome! Feel free to open an issue or submit a pull request.
