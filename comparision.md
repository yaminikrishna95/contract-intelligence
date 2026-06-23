# Day 4 — Tool use vs JSON mode comparison

## Setup
Same Pydantic schema (`Contract` with 7 fields, strict `extra="forbid"`).
Same model: claude-haiku-4-5.
Same temperature: 0.0.
Same dataset: 6 commercial contracts.

Only the extraction mechanism differs:
- **Tool use** (`extract.py`): schema sent to API as `tool.input_schema`, enforced server-side
- **JSON mode** (`extract_json_mode.py`): schema sent in prompt text, model asked to comply

## Headline result

| Metric | Tool use | JSON mode |
|---|---|---|
| Successful extractions | 6/6 (100%) | [FILL: N]/6 |
| Wrong enum values | 0 | 2 (contracts 2, 4) |
| Invented extra fields | 0 | 2 (contracts 3, 4) |
| Quality drift (verbose output) | 0 | 1 (contract 1) |

## Specific JSON mode failures

### contract_2 — Enum drift
- agreement_type returned: `"service_agreement"`
- Schema enum: must be one of `"licensing"`, `"services"`, `"employment"`, `"nda"`, `"lease"`, `"purchase"`, `"other"`
- Tool use produced: `"services"` ✓

### contract_3 — Invented fields
- Added: `"key_obligations"`, `"special_provisions"`
- Schema has 7 defined fields with `extra="forbid"`
- Tool use produced: only the 7 schema fields ✓

### contract_4 — Both failure modes
- Wrong enum: `"distribution"` (not in allowed list)
- Invented 5 extra fields: `territories`, `products`, `dispute_resolution`, `key_obligations`, `confidentiality`
- Tool use produced: `"licensing"` (debatable but schema-valid) + only schema fields ✓

### contract_1 — Validation passed but quality drifted
- `governing_law`:
  - Tool use: `"State of Nevada"` (clean)
  - JSON mode: `"State of Nevada and federal laws of the United States"` (verbose)
- `payment_terms`:
  - Tool use: ~50 words, captured structure
  - JSON mode: ~80 words, listed all specific dollar amounts and interest details
- Insight: Tool use doesn't just enforce schemas — it enforces prompt rules better too

## Why tool use is more reliable

Tool use sends the schema as `input_schema` to Anthropic's API. The API enforces it server-side BEFORE returning the response to my code:
- Allowed enum values
- Required field presence
- `additionalProperties: false` (from `extra="forbid"`)
- Type correctness

JSON mode sends the schema as text in the prompt. The model treats it as guidance, not enforcement. It can — and did — drift:
- Rename enum values to feel more natural (`"service_agreement"` instead of `"services"`)
- Add fields it thinks should be there
- Override strictness rules
- Even when it succeeds, drift on prompt-level rules

## The engineering principle

**Tool use is constraint. JSON mode is request.**

A request is honored about 50% of the time. A constraint is enforced ~100% of the time at the API level. When the output schema is complex — nested objects, enums, strict shape requirements — you want constraints, not requests.

The more complex the expected output, the stronger the case for tool use over JSON mode.

This principle generalizes beyond LLMs: type annotations vs comments, `NOT NULL` vs hope, validated APIs vs trust. Engineering discipline = enforce close to the source.

## When to use each

**Use tool use when:**
- Output schema has enums or strict shape constraints
- You're running at scale and can't afford retry logic
- Reliability matters more than provider portability
- Your provider supports it (Anthropic, OpenAI, etc.)

**JSON mode is acceptable when:**
- Prototyping where occasional drift is fine
- Provider doesn't support tool use
- Schema is simple (no enums, no `extra="forbid"`)
- Manual post-processing of outputs is acceptable

## Conclusion for clausewise

The project uses tool use because:
- 100% success rate on 6/6 contracts vs JSON mode's ~50%
- Cleaner extractions even when JSON mode "succeeds"
- Zero need for retry logic or response parsing
- Production-ready reliability for any future scaling