# LABELING_GUIDE.md — clausewise ground truth rules

This guide defines the rules for labeling contract expected outputs used as ground truth in Week 3's evaluation harness. The purpose is CONSISTENCY across the labeled test set — same rule, same situation, every time.

Version: 1.0 (locked at end of Week 2 Day 6)

---

## Universal rules

### The null rule (critical)
JSON `null` represents a missing value. Never use sentinel strings for absent data.

- Correct: `"term_length": null`
- FORBIDDEN: `"Unknown"`, `"N/A"`, `"Not specified"`, `"Not mentioned in the contract"`, `"Not applicable"`, `"<UNKNOWN>"`, `"TBD"`, `""` (empty string) as a stand-in for absence

If you catch yourself writing a phrase describing the absence of a value, use `null` instead.

---

## agreement_type

Enum: `licensing, services, employment, nda, lease, purchase, other`

Rules:
- Use the closest fit from the enum
- Infer from body language if title is generic (e.g., Licensor/Licensee → licensing)
- For genuinely hybrid contracts (multiple substantial types): use `"other"`
- For software licenses with purchase price elements: `"licensing"` (dominant type wins)
- Distribution / supply / franchise agreements: not in enum → use `"other"`

---

## effective_date

Rules:
- ISO format `YYYY-MM-DD`
- Use the "as of" date in the opening paragraph (the "date first written above")
- Do NOT use signature dates or commencement dates (rent-start, employment-start, etc.)
- Even if the contract's own definition of "Effective Date" points to signature dates, use the header date — signature dates are often unreliable in extracted text
- If no date is specified anywhere → `null`

---

## parties

Rules:
- Full legal name as written in the contract (preserve "Inc.", "LLC", "Corp", etc.)
- Do not modify capitalization (preserve "VERIFY SMART CORP" as written)
- If a party's name is missing/redacted with block characters (▇▇▇) → preserve those characters exactly
- If a party is referenced but not named at all (e.g., "the Employee" with no name given) → omit the party entry (do NOT use `null`, do NOT invent a placeholder)
- Include only ACTUAL parties, not administrative agents (e.g., exclude "c/o Abbey Road Advisors")

### Role selection (priority order)

1. **Specific functional role from whereas clauses** — if the contract explicitly identifies the entity's function (e.g., "HFMC acts as investment adviser"), use that specific role
   Example: `"Investment Adviser"`, `"Principal Underwriter"`, `"Transfer Agent"`

2. **Collective role from party definitions** — if no specific functional role is given, use the collective role defined in parentheses in the opening paragraph
   Example: `"Company"`, `"Hartford Party"`, `"Licensor"`, `"Employer"`, `"Contractor"`

3. **Generic role inferred from context** — only if neither of the above exists
   Example: `"Party A"`, `"Signatory"` (rare)

Consequences:
- The same contract may mix specific and collective roles (e.g., contract_02 has "Company" for insurance entities and "Principal Underwriter"/"Investment Adviser"/"Transfer Agent" for Hartford entities). This is expected — don't force artificial consistency.
- Role strings preserve the contract's title case as written.
- If multiple entities share a collective role, assign the same role string to each.

---

## term_length

Rules:
- Short phrase capturing the duration
- Examples: `"20 years"`, `"3 years"`, `"36 months"`, `"perpetual"`, `"indefinite"`
- If genuinely unspecified in the contract → `null`

---

## governing_law

Rules:
- Format as `"State of X"` with title case
- Do NOT append "and federal laws of the United States" unless the contract explicitly emphasizes federal jurisdiction
- If genuinely absent → `null`

---

## payment_terms

Rules:
- 1-2 sentence summary of the payment STRUCTURE
- Structure, not specific amounts (with exceptions below)

### Include specific amounts
- Single one-time payments (e.g., "$5.5M purchase price")
- Single equity payments (e.g., "8,500,000 common shares")
- Defining rates for percentages/royalties (e.g., "2.5% quarterly royalty")
- Structural minimums that define the deal (e.g., "10,000 units per month minimum" for a distribution agreement)

### OMIT specific amounts
- Ongoing/recurring payments (salary, ongoing fees, monthly rent)
- Multi-amount schedules with 3+ specific figures (milestones, installments)
- Specific rate schedules across many products/classes
- Adjustment mechanics (describe as "subject to standard adjustments")

