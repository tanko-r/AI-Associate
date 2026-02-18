# Pitfalls Research

**Domain:** AI Legal Assistant Plugin (Claude Code) — Contract Review & Legal Work Product
**Researched:** 2026-02-17
**Confidence:** HIGH (grounded in observed failure on PSA review + verified research)

---

## Critical Pitfalls

### Pitfall 1: Shallow Pass Mistaken for Complete Review

**What goes wrong:**
The AI produces a review that covers a fraction of the document's provisions — flagging perhaps 10-15 items on a 170-paragraph PSA when a thorough associate would flag 40-60. The output looks like a complete review (organized, professional, correctly formatted) but covers maybe 10-15% of provisions that actually need attention. The partner receives it, assumes it is thorough, and relies on it.

**Why it happens:**
Without explicit per-paragraph disposition requirements, the LLM stops when it has "enough" findings to fill a plausible-looking review. It defaults to the minimum that satisfies a vague instruction like "review this contract and flag issues." High-severity items get flagged. Moderate items get a mention. Low-severity items — including the conforming changes and drafting cleanups that define Big Law quality — get dropped entirely.

The root cause is a missing completion criterion. "Review the contract" has no done condition. "Assign a disposition (Accept/Revise/Delete/Insert/Comment) to every paragraph" does.

**How to avoid:**
- At aggressiveness Level 4-5, require a disposition table: every paragraph gets Accept / Revise / Delete / Insert / Comment. "No disposition" is not allowed.
- Provide Sara's SKILL.md with a hard count floor: "A thorough review of a 150+ paragraph PSA should produce 35+ revision entries, not 10."
- Require Sara to report the coverage ratio before presenting to the partner: "Reviewed 170 paragraphs; 47 revision entries, 83 accepted, 40 commented."
- Include the paragraph-level disposition table (Section A of the reviewer output) as a mandatory step before drafting the redline.

**Warning signs:**
- Junior's review contains fewer than 20 items for a 100+ paragraph agreement
- Review contains no `info`-severity findings (real reviews always surface minor drafting issues)
- No entries in "Missing Provisions" section
- Review matches the structure of Sara's risk map too exactly — the junior is regurgitating the framework instead of reading the document

**Phase to address:**
Quality Overhaul — Sara behavioral framework + document-reviewer agent rework

---

### Pitfall 2: Overconfident But Wrong Legal Analysis

**What goes wrong:**
Sara (or a junior) states a legal position confidently and incorrectly. The output reads with the same fluency and authority whether it is right or wrong. Examples: stating that a provision is "market standard" when it is actually seller-favorable, citing a market norm that is six months stale, or characterizing a risk level inaccurately because the LLM pattern-matched to a superficially similar clause rather than understanding the deal structure.

Stanford HAI research found legal-specific AI tools hallucinate at 17-34% rates even with RAG. General models hallucinate legal holdings 75%+ of the time. The issue is not occasional error — it is systematic overconfidence without self-awareness.

**Why it happens:**
LLMs produce confident-sounding prose regardless of accuracy. There is no native "I might be wrong here" signal. In legal contexts, this is compounded by:
1. Training data reflects the distribution of published legal content, which skews toward standard forms and tends to underrepresent deal-specific negotiation outcomes
2. "Market standard" claims require current deal data that is post-knowledge-cutoff
3. The model cannot distinguish between "I learned this from authoritative sources" and "I pattern-matched to something plausible-sounding"

**How to avoid:**
- Require Sara to distinguish sourced claims from analytical claims. Sourced: "Section 7.3 says X." Analytical: "In my judgment this is below market because Y."
- Flag any "market standard" characterization as requiring the attorney's validation — Sara should note when she is relying on pattern-matching vs. verified current practice
- For specific jurisdiction/deal-type questions, require legal-researcher to search current sources rather than rely on Sara's training knowledge
- Build a reference library of user-provided source materials (practice guides, form agreements, market surveys) — RAG against those sources rather than LLM knowledge alone
- Prohibit Sara from citing specific case names or statutes without verification; she should describe the rule and note that specific authority requires Westlaw/Lexis confirmation

