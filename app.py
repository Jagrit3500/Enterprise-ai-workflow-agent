import sys
import os
sys.path.insert(0, os.path.abspath("."))

import streamlit as st
from src.pdf_parser import parse_pdf, save_uploaded_pdf
from src.embedder import embed_chunks, get_chroma_client, get_or_create_collection
from src.llm_agent import get_answer
from src.citation_validator import build_final_response
from src.config import SIMILARITY_THRESHOLD, GROQ_MODEL

# ─── Page Config ────────────────────────────────────
st.set_page_config(
    page_title="PDF Conversational Agent",
    page_icon="📄",
    layout="wide"
)

# ─── Session State Init ─────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "threshold" not in st.session_state:
    st.session_state.threshold = float(SIMILARITY_THRESHOLD)

if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0


# ─── Sidebar ────────────────────────────────────────
with st.sidebar:
    st.title("📄 PDF Agent")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"],
        help="Upload any PDF to start chatting"
    )

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.pdf_name:
            with st.spinner("Processing PDF..."):
                pdf_path = save_uploaded_pdf(uploaded_file)
                chunks = parse_pdf(pdf_path)
                success = embed_chunks(chunks)

                if success:
                    st.session_state.pdf_loaded = True
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.chat_history = []
                    st.session_state.messages = []
                    st.session_state.total_chunks = len(chunks)
                    st.success(
                        f"✅ PDF loaded!\n\n"
                        f"{len(chunks)} chunks indexed."
                    )
                else:
                    st.error("Failed to process PDF. Please try again.")

    if st.session_state.pdf_loaded:
        st.markdown("---")
        st.markdown("**Active PDF:**")
        st.markdown(f"`{st.session_state.pdf_name}`")
        st.markdown(f"Chunks indexed: `{st.session_state.total_chunks}`")
        st.markdown("---")

        st.markdown("**Settings**")

        # Threshold slider — fully configurable from UI
        st.session_state.threshold = st.slider(
            "Similarity threshold",
            min_value=0.40,
            max_value=0.90,
            value=st.session_state.threshold,
            step=0.01,
            help="Lower = answers more questions. Higher = stricter grounding."
        )

        st.caption("Recommended: 0.65–0.75 for stricter grounding")

        # Preset buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚖️ Balanced (0.60)"):
                st.session_state.threshold = 0.60
                st.rerun()
        with col2:
            if st.button("🔒 Strict (0.70)"):
                st.session_state.threshold = 0.70
                st.rerun()

        st.markdown(f"Model: `{GROQ_MODEL}`")
        st.markdown("---")

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Upload any PDF")
    st.markdown("2. Ask questions about it")
    st.markdown("3. Get cited answers")
    st.markdown("4. Out-of-scope questions are refused")


# ─── Main Area ──────────────────────────────────────
st.title("📄 PDF Conversational Agent")
st.markdown("*Strictly grounded answers with page citations*")
st.markdown("---")

if not st.session_state.pdf_loaded:
    st.info("👈 Upload a PDF from the sidebar to get started.")

    st.markdown("### What this agent can do:")
    col1, col2 = st.columns(2)
    with col1:
        st.success(
            "✅ **Answers from PDF**\n"
            "Answers strictly from uploaded PDF with page citations"
        )
    with col2:
        st.error(
            "❌ **Refuses out-of-scope**\n"
            "Refuses questions not found in the PDF"
        )

else:
    # ─── Display existing chat messages ─────────────
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and "metadata" in message:
                meta = message["metadata"]
                confidence = meta.get("confidence", "none")

                if confidence == "high":
                    st.success("Confidence: HIGH")
                elif confidence == "medium":
                    st.warning("Confidence: MEDIUM")
                elif confidence == "low":
                    st.error("Confidence: LOW")

                if meta.get("chunks"):
                    with st.expander("📑 View Retrieved Evidence"):
                        for i, chunk in enumerate(meta["chunks"]):
                            st.markdown(
                                f"**Chunk {i+1}** | "
                                f"Page {chunk['page']} | "
                                f"Similarity: {chunk['similarity']:.3f}"
                            )
                            st.text(chunk["text"][:300] + "...")
                            st.markdown("---")

    # ─── Chat Input ─────────────────────────────────
    if query := st.chat_input("Ask a question about your PDF..."):

        st.session_state.messages.append({
            "role": "user",
            "content": query
        })

        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching PDF..."):
                try:
                    raw_result = get_answer(
                        query=query,
                        chat_history=st.session_state.chat_history,
                        threshold=st.session_state.threshold
                    )
                except Exception as e:
                    error_msg = str(e)
                    if "rate_limit_exceeded" in error_msg or "429" in error_msg:
                        st.error("⏳ API rate limit reached. Please wait a few minutes and try again.")
                    else:
                        st.error(f"An error occurred: {error_msg}")
                    st.stop()

                # Validate and build final response
                final_result = build_final_response(
                    answer=raw_result["answer"],
                    chunks=raw_result["chunks"],
                    is_answerable=raw_result["is_answerable"],
                    threshold=st.session_state.threshold
                )

                # Display answer
                st.markdown(final_result["answer"])

                # Show confidence ONLY if answerable
                if final_result["is_answerable"]:
                    confidence = final_result["confidence"]["label"]
                    if confidence == "high":
                        st.success("Confidence: HIGH")
                    elif confidence == "medium":
                        st.warning("Confidence: MEDIUM")
                    elif confidence == "low":
                        st.error("Confidence: LOW")
                else:
                    confidence = "none"
                    st.info("No sufficient PDF evidence found.")

                # Get total chunks in DB for debug
                try:
                    client = get_chroma_client()
                    collection = get_or_create_collection(client)
                    total_in_db = collection.count()
                except Exception:
                    total_in_db = 0

                # Debug info panel
                with st.expander("🧠 Debug Info"):
                    st.write("Query:", query)
                    st.write("Threshold:", st.session_state.threshold)
                    st.write("Total chunks in DB:", total_in_db)
                    if final_result["chunks"]:
                        st.write("Dynamic K used:", final_result["chunks"][0].get("k_used", "N/A"))
                        st.write("Total chunks scanned:", final_result["chunks"][0].get("total_chunks", "N/A"))
                    else:
                        st.write("Dynamic K used:", raw_result.get("actual_k", 0))
                    st.write("Retrieved chunks:", len(final_result["chunks"]))
                    st.write("Is answerable:", final_result["is_answerable"])
                    st.write("Citation valid:", final_result["validation"]["is_valid"])
                    st.write("Pages cited:", final_result["validation"]["cited_pages"])
                    st.write("Top similarity:", final_result["confidence"]["score"])

                # Evidence panel — only if answerable
                if final_result["is_answerable"] and final_result["chunks"]:
                    with st.expander("📑 View Retrieved Evidence"):
                        for i, chunk in enumerate(final_result["chunks"]):
                            st.markdown(
                                f"**Chunk {i+1}** | "
                                f"Page {chunk['page']} | "
                                f"Similarity: {chunk['similarity']:.3f}"
                            )
                            st.text(chunk["text"][:300] + "...")
                            st.markdown("---")

        # Update chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": query
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": final_result["answer"]
        })

        # Save message with metadata
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_result["answer"],
            "metadata": {
                "confidence": confidence,
                "chunks": final_result["chunks"] if final_result["is_answerable"] else []
            }
        })