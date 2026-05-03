# Test Cases — PDF Conversational Agent

## Sample PDF Used
**File:** pitch.pdf (Scaler School of Technology — Judge Recruitment Pitch)
**Pages:** 7
**Chunks indexed:** 8

## Additional Large PDF Test
**File:** the-economic-potential-of-generative-ai-the-next-productivity-frontier.pdf
**Pages:** 68
**Chunks indexed:** 216

Purpose: Validate scalability, dynamic K retrieval, numeric extraction, and large-document grounding.

## Setup Instructions
1. Run: `streamlit run app.py`
2. Upload `pitch.pdf` from sidebar
3. Set threshold to 0.60 (Balanced)
4. Run queries below in order

---

## Valid Queries — Must Answer With Citations

| # | Query | Expected Behavior |
|---|---|---|
| 1 | What is Scaler School of Technology? | Answer with description + [Page 1] citation |
| 2 | What are the student achievements? | List achievements + [Page 1] citation |
| 3 | What are the requirements for judges? | List requirements + [Page 3] citation |
| 4 | What benefits do judges get? | List benefits + [Page 3] citation |
| 5 | On which dates is the event happening? | Mentions 16th and 17th May + page citation |

---

## Invalid Queries — Must Refuse

| # | Query | Expected Behavior |
|---|---|---|
| 1 | Who is the CEO of Google? | "I could not find this information in the uploaded PDF." |
| 2 | What is the capital of France? | "I could not find this information in the uploaded PDF." |
| 3 | Explain quantum computing. | "I could not find this information in the uploaded PDF." |

---

## Follow-up Queries — Must Use Chat History

Ask these in sequence:
1. "What are the requirements for judges?"
2. "Tell me more about the first requirement."

Expected: Second answer should expand on first requirement using context from previous answer.

If follow-up context is unclear, system should refuse instead of guessing.

---

## Edge Case Queries

| # | Query | Expected Behavior |
|---|---|---|
| 1 | What is NOT discussed in this document? | Should not hallucinate — either partial grounded answer or refusal |
| 2 | Does the document mention climate change? | Should refuse if not present in PDF |
| 3 | Explain the second point. | Should use conversation context or refuse if unclear |

---

## Large PDF Test Queries

| # | Query | Expected Behavior |
|---|---|---|
| 1 | How much annual value could generative AI add to the global economy? | ~$2.6T–$4.4T annually with correct page citation |
| 2 | Which four areas account for most of the generative AI use case value? | Customer operations, marketing and sales, software engineering, R&D + citation |
| 3 | Who is the CEO of Google? | Refusal |

---

## Expected Refusal Behavior

When query is out of scope:
- Answer: "I could not find this information in the uploaded PDF."
- Confidence badge: NOT shown
- Evidence panel: NOT shown
- Confidence label should be "none" for refused queries
- Debug shows: `Is answerable: False`

---

## Threshold Testing

| Setting | Expected Behavior |
|---|---|
| Balanced (0.60) | Most valid queries answered |
| Strict (0.70) | Only high-confidence queries answered |

---

## Evaluator Notes

- Dynamic K automatically adjusts based on PDF size
- Small PDFs (≤ 40 chunks) use K=5
- Medium PDFs (41–150 chunks) use K=8
- Medium-large PDFs (151–450 chunks) use K=15
- Very large PDFs (> 450 chunks) use K=20
- Threshold adjustable via sidebar slider — no code change needed
- Debug panel shows full observability for every query

---

## Performance Notes

- Large PDF (216 chunks) processed successfully without latency issues
- Retrieval scales via dynamic K without manual tuning