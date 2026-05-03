# Enterprise AI Workflow Agent
### PDF-Grounded Conversational System

A strictly grounded RAG-based conversational agent that answers questions exclusively from uploaded PDFs with page-level citations.

## Features

- Upload any PDF and chat with it instantly
- Every answer includes page citations like [Page X]
- Refuses out-of-scope questions cleanly
- Configurable similarity threshold via UI slider
- Full observability with debug panel
- Conversation history for follow-up questions
- Dynamic K retrieval based on PDF size

## Tech Stack

| Component | Technology |
|---|---|
| PDF Parsing | PyMuPDF |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| LLM | Groq (llama-3.3-70b-versatile) |
| Frontend | Streamlit |

## Project Structure

```
enterprise-ai-workflow-agent/
├── src/
│   ├── config.py               # All settings via .env
│   ├── pdf_parser.py           # PDF ingestion + chunking
│   ├── embedder.py             # Embeddings + ChromaDB
│   ├── retriever.py            # Similarity search + dynamic K
│   ├── llm_agent.py            # Grounded LLM + chat history
│   └── citation_validator.py  # Citation validation + confidence
├── tests/
│   ├── test_parser.py
│   ├── test_retriever.py
│   └── test_agent.py
├── docs/
│   ├── technical_note.md
│   └── test_cases.md
├── uploads/
├── chroma_db/
├── app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd enterprise-ai-workflow-agent
```

### 2. Create virtual environment
```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Contents of `.env.example`:
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=1024
TEMPERATURE=0.0
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=50
CHUNK_SIZE=900
CHUNK_OVERLAP=150
CHROMA_DB_PATH=chroma_db
COLLECTION_NAME=pdf_chunks
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.60
UPLOAD_DIR=uploads
TRANSFORMERS_OFFLINE=1
HF_DATASETS_OFFLINE=1
```

### 5. Run the app
```bash
streamlit run app.py
```

## Usage

1. Upload any PDF from the sidebar
2. Ask questions about the document
3. Get answers with page citations
4. Adjust similarity threshold slider if needed
5. Out-of-scope questions are automatically refused

## Threshold Guide

| Threshold | Behavior |
|---|---|
| 0.50-0.60 | Balanced — answers more questions |
| 0.65-0.75 | Recommended — strict grounding |
| 0.75-0.90 | Very strict — only high confidence answers |

## Dynamic K Retrieval

| PDF Size | Chunks | K Used |
|---|---|---|
| Small | ≤ 40 chunks | 5 |
| Medium | 41–150 chunks | 8 |
| Medium-large | 151–450 chunks | 15 |
| Very large | > 450 chunks | 20 |

## Large PDF Validation

Tested on a 68-page McKinsey report with 216 indexed chunks. Dynamic K increased retrieval depth to 15 chunks and correctly answered numeric and business-function questions with citations.

## Test Cases

See `docs/test_cases.md` for full test cases.

### Quick Test — Valid Queries
1. What is this document about?
2. What are the main topics covered?
3. Summarize the key points.
4. What are the requirements mentioned?
5. What activities are included?

### Quick Test — Invalid Queries
1. Who is the CEO of Google?
2. What is the capital of France?
3. Explain quantum computing.

## Architecture

```text
PDF Upload → Parser → Chunker → Embedder → ChromaDB
User Query → Query Enricher → Retriever → Evidence Filter
Grounded LLM Agent → Citation Validator → Final Answer / Refusal
```

## Limitations

- Numeric queries may need richer phrasing
- Scanned PDFs without text layer not supported
- Cross-page sentences may split between chunks