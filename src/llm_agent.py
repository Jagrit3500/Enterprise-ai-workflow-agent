import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from groq import Groq
from src.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    validate_groq_key
)
from src.retriever import retrieve_and_filter, format_context
from src.citation_validator import get_confidence_label

# Validate key on import
validate_groq_key()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a strict PDF-grounded assistant.

Your rules:
1. Answer ONLY using the provided context below.
2. Every factual claim MUST include a citation in format: [Page X]
3. If the answer is not present in the context, respond with EXACTLY:
   "I could not find this information in the uploaded PDF."
4. Never use outside knowledge or general knowledge.
5. Never guess or make assumptions beyond what the context says.
6. If the question is partially answerable, answer only the part supported.
7. Be concise and factual.
8. Always respond in the same language as the user's query.
9. Always keep citations in the format [Page X] in English.

Context will be provided in the format:
[Page X]
... text ...
"""


def enrich_query_with_history(
    query: str,
    chat_history: list[dict]
) -> str:
    """
    Combine recent chat history with current query
    for better retrieval on follow-up questions.
    """
    if not chat_history:
        return query

    last_turns = chat_history[-4:]
    history_text = ""
    for turn in last_turns:
        if turn["role"] == "user":
            history_text += f"Previous question: {turn['content']}\n"

    is_followup = len(query.split()) < 8 or any(
        word in query.lower()
        for word in ["it", "this", "that", "more", "explain",
                     "elaborate", "second", "first", "above"]
    )

    if is_followup and history_text:
        return f"{history_text}Current question: {query}"

    return query


def build_messages(
    query: str,
    context: str,
    chat_history: list[dict]
) -> list[dict]:
    """
    Build message list for Groq API call.
    Includes last 3 turns of chat history.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    recent_history = chat_history[-6:]
    messages.extend(recent_history)

    user_message = f"""Context from PDF:
{context}

Question: {query}

Remember: Answer only from the context above. Cite page numbers as [Page X]."""

    messages.append({"role": "user", "content": user_message})
    return messages


def extract_cited_pages(answer: str) -> list[int]:
    """
    Extract page numbers cited in answer like [Page 3].
    """
    pattern = r'\[Page (\d+)\]'
    matches = re.findall(pattern, answer)
    return list(set(int(m) for m in matches))


def get_answer(
    query: str,
    chat_history: list[dict] | None = None,
    threshold: float | None = None
) -> dict:
    """
    Main function — retrieves evidence and generates grounded answer.
    threshold: optional override from UI slider.
    """
    if chat_history is None:
        chat_history = []

    # Step 1 — enrich query with history for follow-up questions
    enriched_query = enrich_query_with_history(query, chat_history)

    # Step 2 — retrieve and filter evidence
    chunks, is_answerable, actual_k = retrieve_and_filter(
        enriched_query,
        threshold=threshold
    )

    # Step 3 — if no evidence, return refusal immediately
    if not is_answerable:
        return {
            "answer": "I could not find this information in the uploaded PDF.",
            "chunks": [],
            "is_answerable": False,
            "pages_cited": [],
            "confidence": "none",
            "actual_k": actual_k
        }

    # Step 4 — format context for LLM
    context = format_context(chunks)

    # Step 5 — build messages with history
    messages = build_messages(query, context, chat_history)

    # Step 6 — call Groq LLM
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

    answer = response.choices[0].message.content.strip()

    # Step 7 — extract cited pages
    pages_cited = extract_cited_pages(answer)

    # Step 8 — get confidence (single source of truth)
    confidence = get_confidence_label(chunks)["label"]

    return {
        "answer": answer,
        "chunks": chunks,
        "is_answerable": True,
        "pages_cited": pages_cited,
        "confidence": confidence,
        "actual_k": actual_k
    }


if __name__ == "__main__":
    print("=" * 50)
    print("TEST 1 — Valid query")
    print("=" * 50)
    result = get_answer("What is Scaler School of Technology?")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Pages cited: {result['pages_cited']}")
    print(f"Chunks used: {len(result['chunks'])}")

    print("\n" + "=" * 50)
    print("TEST 2 — Out of scope query")
    print("=" * 50)
    result2 = get_answer("Who is the president of USA?")
    print(f"Answer: {result2['answer']}")
    print(f"Is answerable: {result2['is_answerable']}")

    print("\n" + "=" * 50)
    print("TEST 3 — Follow up with chat history")
    print("=" * 50)
    history = [
        {"role": "user", "content": "What are the main requirements?"},
        {"role": "assistant", "content": result["answer"]}
    ]
    result3 = get_answer(
        "Tell me more about the second point",
        chat_history=history
    )
    print(f"Answer: {result3['answer']}")
    print(f"Confidence: {result3['confidence']}")
    print(f"Pages cited: {result3['pages_cited']}")