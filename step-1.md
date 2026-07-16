# Week 2 Retrospective

**Project:** clausewise — commercial contract intelligence pipeline
**Duration:** 7 days
**Status at end of week:** Extraction pipeline working, hardened for production, 6 ground-truth labels ready for Week 3 eval harness

---

## What I built

- Working extraction pipeline in `pipeline/extract.py` using Anthropic tool use
- Pydantic schema (`pipeline/schemas.py`) with strict validation (`extra="forbid"`) covering 7 contract fields
- Two versions of the extraction prompt (`extraction_v1.txt`, `extraction_v2.txt`) with documented iteration between them
- Alternative implementation using JSON mode instead of tool use (`extract_json_mode.py`) for direct comparison
- Production-grade hardening: retry logic with exponential backoff, input validation, structured JSONL logging, human-review routing for uncertain extractions, deliberate failure testing
- 6 hand-labeled ground-truth files in `data/expected_outputs/`
- Comprehensive `LABELING_GUIDE.md` documenting labeling rules and per-contract edge cases
- Validation script (`validate_labels.py`) confirming all 6 labels conform to schema
- Analysis documents: `day3_review.md` (v1 vs v2), `day4_comparison.md` (tool use vs JSON mode)

---

## What worked well

- **Tool calling as a mechanism.** Discovering that tool use enforces schema at the API level (constraint), while JSON mode only requests format in the prompt (request), completely reframed how I think about structured LLM output.
- **Evidence-driven prompt iteration.** Observing specific failures in v1, categorizing them into patterns, and writing targeted rules for v2 — instead of guessing at what might work — felt like real engineering rather than vibes.
- **Pydantic schema + explicit rules.** Combining a strict schema with prompt-level rules produced consistent, structured output that both the model and downstream code could rely on.
- **Deliberate failure testing.** Watching my pipeline handle 6 consecutive 404 errors gracefully, log each one, and continue to the next contract — this is what production reliability actually feels like.
- **Multi-model comparison groundwork.** Building tool use vs JSON mode side-by-side gave me evidence-based confidence in the pipeline's design choices, not just theoretical arguments.

---

## What was harder than expected

- **Prompt regression on contract_05.** v2 fixed sentinel strings for contract_02 and contract_03, but introduced a new failure on contract_05 — the "no dollar amounts" rule that worked for fund services made purchase agreements worse, where the dollar amount IS the deal structure. This was my first real experience with a prompt change fixing one thing and breaking another.
- **Debugging the retry loop on Day 5.** Multiple iterations to get the retry logic right — missing imports (`APIStatusError`, `RateLimitError`), `UnboundLocalError` on `result` when all retries failed, flat backoff instead of exponential. Each bug was small; together they took real time to work through.
- **Manual labeling was exhausting and involved anchoring bias.** Day 6 was the hardest day of the week. I kept using the model's output as my ground truth instead of writing labels independently. The mentor had to push back multiple times before I understood: ground truth is what I want the model to produce, not what the model currently produces.
- **Distinguishing "structure" from "amounts" for payment_terms across contract types.** One rule didn't fit all contracts. Purchase agreements need dollar amounts; services agreements don't; employment agreements have salary (ongoing → omit) plus bonus (structural → include mechanism). Making the rules consistent across 6 contract types required real judgment.

---

## Biggest concepts I now understand

- **Constraint vs request.** Tool use enforces structure at the API level (~100% enforcement). JSON mode requests structure in the prompt (~50-70% honored). For complex outputs, constraints beat requests every time. This principle generalizes far beyond LLMs — it shows up in type systems, database schemas, API validation.
- **Why prompts matter more than I thought.** Before this project, I thought of prompting as "give input, get answer." Now I understand it as engineering the model's behavior — including rules for missing data (nulls, not sentinels), format enforcement (ISO dates), and edge cases (hybrid contracts). Prompt engineering is one dial in a larger system, but the dial matters.
- **Input validation for cost engineering.** Before this project, I would have sent whatever came in to the LLM. Now I validate first — empty text, too-short text, too-long text — because tokens cost money and failed extractions on garbage input teach me nothing.
- **Pydantic schemas as the contract between LLM and downstream code.** The schema is the spec. When the model returns something that doesn't conform, Pydantic raises before my code touches bad data. The strict `extra="forbid"` config was the difference between "accepted invented fields silently" and "rejected them loudly."
- **The prompt regression phenomenon.** Iterating a prompt to fix one failure can create new failures elsewhere. Without an eval harness, you catch these by manual review only. This is exactly why Week 3 exists.
- **Ground truth is what YOU decide, not what the model produces.** The circular trap of using model output as labels means you measure the model against itself and learn nothing. Independent labeling is hard but necessary.
- **Sentinel strings are a specific, generalizable failure mode.** `"<UNKNOWN>"`, `"Not specified"`, `"N/A"` — models invent placeholder strings across many fields when null would be correct. Forbidding them explicitly in the prompt is table stakes for reliable extraction.

---

## What I'd do differently

1. **Front-load engineering conventions into v1, discover behavior-specific rules empirically.** Some prompt rules are baseline engineering conventions — use JSON null instead of sentinel strings, ISO date format YYYY-MM-DD, proper title case for jurisdictions. These I could have reasoned to before running anything and put them in v1 from the start. Other rules — like handling hybrid contracts as "other" — could only be discovered after seeing the model force-fit contract_04 into "licensing." Those inherently require iteration. Separating these two categories would have reduced my v1 → v2 rework on the avoidable part while preserving the necessary iteration on the empirical part.

2. **Write the labeling guide BEFORE labeling any contract.** I started labeling contract_01 and added rules to the guide inline as edge cases came up. My early labels were inconsistent because rules weren't documented yet. Better to spend 20-30 minutes upfront thinking through the rules for each field, then apply them as a stable rulebook. Add rules for edge cases that arise, but start with a real baseline.

3. **Never open the model's output before writing my own label.** Day 6 taught me anchoring bias is real and powerful. Once I saw what the model produced, my "independent" judgment became lightly-edited-model-output. In Week 3 Day 2 (labeling 44 more contracts), I'll write my labels from source + guide only, then compare to the model afterward.

---

## Prerequisites I need for Week 3

- Together AI account (free credits) — for Llama 3.1 8B multi-model comparison on Day 6
- OpenAI billing setup ($5 minimum) — for GPT-4o-mini multi-model comparison on Day 6
- Both API keys added to `.env`
- Reading list ready for Day 1: Hamel Husain's "Your AI Product Needs Evals" and "Creating an LLM-as-a-Judge," Eugene Yan's "Patterns for Building LLM-Based Systems"

---

## Version history

- v1.0 — End of Week 2, before Week 3 begins