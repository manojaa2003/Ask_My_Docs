# 📄 Ask My Docs — PDF Q&A with RAG

A Streamlit web app that lets you upload PDFs, ask questions in natural language, and get grounded answers with source citations — powered by Retrieval-Augmented Generation (RAG).

---

## 🏗️ Architecture & Design Decisions

### Pipeline Overview

```
PDF Upload → Text Extraction → Chunking → Embedding → Chroma Vector Store
                                                              ↓
User Query → Embed Query → Similarity Search → Top-K Chunks → Groq LLM → Answer + Source
```

### Key Design Choices

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` — free, runs locally, no API cost.
- **Vector Store**: ChromaDB with disk persistence (`resources/vector_store/`) — embeddings survive app restarts.
- **LLM**: Groq API (llama-3.3-70b-versatile) — free tier, very fast inference.
- **Chunking**: `RecursiveCharacterTextSplitter` with `chunk_size=500`, `chunk_overlap=100` — balances context richness with retrieval precision.
- **Retrieval**: Top-3 chunks per query (`k=3`), fed as context to the LLM.
- **Prompt**: Instructs the LLM to answer only from provided context; returns "I don't know based on the provided article." when context is insufficient.
- **LangChain**: Used to structure the full RAG pipeline (loaders, splitters, retrievers, chains).

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ask-my-docs.git
cd ask-my-docs
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example env file and add your Groq API key:

```bash
cp .env.example .env
```

Open `.env` and fill in your key:

```
GROQ_API_KEY=your_groq_api_key_here
```

> **Get a free Groq API key**: Go to [https://console.groq.com/](https://console.groq.com/), sign up for free, and create an API key under **API Keys**.

### 5. Run the App

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`.

---

## 🌐 Deployment (Streamlit Community Cloud)

1. Push your repository to GitHub (make sure `.env` is in `.gitignore`).
2. Go to [https://share.streamlit.io/](https://share.streamlit.io/) and sign in.
3. Click **New app** → select your repo, branch, and set `main.py` as the entry point.
4. Under **Advanced settings → Secrets**, add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
5. Click **Deploy**.

---

## 📁 Project Structure

```
ask-my-docs/
├── main.py               # Streamlit UI — file upload, chat input/output
├── rag.py                # RAG pipeline — PDF loading, chunking, embedding, retrieval, LLM call
├── requirements.txt      # Python dependencies
├── .env                  # Secret keys (never committed)
├── .env.example          # Placeholder for secrets
├── resources/
│   └── vector_store/     # Chroma persisted embeddings (auto-created)
└── uploaded_pdfs/        # Temporarily stores uploaded PDF files (auto-created)
```

---

## 🔧 Environment Variables

| Variable       | Description                        | Required |
|----------------|------------------------------------|----------|
| `GROQ_API_KEY` | API key for Groq LLM inference     | Yes      |

See `.env.example` for the template.

---

## 📦 Tech Stack

| Component         | Library / Tool                              |
|-------------------|---------------------------------------------|
| UI                | Streamlit                                   |
| PDF Loading       | LangChain `PyPDFLoader`                     |
| Text Splitting    | LangChain `RecursiveCharacterTextSplitter`  |
| Embeddings        | `sentence-transformers/all-MiniLM-L6-v2`   |
| Vector Store      | ChromaDB (local, persisted to disk)         |
| LLM               | Groq API — `llama-3.3-70b-versatile`        |
| Orchestration     | LangChain (chains, retrievers, prompts)     |

---

## 💬 Sample Q&A

The following examples were run against a set of documents about human biology
---

**Q1: what is the function of brain?**

> The function of the brain is to act as the control center of the nervous system, responsible for thinking, memory, emotions, movement, and body coordination. It receives information from different parts of the body through nerves, processes that information, and produces responses.The brain also controls nearly every activity of the body, processes information, stores memories, and coordinates actions.
>
> *Source: human_brain_information.pdf — Page 1*

---

**Q2: what connects the brain to spinal cord?**

> The brainstem connects the brain to the spinal cord.
>
> *Source: human_brain_information.pdf — Page 1*

---

**Q3: what is the function of brain stem?**

> The brainstem connects the brain to the spinal cord and controls essential life functions such as breathing, heartbeat. It also maintains body balance, posture, and muscle coordination, ensuring smooth and accurate body movements.
>
> *Source: human_brain_information.pdf — Page 1*

---

**Q4: what is the function of pancreas?**

> The function of the pancreas is to produce digestive enzymes.
>
> *Source: human_digestive_system.pdf — Page 1*

---

## ✅ What Worked Well

- ChromaDB persistence meant re-runs were fast after the first ingestion.
- The "I don't know" fallback in the prompt worked reliably for out-of-scope questions.
- Page number citations came through accurately via LangChain's `PyPDFLoader` metadata.
- LangChain's LCEL chains made it clean to wire retriever → prompt → LLM → parser.

## ⚠️ What Didn't Work / Known Limitations

- `k=2` retrieval can miss relevant context for complex multi-part questions; increasing to `k=4` or `k=5` may improve accuracy at the cost of token usage.
- Scanned PDFs (image-based) are not supported — `PyPDFLoader` only handles text-layer PDFs.
- The app resets the Chroma collection on every "Process PDFs" click, so you cannot incrementally add more PDFs without re-processing all of them.
- No authentication or rate limiting — not suitable for public deployment without additional safeguards.

---

## 🧪 Testing

Manual testing was performed by:

1. Uploading 3+ PDFs with known content.
2. Asking factual questions with known answers to verify retrieval accuracy.
3. Asking out-of-scope questions to verify the "I don't know" fallback.
4. Verifying source filenames and page numbers in citations.
5. Restarting the app to confirm ChromaDB persistence works correctly.

---

## 📬 Submission

- **Live APP URL**: https://askmydocs-drdfhjzayzjuryjg38es2b.streamlit.app/
- **Email**: `aamanoj743@gmail.com` 