**Warning signs:**
- Review uses phrases like "market standard" or "customarily" without citing a source
- Any specific case citation or statute number in the output (high hallucination risk)
- Analysis that perfectly agrees with the user's initial framing (confirmation bias, not independent analysis)
- Uniform confidence level across all findings — real analysis would flag some items as uncertain

**Phase to address:**
Quality Overhaul — Sara behavioral framework; also RAG Integration when reference library is implemented

---

### Pitfall 3: Vague Delegation Producing Generic Junior Output

**What goes wrong:**
Sara delegates to a junior associate with an instruction like "Review this purchase agreement and identify the key issues from a buyer's perspective." The junior returns a competent generic review — the kind of output you'd get by asking any LLM to review any PSA. It identifies common issues (indemnification, representations, conditions to closing) but misses deal-specific issues, does not use the specific paragraph IDs, does not reference the deal context, and does not apply the analysis framework Sara built in Step 3.

Sara accepts this output without adequate review and it becomes the basis for the redline — which therefore lacks the specificity and deal-sensitivity that Big Law quality requires.

**Why it happens:**
Each subagent starts with no memory of the prior workflow steps. Sara must transfer the entire context — representation, commercial context, aggressiveness level, the target risk list, the defined terms, the paragraph ID map — in the delegation prompt. When the delegation prompt is vague, the junior fills in the blanks with generic patterns.

Research on multi-agent LLM systems confirms: "As the complexity of instructions increases, adherence to specific rules degrades, and error rates compound."

**How to avoid:**
- Mandate that every delegation prompt to document-reviewer includes: (1) representation and aggressiveness, (2) the complete target risk list from Step 3, (3) the paragraph ID map, (4) specific defined terms, (5) explicit output format requirements
- Require Sara to log every delegation in prompt-log.md BEFORE dispatching — the act of writing the prompt out forces specificity
- Add rejection criteria to Sara's SKILL.md: Sara sends junior work back if it contains zero `info`-severity findings, if it lacks section references, or if it fails to apply the target risk categories
- Document-reviewer should receive a filled-out briefing template, not a free-form instruction

**Warning signs:**
- Delegation prompt is under 200 words (a thorough briefing requires more)
- Junior output does not reference any paragraph IDs
- Junior output does not mention any defined terms by name
- Junior output's "Critical Issues" list contains only universal risk categories (indemnification, reps, etc.) with no deal-specific items

**Phase to address:**
Quality Overhaul — delegation model rework; document-reviewer agent instruction upgrade

---

### Pitfall 4: Cross-Reference Blindness on Conforming Changes

**What goes wrong:**
Sara revises Section 7 (indemnification) to add a cap. She does not update Section 12 (which references the indemnification section by name) or Section 4 (which feeds into the indemnification trigger). The redline has internally inconsistent changes — a cap that is not honored downstream, a modified definition that is still used in its original form elsewhere. The partner catches this, or worse, opposing counsel does.

This is the most damaging quality failure because it cannot be detected by reading the modified sections in isolation — it requires a whole-document understanding that single-pass or batched review inherently lacks.

**Why it happens:**
The LLM processes paragraphs in batches and does not natively track semantic dependencies across batches. When the contract-reviser juniors work in parallel, they each see their slice of the document and cannot know that another batch changed a cross-referenced definition or provision. Even in serial batching, the junior receiving Batch 3 does not know what Batch 1 changed unless Sara explicitly includes that information in the delegation.

Definely's 2025 "Cascade" product emerged specifically because this problem — tracking first-, second-, and third-order knock-on effects — is "a critical gap that has forced lawyers to spend 40-60% of their time on manual review." The problem is hard enough that a company built a dedicated product around it.

**How to avoid:**
- Always batch sequentially, not in parallel — Batch 2 must know what Batch 1 changed
- Require each batch output to include a "Conforming Changes Required" section listing affected sections outside the batch scope
- After all batches complete, Sara must run a conforming-changes reconciliation pass before compiling the final revision set
- Include the full document map (section headings, paragraph IDs) in every batch delegation so the junior can flag cross-references explicitly
- For contracts with highly interconnected provisions (loan agreements, complex PSAs), consider a final "consistency check" delegation that reviews only the compiled revision set for internal contradictions

