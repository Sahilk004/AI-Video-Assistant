# 🎥 AI Video Assistant

Turn any meeting recording or YouTube video into a structured summary, action items, key decisions, and open questions, then **chat with it** using Retrieval-Augmented Generation (RAG).

Give it a YouTube link or a local audio/video file, and the assistant will transcribe it, analyse it with an LLM, and let you ask follow-up questions grounded strictly in the transcript.

---

## ✨ Features

- **Flexible input**: paste a YouTube URL or point to a local audio/video file (anything `ffmpeg` can read).
- **Automatic audio prep**: downloads, converts to 16 kHz mono WAV, and splits long recordings into 10-minute chunks.
- **Two transcription engines**
  - **English** → [OpenAI Whisper](https://github.com/openai/whisper) running locally.
  - **Hinglish** → [Sarvam AI](https://www.sarvam.ai/) speech-to-text-translate, which transcribes *and* translates to English.
- **AI-generated insights**
  - 📌 Short professional title
  - 📋 Bullet-point summary (map-reduce over long transcripts)
  - ✅ Action items (task, owner, deadline)
  - 🔑 Key decisions
  - ❓ Open questions / follow-ups
- **Chat with your meeting**: a RAG pipeline (ChromaDB + OpenAI embeddings) answers questions using *only* what was said in the transcript.

---

## 🧠 How It Works

```
 YouTube URL / Local file
          │
          ▼
 ┌─────────────────────┐
 │  Audio Processing   │  yt-dlp · pydub · ffmpeg
 │  download → WAV     │  16 kHz mono, 10-min chunks
 └─────────┬───────────┘
           ▼
 ┌─────────────────────┐
 │   Transcription     │  English  → Whisper (local)
 │                     │  Hinglish → Sarvam AI (25s pieces)
 └─────────┬───────────┘
           ▼
 ┌─────────────────────┐
 │   LLM Analysis      │  Title · Summary · Action items
 │   (LangChain)       │  Key decisions · Open questions
 └─────────┬───────────┘
           ▼
 ┌─────────────────────┐
 │   RAG Chat          │  ChromaDB + OpenAI embeddings
 │                     │  top-4 retrieval → grounded answers
 └─────────────────────┘
```

### Pipeline details

| Stage | What happens |
|-------|--------------|
| **Input** | URLs starting with `http://` or `https://` are downloaded via `yt-dlp` as WAV; anything else is treated as a local file and converted with `pydub`. |
| **Chunking** | Audio is split into 10-minute WAV chunks so long recordings can be transcribed reliably. |
| **Transcription** | Whisper handles English. For Hinglish, each chunk is sliced into 25-second pieces (Sarvam's sync API rejects audio longer than 30s) and the results are joined. |
| **Summarisation** | The transcript is split (3000 chars, 200 overlap), each piece is summarised, then the partial summaries are merged into one final summary. |
| **Extraction** | Dedicated prompts pull out action items, decisions, and unresolved questions. |
| **RAG** | The transcript is split into 500-char chunks (50 overlap), embedded, stored in Chroma, and the top 4 matches are passed to the LLM for each question. |

---

## 📁 Project Structure

```
ai-video-assistant/
├── main.py                  # CLI entry point & pipeline orchestration
├── utils/
│   └── audio_processor.py   # Download, convert, and chunk audio
├── core/
│   ├── transcriber.py       # Whisper + Sarvam AI transcription
│   ├── summarizer.py        # Title generation & map-reduce summary
│   ├── extractor.py         # Action items, decisions, open questions
│   ├── rag_engine.py        # RAG chain construction & Q&A
│   └── vector_store.py      # ChromaDB build / load / retriever
├── .env                     # API keys (not committed)
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **[FFmpeg](https://ffmpeg.org/download.html)** installed and available on your `PATH` (required by `yt-dlp`, `pydub`, and Whisper)
- An **OpenAI API key**
- A **Sarvam AI API key** (only needed for Hinglish transcription)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ai-video-assistant.git
cd ai-video-assistant

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, these are the packages the project imports:

```text
yt-dlp
pydub
openai-whisper
requests
python-dotenv
langchain-openai
langchain-core
langchain-text-splitters
langchain-chroma
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key

# Only required for Hinglish transcription
SARVAM_API_KEY=your_sarvam_api_key

# Optional overrides
WHISPER_MODEL=small             # tiny | base | small | medium | large
SARVAM_STT_MODEL=saaras:v2.5
```

---

## 💻 Usage

```bash
python main.py
```

You'll be prompted for:

1. **Source**: a YouTube URL or a local file path
2. **Language**: `english` (default) or `hinglish`

Example session:

```text
Enter YouTube URL or local file path: https://www.youtube.com/watch?v=XXXXXXXXXXX
Language (english/hinglish): english

Starting AI Video Assistant
Detected YouTube URL. Downloading audio...
Chunking audio...
Audio ready — 3 chunk(s) created.
Using Whisper for transcription.
...
============================================================
📌 Title: Q3 Product Roadmap Planning

📋 Summary:
- ...

✅ Action Items:
1. ...

🔑 Key Decisions:
1. ...

❓ Open Questions:
1. ...
============================================================

💬 Chat with your meeting (type 'exit' to quit)

You: Who is responsible for the launch checklist?
🤖 Assistant: ...
```

### Use it as a library

```python
from main import run_pipeline
from core.rag_engine import ask_question

result = run_pipeline("meeting.mp4", language="english")

print(result["title"])
print(result["summary"])

answer = ask_question(result["rag_chain"], "What deadlines were mentioned?")
```

`run_pipeline` returns a dictionary with: `title`, `transcript`, `summary`, `action_items`, `key_decisions`, `open_questions`, and `rag_chain`.

---

## 🛠️ Tech Stack

| Purpose | Tools |
|---------|-------|
| Audio download | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Audio processing | [pydub](https://github.com/jiaaro/pydub), FFmpeg |
| Speech-to-text | [OpenAI Whisper](https://github.com/openai/whisper), [Sarvam AI](https://www.sarvam.ai/) |
| LLM orchestration | [LangChain](https://www.langchain.com/) |
| LLM & embeddings | OpenAI |
| Vector database | [ChromaDB](https://www.trychroma.com/) |

---

## ⚠️ Notes & Limitations

- Whisper runs locally; larger models (`medium`, `large`) are more accurate but need more RAM/VRAM and time.
- The Chroma store is persisted to `vector_db/`. Each run adds the new transcript to the same collection, so delete the folder between unrelated meetings if you want clean answers.
- The RAG assistant is instructed to answer only from the transcript and will say so when information isn't found.
- Only use content you have the right to download and process, and respect YouTube's Terms of Service.

---

## 🗺️ Roadmap Ideas

- [ ] Web UI (Streamlit / Gradio)
- [ ] Speaker diarization
- [ ] Export results to PDF / Markdown / Notion
- [ ] Per-meeting vector collections
- [ ] Support for more Indian languages via Sarvam

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Add your license here (e.g. [MIT](https://choosealicense.com/licenses/mit/)).

---

## 🙌 Acknowledgements

[OpenAI Whisper](https://github.com/openai/whisper) · [Sarvam AI](https://www.sarvam.ai/) · [LangChain](https://www.langchain.com/) · [ChromaDB](https://www.trychroma.com/) · [yt-dlp](https://github.com/yt-dlp/yt-dlp)