### For employment contracts
- Cover salary structure + bonus mechanism
- Include bonus TRIGGER (e.g., "well-production milestones", "revenue targets") 
- Include cap EXISTENCE (yes/no) but not specific cap amount
- OMIT benefits (health, 401(k), PTO) — these are conditions of employment, not payment structure
- OMIT reimbursements
- OMIT severance amounts — belongs to termination_clauses if relevant

### For multi-tier fee structures (like contract_02)
- Include fee TYPE NAMES if structurally significant (e.g., "service fees, administrative fees, sub-transfer-agent fees")
- Include who pays each type IF this varies (structural information)
- OMIT specific bps rates and rate schedules

---

## termination_clauses

Rules:
- Each distinct triggering condition as one list item
- SHORT trigger phrase per item (2-8 words typical)
- Capture the trigger, not the full legal detail

### Do NOT include
- Cure periods (e.g., "30 days to cure") unless the cure period is the defining structural element
- Notice periods (e.g., "with 30 days written notice") — same exception applies
- Consequences (e.g., "and receives lump sum payment")
- Section references (e.g., "in Section 7(b)")
- Full legal precision (that lives in the contract itself)

### Splitting combined sub-clauses
When a single sub-section groups multiple distinct triggers under one notice period:
- SPLIT into separate items (one per distinct trigger)
- Each item mentions the shared notice period if it's a defining feature

Example (contract_02 Section 7(b)):
- Sub-section: "Any party may terminate on 30 days notice: (1) if required by law; or (2) for material breach"
- Correct: TWO items — "termination if required by law" and "termination for material breach"
- Wrong: ONE item combining both triggers

### When contract expiration counts as a termination clause
- Yes — an automatic termination at end of term is a valid termination clause
- Example: "Automatic expiration at end of 5-year term"

---

## Schema limitations acknowledged

The 7-field Contract schema does NOT capture:
- Territorial rights (e.g., contract_04's exclusive distribution in China/Japan/Korea/India)
- Product specifics beyond names
- Exclusivity terms
- Confidentiality obligations
- Warranties and indemnification
- Cure periods and notice periods (except when captured summarily)

For labeling: acknowledge these exist but don't force them into other fields. If they're structurally important, they might warrant a future schema extension.

---

## Edge cases documented while labeling

### contract_01 (Verify Smart licensing agreement)
- Multi-tranche payment: describe milestone structure without listing each amount
- 8,500,000 common shares → include the number (single defining equity amount)
- 2.5% royalty → include the rate (single defining percentage)

### contract_02 (Hartford Funds services agreement)
- 5 parties with mixed role treatment:
  - AULife + Securities → both `"Company"` (collective, no specific whereas)
  - HFD → `"Principal Underwriter"` (from whereas clause)
  - HFMC → `"Investment Adviser"` (from whereas clause)
  - HASCO → `"Transfer Agent"` (from whereas clause)
- Multi-tier bps schedule across 45+ funds → describe fee TYPES, not rates
- Section 7(b) sub-clauses split into 2 items ("required by law" and "material breach")
- term_length: null (indefinite services agreement)

### contract_03 (Synergy Resources employment agreement)
- Employee not named in source → omit Employee party (do not use null)
- Bonus with well-production milestones + annual cap → structural language, no dollar amounts
- 8 distinct termination triggers, each summarized in 2-8 words

### contract_04 (Progressive/Ingen distribution agreement)
- Distribution agreements not in enum → `"other"`
- Contract's own roles preserved (Contractor, Company)
- Minimum purchase quantity IS structural (include "10,000 units per month")
- Contract expiration counts as a termination clause

### contract_05 (Vanguard Energy purchase agreement)
- One-time purchase → include both defining amounts ($150K earnest, $5.5M closing)
- term_length: null (no ongoing term for one-time purchase)
- 7 distinct termination triggers, each as short trigger phrase without consequences

### contract_06 (Anonymized landlord lease)
- Landlord name redacted with ▇▇▇ characters → preserve exactly
- Administrative agent "c/o Abbey Road Advisors" excluded (agent, not party)
- Ongoing rent → structural description, no per-sq-ft rates
- 13 distinct termination triggers (one more than the model's 12 — found eminent domain of other building portions)

---

## Version history

- **v1.0 (Week 2 Day 6)** — Initial version. 6 labeled contracts. Rules established through case-by-case decisions during first labeling session.

Future updates: as more contracts are labeled in Week 3 Day 2, new edge cases will surface. Add rules to this guide as they arise. Do NOT retroactively re-label older contracts unless a rule fundamentally changes.