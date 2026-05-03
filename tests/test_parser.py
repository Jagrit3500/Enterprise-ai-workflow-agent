import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.pdf_parser import parse_pdf, create_chunks
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

TEST_PDF_PATH = "uploads/pitch.pdf"


def test_parse_pdf_returns_list():
    chunks = parse_pdf(TEST_PDF_PATH)
    assert isinstance(chunks, list)


def test_parse_pdf_not_empty():
    chunks = parse_pdf(TEST_PDF_PATH)
    assert len(chunks) > 0


def test_parse_pdf_chunk_has_required_keys():
    chunks = parse_pdf(TEST_PDF_PATH)
    required_keys = [
        "chunk_id", "text", "page",
        "page_start", "page_end",
        "source", "char_start", "char_end"
    ]
    for chunk in chunks:
        for key in required_keys:
            assert key in chunk, f"Missing key: {key}"


def test_parse_pdf_page_numbers_positive():
    chunks = parse_pdf(TEST_PDF_PATH)
    for chunk in chunks:
        assert chunk["page"] >= 1
        assert chunk["page_start"] >= 1
        assert chunk["page_end"] >= 1


def test_parse_pdf_chunk_text_not_empty():
    chunks = parse_pdf(TEST_PDF_PATH)
    for chunk in chunks:
        assert chunk["text"].strip() != ""


def test_parse_pdf_source_is_filename():
    chunks = parse_pdf(TEST_PDF_PATH)
    for chunk in chunks:
        assert "/" not in chunk["source"]
        assert "\\" not in chunk["source"]
        assert chunk["source"].endswith(".pdf")


def test_parse_pdf_chunk_ids_unique():
    chunks = parse_pdf(TEST_PDF_PATH)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))


def test_parse_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_pdf("uploads/nonexistent.pdf")


def test_create_chunks_respects_chunk_size():
    sample_text = "A" * 5000
    chunks = create_chunks(
        text=sample_text,
        page_num=1,
        source="test.pdf",
        chunk_id_start=0
    )
    for chunk in chunks:
        assert len(chunk["text"]) <= CHUNK_SIZE


def test_create_chunks_returns_list():
    chunks = create_chunks("Sample text", 1, "test.pdf", 0)
    assert isinstance(chunks, list)


def test_create_chunks_empty_text():
    chunks = create_chunks("", 1, "test.pdf", 0)
    assert chunks == []


if __name__ == "__main__":
    tests = [
        test_parse_pdf_returns_list,
        test_parse_pdf_not_empty,
        test_parse_pdf_chunk_has_required_keys,
        test_parse_pdf_page_numbers_positive,
        test_parse_pdf_chunk_text_not_empty,
        test_parse_pdf_source_is_filename,
        test_parse_pdf_chunk_ids_unique,
        test_create_chunks_returns_list,
        test_create_chunks_empty_text,
    ]

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
        except Exception as e:
            print(f"⚠️ {test.__name__}: {e}")

    print("\nDone!")