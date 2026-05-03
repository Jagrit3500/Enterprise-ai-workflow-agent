import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.citation_validator import (
    extract_cited_pages,
    validate_citations,
    get_confidence_label,
    build_final_response
)


def test_extract_cited_pages_single():
    answer = "This is from [Page 3]."
    assert extract_cited_pages(answer) == [3]


def test_extract_cited_pages_multiple():
    answer = "From [Page 1] and [Page 5]."
    pages = extract_cited_pages(answer)
    assert set(pages) == {1, 5}


def test_extract_cited_pages_none():
    answer = "No citations here."
    assert extract_cited_pages(answer) == []


def test_validate_citations_valid():
    answer = "Answer from [Page 1]."
    chunks = [{"page": 1, "similarity": 0.80, "text": "text"}]
    result = validate_citations(answer, chunks)
    assert result["is_valid"] is True
    assert result["is_refusal"] is False


def test_validate_citations_refusal():
    answer = "I could not find this information in the uploaded PDF."
    result = validate_citations(answer, [])
    assert result["is_refusal"] is True
    assert result["is_valid"] is True


def test_validate_citations_missing():
    answer = "Answer with no citation."
    chunks = [{"page": 1, "similarity": 0.80, "text": "text"}]
    result = validate_citations(answer, chunks)
    assert result["is_valid"] is False
    assert result["missing_citations"] is True


def test_validate_citations_invalid_page():
    answer = "Answer from [Page 99]."
    chunks = [{"page": 1, "similarity": 0.80, "text": "text"}]
    result = validate_citations(answer, chunks)
    assert result["is_valid"] is False
    assert 99 in result["invalid_pages"]


def test_confidence_high():
    chunks = [{"similarity": 0.85, "page": 1, "text": "text"}]
    result = get_confidence_label(chunks)
    assert result["label"] == "high"


def test_confidence_medium():
    chunks = [{"similarity": 0.70, "page": 1, "text": "text"}]
    result = get_confidence_label(chunks, threshold=0.60)
    assert result["label"] == "medium"


def test_confidence_empty():
    result = get_confidence_label([])
    assert result["label"] == "none"
    assert result["score"] == 0.0


def test_build_final_response_valid():
    answer = "Answer from [Page 1]."
    chunks = [{"page": 1, "similarity": 0.80, "text": "text"}]
    result = build_final_response(answer, chunks, True)
    assert result["is_answerable"] is True
    assert result["answer"] == answer


def test_build_final_response_refusal():
    answer = "I could not find this information in the uploaded PDF."
    result = build_final_response(answer, [], False)
    assert result["is_answerable"] is False


def test_build_final_response_invalid_citation():
    answer = "Answer with no citation."
    chunks = [{"page": 1, "similarity": 0.80, "text": "text"}]
    result = build_final_response(answer, chunks, True)
    assert result["is_answerable"] is False


if __name__ == "__main__":
    tests = [
        test_extract_cited_pages_single,
        test_extract_cited_pages_multiple,
        test_extract_cited_pages_none,
        test_validate_citations_valid,
        test_validate_citations_refusal,
        test_validate_citations_missing,
        test_validate_citations_invalid_page,
        test_confidence_high,
        test_confidence_medium,
        test_confidence_empty,
        test_build_final_response_valid,
        test_build_final_response_refusal,
        test_build_final_response_invalid_citation,
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