**Warning signs:**
- Batch output has no "Conforming Changes Required" entries (almost every substantive change creates at least one)
- Revision to a definition does not trigger review of all provisions using that defined term
- Redline changes a section number but does not update internal cross-references

**Phase to address:**
Quality Overhaul — Step 6 batch dispatch protocol; contract-reviser agent instruction upgrade

---

### Pitfall 5: Context Degradation on Long Documents (Lost in the Middle)

**What goes wrong:**
Sara reads a 170-paragraph PSA in a single pass. Provisions in the middle of the document — Articles 5-8 in a 12-article agreement — receive substantially less analytical attention than provisions at the beginning (Article 1 definitions, Article 2 purchase price) and end (Article 10 general provisions). The LLM's attention mechanism is known to degrade on middle-context content, and performance can drop by more than 30% compared to the same content appearing at the start or end.

The output looks complete — Sara covers all articles — but the depth of analysis is uneven. Moderate-severity issues buried in Article 6 get a one-line mention while low-severity issues in Article 2 get paragraphs.

**Why it happens:**
This is a documented phenomenon called "Lost in the Middle" (Liu et al., 2023, MIT Press/TACL). Language models exhibit a serial-position effect similar to human memory: recall and attention are strongest at the beginning and end of the input, weakest in the middle. For a 170-paragraph PSA, the "middle" is roughly paragraphs 50-120 — often including indemnification, representations, covenants, and closing conditions, which are precisely the highest-risk provisions.

**How to avoid:**
- Structure the review in explicit sequential passes, not one giant read — each pass covers a logical subsection (e.g., Article by Article)
- For the detailed review (Step 5), delegate to document-reviewer in defined chunks; do not ask a single agent to review a 170-paragraph document in one pass
- Position the highest-priority provisions at the start of each batch — the LLM will pay most attention to what it sees first
- Sara's Step 2 (Initial Read) should be a structural orientation, not a detailed review — reserve detailed analysis for the structured Step 4-5 framework
- After the review, ask: "Which articles have the fewest risk entries relative to their length?" — imbalanced coverage is a warning sign

**Warning signs:**
- Risk map entries are clustered in the first and last quartile of the document
- Middle articles (typically indemnification, reps, covenants) have fewer entries per paragraph than opening/closing articles
- Any article with zero entries in a substantive PSA (genuine zero-issue articles are rare)

**Phase to address:**
Quality Overhaul — Step 2 initial read + Step 5 risk map delegation structure; also relevant to RAG integration architecture

---

### Pitfall 6: Generic Language Instead of Deal-Specific Drafting

