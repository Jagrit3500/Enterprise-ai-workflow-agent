# Enterprise AI Workflow Agent
### PDF-Grounded Conversational System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://enterprise-ai-workflow-agent-9kzrt6ok4vjktzwccpdguc.streamlit.app/)

[![Demo Video](https://img.shields.io/badge/Demo%20Video-Google%20Drive-4285F4?style=for-the-badge&logo=googledrive)](https://drive.google.com/file/d/1vyWUq-QfFEdc9MKBe1tX46A-aPx3qsp-/view?usp=sharing)

A strictly grounded RAG-based conversational agent that answers questions exclusively from uploaded PDFs with page-level citations. Minimizes hallucination through strict grounding and validation. Every answer is cited. Out-of-scope questions are refused.

---

## Features

- Upload any PDF and chat with it instantly
- Every answer includes page citations like [Page X]
- Refuses out-of-scope questions cleanly
- Configurable similarity threshold via UI slider
- Full observability with debug panel
- Conversation history for follow-up questions
- Dynamic K retrieval scales with PDF size

---

## Tech Stack

| Component | Technology |
|---|---|
| PDF Parsing | PyMuPDF |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| LLM | Groq (llama-3.3-70b-versatile) |
| Frontend | Streamlit |

---

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
│   ├── test_parser.py          # 9 tests
│   ├── test_retriever.py       # 11 tests
│   └── test_agent.py           # 13 tests
├── docs/
│   ├── technical_note.md       # Architecture + decisions
│   └── test_cases.md           # Test instructions for evaluators
├── uploads/                    # runtime (ignored)
├── chroma_db/                  # runtime (ignored)
├── app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

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
Copy `.env.example` to `.env` and fill in your Groq API key:
```bash
cp .env.example .env
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## Usage

1. Upload any PDF from the sidebar
2. Ask questions about the document
3. Get answers with page citations
4. Adjust similarity threshold slider if needed
5. Out-of-scope questions are automatically refused

---

## Quick Demo

1. Upload a PDF
2. Ask: "What is this document about?"
3. Ask: "Summarize the key points"
4. Ask: "Who is the CEO of Google?"

Expected:
- First two → grounded answers with citations
- Last → refusal

This demonstrates strict grounding and hallucination prevention.

---

## Architecture

```text
PDF Upload → Parser → Chunker → Embedder → ChromaDB
User Query → Query Enricher → Retriever → Evidence Filter
Grounded LLM Agent → Citation Validator → Final Answer / Refusal
```

---

## Threshold Guide

| Threshold | Behavior |
|---|---|
| 0.50–0.60 | Balanced — answers more questions |
| 0.65–0.75 | Recommended — strict grounding |
| 0.75–0.90 | Very strict — only high confidence answers |

---

## Dynamic K Retrieval

| PDF Size | Chunks | K Used |
|---|---|---|
| Small | ≤ 40 chunks | 5 |
| Medium | 41–150 chunks | 8 |
| Medium-large | 151–450 chunks | 15 |
| Very large | > 450 chunks | 20 |

---

## Large PDF Validation

Tested on a 68-page McKinsey report with 216 indexed chunks. Dynamic K increased retrieval depth to 15 chunks and correctly answered numeric and business-function questions with citations.

---

## Tests

33 tests across 3 files — all passing.

```bash
python tests/test_parser.py
python tests/test_retriever.py
python tests/test_agent.py
```

See `docs/test_cases.md` for full evaluator test instructions.

---

## Live Demo & Video

- 🌐 **Deployed App:** https://enterprise-ai-workflow-agent-9kzrt6ok4vjktzwccpdguc.streamlit.app/

- 🎥 **Demo Video:** https://drive.google.com/file/d/1vyWUq-QfFEdc9MKBe1tX46A-aPx3qsp-/view?usp=sharing

---

## Limitations

- Numeric queries may need richer phrasing
- Scanned PDFs without text layer not supported
- Cross-page sentences may split between chunks

---

## Multilingual Support

The system responds in the same language the user writes in.
Citations remain in English format [Page X] regardless of language.

Tested languages: English, Hindi, Spanish