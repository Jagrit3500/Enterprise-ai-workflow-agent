# Technical Note — PDF Conversational Agent

## 1. Problem Statement

Build a conversational agent that answers queries strictly from a given PDF, with:
- No hallucination or outside knowledge
- Explicit refusal for out-of-scope queries
- Page-level citations on every answer
- Conversational follow-up support

---

## 2. System Architecture

```text
PDF Upload
    ↓
PDF Parser (PyMuPDF)
    ↓
Page-wise Text Extraction
    ↓
Chunker (900 chars, 150 overlap)
    ↓
Embedding Model (all-MiniLM-L6-v2)
    ↓
Vector Database (ChromaDB)

User Query
    ↓
Query Enrichment (chat history injected into prompt for context)
    ↓
Retriever (dynamic K cosine search)
    ↓
Evidence Filter (similarity threshold)
    ↓
Grounded LLM Agent (Groq)
    ↓
Citation Validator
    ↓
Final Answer / Refusal
```

---

## 3. Key Design Decisions

### 3.1 Strict Grounding via System Prompt
The LLM is constrained by a strict system prompt that:
- Allows answers only from retrieved context
- Enforces [Page X] citation format on every factual claim
- Returns a hard refusal string when evidence is absent
- Prohibits any outside knowledge or assumptions

### 3.2 Pre-LLM Evidence Filter
Before calling the LLM, retrieved chunks are filtered by similarity threshold.
- Chunks below threshold are rejected entirely
- LLM is never called with weak or unrelated evidence
- This ensures the LLM never sees low-confidence or irrelevant chunks, making the grounding constraint enforceable at the retrieval level

### 3.3 Post-LLM Citation Validator
After the LLM generates an answer, a programmatic check verifies:
- Answer contains at least one [Page X] citation
- Every cited page number exists in the retrieved chunks
- If validation fails, the answer is overridden with a refusal

### 3.4 Dynamic K Retrieval
K (number of retrieved chunks) is not fixed. It scales with document size:
- ≤ 40 chunks → K = 5
- 41–150 chunks → K = 8
- 151–450 chunks → K = 15
- > 450 chunks → K = 20

This prevents under-retrieval on large PDFs and reduces noise on small PDFs.

### 3.5 Configurable Threshold
Similarity threshold is not hardcoded. It is:
- Set as default in .env (0.60)
- Overridable via UI slider in real time
- Preset buttons for Balanced (0.60) and Strict (0.70)

This allows evaluators to tune grounding without touching code.

### 3.6 Conversation History
The last 3 turns of chat are injected into retrieval and LLM calls.
Follow-up queries like "tell me more about that" are enriched with
previous context before embedding, improving retrieval accuracy.

---

## 4. Trade-offs

| Decision | Benefit | Trade-off |
|---|---|---|
| Threshold 0.60 default | Better recall, usable immediately | Slight noise on borderline queries |
| Threshold 0.70 strict | Strong grounding, fewer weak matches | More refusals on valid queries |
| Chunk size 900 chars | Good context preservation | May split cross-page sentences |
| Chunk overlap 150 chars | Preserves context at boundaries | Slight redundancy in retrieval |
| Dynamic K | Scales with document size | Slight latency increase on large PDFs |
| Local embeddings | No API cost, offline capable | Lower quality than OpenAI embeddings |
| Pre + post grounding gates | Double validation, very robust | Two extra processing steps per query |

---

## 5. Observability

Every response includes a debug panel showing:
- Query text
- Active similarity threshold
- Total chunks in vector DB
- Dynamic K used
- Retrieved chunks count
- Is answerable flag
- Citation validity
- Pages cited
- Top similarity score

This supports full testability and failure diagnosis without code changes.

---

## 6. Testability

- 5 valid queries with expected citations
- 3 invalid queries with expected refusals
- Follow-up conversation tests
- Edge case queries (ambiguous, negation, out-of-scope)
- Large PDF test (68 pages, 216 chunks)
- Threshold variation testing (0.60 vs 0.70)
- 33 automated unit tests across parser, retriever, and validator

---

## 7. Limitations

- Scanned PDFs without a text layer are not supported
- Cross-page sentences may be split between chunks
- Numeric queries benefit from richer phrasing due to embedding limitations
- Groq free tier has a daily token limit (100k tokens/day)

---

## 8. Future Improvements

- Cross-encoder reranking for better chunk selection
- Multi-PDF support with source attribution
- Semantic chunking instead of character-based splitting
- Multilingual grounding and citation
- Streaming responses for better UX on large PDFs

---

## 9. Why This Design Works

This system enforces grounding at three levels:
1. Retrieval stage (threshold filtering)
2. Generation stage (strict system prompt)
3. Validation stage (citation verification)

This layered approach reduces hallucination risk significantly compared to
single-stage prompting or naive RAG pipelines. Most RAG systems rely only
on prompt-based grounding. This system adds programmatic enforcement before
and after the LLM call, making grounding verifiable and testable.