**What goes wrong:**
When Sara revises a provision or proposes replacement language, the proposed language is generic — "market standard" boilerplate that could have come from any form agreement. It does not reflect the specific deal context (property type, buyer's risk profile, commercial objectives, jurisdiction), does not integrate with the defined terms in this agreement, and may actually be worse than the original provision in ways that require context to understand.

Example: Sara proposes a standard due diligence termination right without incorporating the specific deposit mechanics and going-hard provisions that are unique to this PSA. The proposed language would create an inconsistency with the existing Section 3 that neither party notices until closing.

**Why it happens:**
LLMs are trained on a distribution of published legal forms and tend to produce responses that look like the training distribution average — which is generic form language. Without explicit instruction to (a) use this agreement's specific defined terms, (b) reference this agreement's specific provisions by section number, and (c) account for the commercial context established in intake, the reviser defaults to what generic training data suggests.

The 2025 lessons from AI legal drafting are clear: "High-quality precedents remain the gold standard, and large language models are not a substitute for precedents crafted by experienced knowledge lawyers."

**How to avoid:**
- Every contract-reviser batch delegation must include the full defined terms list and require use of those exact terms in proposed language
- Require proposed language to cite the specific section numbers it interacts with
- Include the commercial context (property type, buyer profile, deal structure) in every batch delegation — not just the risk map entries
- Sara must do a defined-terms-consistency check on all proposed language before compiling the final revision set
- For critical provisions (purchase price mechanics, deposit provisions, termination rights, closing conditions), Sara should draft or heavily revise rather than accepting junior output verbatim

**Warning signs:**
- Proposed language uses defined terms not present in the agreement (e.g., "Material Adverse Change" when the agreement uses "Material Adverse Effect")
- Proposed language references section numbers that do not exist in the agreement
- Multiple proposed provisions use identical boilerplate for structurally different situations
- Proposed language is identical or near-identical to what Sara would produce for any PSA, regardless of deal specifics

**Phase to address:**
Quality Overhaul — contract-reviser agent; Step 6 batch delegation protocol; reference library integration

---

### Pitfall 7: Missing Deliverable Completeness (Naked Redline)

**What goes wrong:**
Sara produces the redline and presents it without a transmittal memo and open items list. The partner receives a tracked-changes document with no narrative — no statement of the key issues, no explanation of the negotiation priorities, no list of commercial points requiring client input, no recommended next steps. The partner has to reconstruct Sara's thinking from the redline itself, which is exactly the kind of work a senior associate should be doing.

Even when a transmittal memo is produced, it is cursory — a one-paragraph summary that lists the sections changed without explaining why the changes matter or what outcome Sara is seeking.

**Why it happens:**
When the LLM finishes the redline task, "done" feels natural — the primary deliverable exists. The transmittal memo and open items list are second-order deliverables that require a different kind of thinking (strategic communication, prioritization) than the redline itself. Without a hard process requirement that the redline is not "complete" until all three deliverables exist, the system defaults to stopping at the visible finish line.

**How to avoid:**
- Sara's SKILL.md must define the unit of delivery as the "transmittal package" (redline + transmittal memo + open items list) — not the redline alone
- The contract-review-workflow.md must make Step 7 mandatory, not optional
- Sara should present to the partner using a completion checklist that requires all three deliverables to be checked off before the work product is presented
- The transmittal memo template must require: (1) overall assessment, (2) top 3-5 issues with recommended positions, (3) commercial points for client, (4) recommended next steps — not just a list of changed sections

**Warning signs:**
- Sara presents the redline directly without asking about the transmittal package
- Transmittal memo is under 300 words
- Open items list is absent or merged into the transmittal memo as a brief list
- No "Commercial Points" section in the transmittal memo — Sara made all the calls without flagging business questions for the partner

**Phase to address:**
Quality Overhaul — Step 7 protocol and completeness gate; Sara SKILL.md workflow requirements

---

### Pitfall 8: Aggressiveness Setting Not Changing Scope (Only Calibration)

**What goes wrong:**
The aggressiveness setting (1-5) affects how strongly Sara phrases findings but does not change which provisions she reviews or how many revision entries she produces. At Level 1, she flags 10 critical issues. At Level 5, she flags the same 10 issues but describes them more aggressively. A real attorney at Level 5 would review every paragraph and assign a disposition — the scope expands, not just the tone.

**Why it happens:**
Without explicit instructions that aggressiveness changes the completeness requirement (not just the output calibration), the LLM treats it as a tone modifier. The path of least resistance is to reuse the same analysis framework and adjust language strength.

**How to avoid:**
- Define aggressiveness levels in Sara's SKILL.md with explicit scope requirements:
  - Level 1-2: Flag high and medium risks; accept market terms; limited revision entries
  - Level 3: Flag all risks above `info`; propose market-standard alternatives; 25+ revision entries on a 150-paragraph agreement
  - Level 4-5: Paragraph-level disposition required for every non-boilerplate provision; maximize client position; 40+ revision entries on a 150-paragraph agreement; propose new reps and covenants not in the original document
- At Level 4-5, require Sara to perform Step 5.5 (paragraph-level disposition table) before Step 6 (redline preparation)
- Aggressiveness Level 4-5 should trigger a "did not review" warning if any substantive section has zero entries

**Warning signs:**
- Identical section coverage between a Level 2 and Level 5 review of the same document
- Level 5 review contains no proposed new provisions (a Level 5 review should add buyer protections not in the original)
- Level 5 open items list is shorter than 20 items on a 150-paragraph agreement

**Phase to address:**
Quality Overhaul — Sara behavioral framework; aggressiveness level specification

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Parallel batch dispatch (not sequential) | Faster redline production | Conforming changes missed across batches; internally inconsistent redline | Never — always batch sequentially |
| Single document read pass for full review | Simpler workflow | Lost-in-the-middle degradation on middle provisions | Only for documents under 30 paragraphs |
| Junior review without target risk list | Faster delegation | Generic output that misses deal-specific issues | Never at Level 3+ |
| Transmittal memo drafted from memory (not from risk map) | Saves one step | Transmittal priorities misaligned with actual risk map findings | Never |
| Accepting junior output without cover count check | Faster turnaround | Shallow review passes to partner unchecked | Never at Level 4-5 |
| Relying on LLM knowledge for market standards (no research) | No research step needed | Stale or jurisdiction-wrong characterizations | Only for routine, non-jurisdictional questions |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| read_docx + review delegation | Give junior the raw paragraph dump without the analysis framework | Always pair paragraph text with (1) representation, (2) target risk list, (3) defined terms, (4) paragraph ID map |
| redline_docx + revision JSON | Pass revision JSON from a single batch without reconciling conforming changes | Compile all batch outputs, run conforming-changes pass, then generate the redline |
| RAG reference library | Embed entire documents and retrieve full chunks | Chunk at provision/section level; use semantic search to retrieve specific analogous provisions, not whole documents |
| legal-researcher + web search | Accept first search result as verified market standard | Require researcher to triangulate across multiple sources and flag single-source claims |
| contract-reviser + long batch | Give reviser a 30-paragraph batch for a complex article | Keep batches under 20 paragraphs; group by logical unit (all reps together, all covenants together) |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full-document single context pass | Middle-section provisions underrepresented in risk map | Sequential article-by-article review passes | Any document over 50 paragraphs |
| Parallel subagent dispatch for batches | Inconsistent defined term usage across batches; cross-reference errors | Sequential dispatch; each batch gets prior batch's change summary | Any document with more than 2 batches |
| Legal-researcher web search for case citations | Hallucinated case names, wrong holdings | Require researcher to use CourtListener for case law; flag web-only citations as unverified | Always; never trust web-sourced citations without verification |
| Transmittal memo drafted from redline (not from risk map) | Transmittal priorities do not match actual risk severity | Draft transmittal from risk map, not from reviewing the redline | Every time — the risk map is the authoritative priority ranking |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Sending client document text in web searches | Client confidentiality breach; privilege waiver | Legal-researcher must never quote client document text in web search queries; search for legal concepts, not document excerpts |
| Logging full document text in prompt-log.md | Unnecessarily broad exposure in audit trail | prompt-log.md records the delegation instructions, not the full document text — reference paragraph IDs instead |
| RAG library indexing client work product | Attorney-client privilege indexed alongside reference materials | Maintain strict separation: RAG library contains only public/reference material; client documents never indexed |

---

## "Looks Done But Isn't" Checklist

- [ ] **Redline:** Transmittal memo and open items list must exist — redline alone is never complete
- [ ] **Risk Map:** Every substantive article (not just boilerplate) has at least one entry — zero-entry articles signal missed analysis
- [ ] **Disposition Table (Level 4-5):** Every non-boilerplate paragraph has Accept/Revise/Delete/Insert/Comment — no paragraph left uncategorized
- [ ] **Proposed Language:** Uses this agreement's defined terms — not generic terms from a different form
- [ ] **Conforming Changes:** Every batch output included a "Conforming Changes Required" section, and Sara reconciled all of them before generating the redline
- [ ] **Coverage Count:** Sara reported paragraph coverage ratio (paragraphs reviewed / total paragraphs) before presenting to partner
- [ ] **Market Standard Claims:** Every "market standard" characterization is either sourced or flagged as Sara's analytical judgment requiring partner validation
- [ ] **Case Citations:** Zero case names cited in output without a verified source (CourtListener or verified legal database)
- [ ] **Junior Review Gates:** Sara sent back any junior output that lacked paragraph IDs, section references, or was under the minimum entry count for the aggressiveness level

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Shallow pass discovered after delivery | HIGH | Re-run from Step 5 (risk map) with explicit paragraph-level disposition requirement; re-generate redline; re-issue transmittal package; explain to partner why a revised version is coming |
| Wrong market standard claim | MEDIUM | Legal-researcher validates the claim; Sara issues a corrected note to the partner flagging the correction before it goes to opposing counsel |
| Missing conforming changes discovered | MEDIUM | Run the conforming-changes reconciliation pass manually; identify all affected provisions; issue a corrected redline with a note of what changed |
| Generic proposed language discovered | MEDIUM | Sara revises specific provisions using the agreement's defined terms; does not require full restart |
| Hallucinated case citation discovered | LOW (if caught before delivery) / HIGH (if sent to opposing counsel) | Remove all citations; replace with description of rule plus note that specific authority requires attorney verification with Westlaw/Lexis |
| Naked redline delivered (no transmittal) | LOW | Draft transmittal memo and open items list from the existing risk map; deliver as a follow-up |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Shallow pass mistaken for complete review | Quality Overhaul — Sara framework + reviewer rework | PSA review test: Level 5 review produces 40+ entries on 150-paragraph agreement |
| Overconfident wrong legal analysis | Quality Overhaul + RAG Integration | Review output flags uncertainty on market-standard claims; no unverified case citations |
| Vague delegation producing generic output | Quality Overhaul — delegation model rework | Every delegation prompt includes representation, target risks, paragraph IDs, defined terms |
| Cross-reference blindness on conforming changes | Quality Overhaul — Step 6 batch protocol | Every batch output contains "Conforming Changes Required"; reconciliation pass completed |
| Context degradation on long documents | Quality Overhaul — Step 5 review structure | Risk map entries are distributed proportionally across document sections |
| Generic vs. deal-specific proposed language | Quality Overhaul + Reference Library | Proposed language uses agreement's exact defined terms; no generic boilerplate |
| Missing deliverable completeness | Quality Overhaul — Step 7 + completeness gate | All three deliverables (redline, memo, open items) present before partner presentation |
| Aggressiveness not changing scope | Quality Overhaul — Sara behavioral framework | Level 5 review coverage table shows paragraph-level disposition for all substantive provisions |

---

## Sources

- Observed PSA review failure (2026-02-15) — 10 changes on 170-paragraph document, no transmittal memo, no conforming changes, no new reps proposed
- Project MEMORY.md — lessons learned from first PSA review: shallow pass, missing cross-references, naked redline, 19/170 paragraphs insufficient
- Stanford HAI / Journal of Legal Analysis: "Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models" (2024) — hallucination rates 58-88% for specific legal queries; 75%+ for court holdings
- Stanford / Journal of Empirical Legal Studies (2025): Legal RAG systems (Lexis+ AI, Westlaw AI) hallucinate at 17-34% despite RAG architecture
- Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (TACL/MIT Press, 2024) — 30%+ performance degradation for middle-context content
- Artificial Lawyer, "Contract AI Barriers: Economics, Reasoning + Prompt Engineering" (2025-11-10) — structured reasoning requirements, prompt engineering complexity
- Artificial Lawyer, "Contract AI's Reliability Problem: When AI Gets It Wrong" (2025-10-23) — fabricated terms, phantom numbers, variability
- Zuva, "Problems with Prompts: Measurability, Predictability of LLM Accuracy" — prompt accuracy unknowable on unseen documents; LLM non-determinism
- Definely / LawNext, "Definely Launches First-of-Its-Kind Solution to Track Knock-on Effects of Contract Changes" (2025-08) — conforming changes require first/second/third-order tracking; 40-60% of review time spent on manual cross-reference checking
- Lexology, "Five Lessons We Learned About AI Legal Drafting in 2025" (2025-12-05) — high-quality precedents not replaceable by LLMs; deal-specific customization requires human judgment
- arXiv 2512.08769: "A Practical Guide for Designing, Developing, and Deploying Production-Grade Agentic AI Workflows" — instruction complexity degrades adherence; error rates compound in multi-agent systems
- Stanford Law School, "Hallucinating Law: Legal Mistakes with Large Language Models Are Pervasive" (2024-01-11)
- Jones Walker AI Law Blog, "From Enhancement to Dependency: What the Epidemic of AI Failures in Law Means for Professionals" (2025)

---
*Pitfalls research for: AI Legal Assistant Plugin (Sara) — Contract Review Quality*
*Researched: 2026-02-17*
