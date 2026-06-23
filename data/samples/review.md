## contract_01 — Licensing (Verify Smart Corp / Assured Mobile)

- agreement_type: "licensing" — ✅ correct (matches manual classification)
- effective_date: "2012-08-05" — ✅ correct, ISO format
- parties: 2 parties with Licensor/Licensee roles — ✅ correct
- term_length: "20 years" — ✅ concise and correct
- governing_law: "State of Nevada" — ✅ correct, concise
- payment_terms: 🟡 TOO VERBOSE
  - Prompt said "1-2 sentence summary" → got 2 sentences but ~70 words
  - Contains specific dollar amounts ($100, $10,000, $40,000, $249,900, 8.5M shares)
  - Prompt rule "Do not copy the entire payment section" partially violated
  - Should be: "Initial license fees paid in installments over 12 months, plus 2.5% quarterly royalty on gross sales."
- termination_clauses: ⚠️ INCOMPLETE — likely missing clauses
  - Only 2 clauses extracted
  - Most contracts have 3-5 termination conditions (material breach, insolvency, mutual agreement, notice period, etc.)
  - Need to check the source contract — are those really the only 2 termination clauses, or did Claude miss some?

Overall: 5/7 perfect, 1 borderline (payment_terms), 1 possibly incomplete (termination_clauses).

## contract_02 — Multi-party Services Agreement (Fund services)

- agreement_type: "services" — ✅ correct
- effective_date: "2018-03-01" — ✅ correct, ISO format
- parties: 5 parties extracted with correct service-provider/recipient roles — ✅ correct (multi-party arrangement, all legitimate entities)
- term_length: "<UNKNOWN>" — ⚠️ FAILURE MODE: sentinel string instead of null
  - Either the contract doesn't specify (should be null) or Claude missed it (also wrong)
  - Either way: prompt must forbid sentinel strings
- governing_law: "State of New York" — ✅ correct
- payment_terms: 2 sentences capturing fee structure (quarterly, % of NAV, 5-50 bps) — ✅ better than contract_01's verbose version
- termination_clauses: 5 distinct clauses, clean summaries — ✅ correct

Overall: 6/7 perfect. 1 specific failure: sentinel string for missing field.


## contract_03 — Employment (Synergy Resources Corp / [Employee])

- agreement_type: "employment" — ✅ correct
- effective_date: "2013-06-01" — ✅ correct, ISO format
- parties: ⚠️ FAILURE MODE: sentinel string for unknown employee name
  - Employer correctly extracted: "Synergy Resources Corporation"
  - Employee returned as `{name: "<UNKNOWN>", role: "Employee"}` 
  - Likely the source has a placeholder; Claude couldn't return null (required field), so invented sentinel
  - Schema fix needed OR prompt instruction to omit unnamed parties
- term_length: "3 years" — ✅ correct (note: contract_02 also showed term_length issue, here it's clean)
- governing_law: "State of Colorado" — ✅ correct
- payment_terms: 1 sentence, ~50 words — 🟡 borderline; captures structure (salary + bonus + benefits) but specific dollar amounts ($420K, $300K) preserved
- termination_clauses: 5 distinct, detailed clauses — ✅ excellent extraction; each clause is substantive but concise

Overall: 5/7 clean, 1 failure mode confirmed (sentinel string), 1 borderline (payment_terms verbosity)



## contract_04 — Hybrid Distribution Agreement (Progressive Int'l / Ingen Technologies)

- agreement_type: "licensing" — ⚠️ DEBATABLE
  - Reveals schema limitation: this is really a Distribution Agreement (exclusive distributor + minimum purchase obligations)
  - Claude picked "licensing" because one party is called "Licensor" (lexical signal)
  - Arguably should be "other" given the hybrid nature
- effective_date: "2008-02-01" — ✅ correct
- parties: 2 parties, distinct roles — ✅ correct
- term_length: "5 years" — ✅ correct
- governing_law: "State of California" — ✅ correct
- payment_terms: minimum 10K units/month, tiered pricing — ✅ good summary
- termination_clauses: 2 brief clauses — ✅ accurate (verified against source; the contract genuinely has only brief termination language)

Overall: 6/7 clean. 1 case of schema limitation (hybrid agreement type).


## contract_05 — Purchase Agreement (Vanguard Energy / Vast Exploration)

- agreement_type: "purchase" — ✅ correct
- effective_date: "2014-04-01" — ✅ correct, ISO format
- parties: Seller (Vanguard Energy) + Purchaser (Vast Exploration), both correctly extracted — ✅ correct
- term_length: "Not specified" — ⚠️ THIRD SENTINEL STRING INSTANCE (placeholder instead of null)
- governing_law: "State of Texas" — ✅ correct, proper title case
- payment_terms: 1 sentence, captures earnest money + total + payment method — ✅ EXCELLENT (best in the dataset)
- termination_clauses: 7 distinct, concise clauses — ✅ EXCELLENT (best in the dataset)

Overall: 6/7 perfect. 1 confirmed failure: sentinel string for missing term length.



## contract_06 — Commercial Lease (Redacted Landlord / Competitive Technologies)

- agreement_type: "lease" — ✅ correct
- effective_date: "2010-11-22" — ✅ correct, ISO format
- parties: 2 parties (Landlord with redacted name + Tenant Competitive Technologies) — ✅ correct
  - Note: source has c/o Abbey Road Advisors LLC as administrative agent; Claude correctly did NOT include this as a third party
  - Note: redacted name preserved as Unicode blocks, not invented as a sentinel string
- term_length: "36 months" — ✅ correct
- governing_law: "State of Connecticut" — ✅ correct
- payment_terms: 2 sentences with base rent range + additional rent components — ✅ excellent
- termination_clauses: 12 distinct clauses, all materially different — ✅ excellent

Overall: 7/7 fields correct. Best extraction in the dataset.