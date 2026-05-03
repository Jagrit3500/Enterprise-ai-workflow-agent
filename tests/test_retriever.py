import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retriever import (
    get_dynamic_k,
    retrieve_chunks,
    filter_by_threshold,
    retrieve_and_filter,
    format_context
)


def test_dynamic_k_small():
    assert get_dynamic_k(10) == 5


def test_dynamic_k_medium():
    assert get_dynamic_k(100) == 8


def test_dynamic_k_large():
    assert get_dynamic_k(300) == 15


def test_dynamic_k_very_large():
    assert get_dynamic_k(500) == 20


def test_filter_by_threshold_removes_low():
    chunks = [
        {"similarity": 0.80, "page": 1, "text": "a"},
        {"similarity": 0.50, "page": 2, "text": "b"},
        {"similarity": 0.65, "page": 3, "text": "c"},
    ]
    filtered = filter_by_threshold(chunks, threshold=0.60)
    assert len(filtered) == 2
    assert all(c["similarity"] >= 0.60 for c in filtered)


def test_filter_by_threshold_empty():
    result = filter_by_threshold([], threshold=0.60)
    assert result == []


def test_filter_by_threshold_all_pass():
    chunks = [
        {"similarity": 0.80, "page": 1, "text": "a"},
        {"similarity": 0.90, "page": 2, "text": "b"},
    ]
    filtered = filter_by_threshold(chunks, threshold=0.60)
    assert len(filtered) == 2


def test_filter_by_threshold_none_pass():
    chunks = [
        {"similarity": 0.30, "page": 1, "text": "a"},
        {"similarity": 0.40, "page": 2, "text": "b"},
    ]
    filtered = filter_by_threshold(chunks, threshold=0.60)
    assert len(filtered) == 0


def test_format_context_empty():
    result = format_context([])
    assert result == ""


def test_format_context_includes_page():
    chunks = [{"page": 3, "text": "Sample text here"}]
    result = format_context(chunks)
    assert "[Page 3]" in result
    assert "Sample text here" in result


def test_retrieve_and_filter_returns_tuple():
    result = retrieve_and_filter("test query")
    assert isinstance(result, tuple)
    assert len(result) == 3


if __name__ == "__main__":
    tests = [
        test_dynamic_k_small,
        test_dynamic_k_medium,
        test_dynamic_k_large,
        test_dynamic_k_very_large,
        test_filter_by_threshold_removes_low,
        test_filter_by_threshold_empty,
        test_filter_by_threshold_all_pass,
        test_filter_by_threshold_none_pass,
        test_format_context_empty,
        test_format_context_includes_page,
        test_retrieve_and_filter_returns_tuple,
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