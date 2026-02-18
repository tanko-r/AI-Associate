# Phase 1: Behavioral Foundation - Research

**Researched:** 2026-02-18
**Domain:** LLM prompt architecture for multi-agent legal document review — behavioral rules, subagent prompt design, quality gate enforcement, deliverable packaging
**Confidence:** HIGH

## Summary

Phase 1 rewrites Sara's orchestration logic (SKILL.md), all four subagent prompts (document-reviewer, contract-reviser, document-drafter, legal-researcher), and the reference files (delegation-model.md, contract-review-workflow.md, work-product-standards.md) so that Sara reliably produces thorough, partner-ready PSA reviews. This is entirely a prompt engineering and behavioral specification project — no new infrastructure, no new Python code, no new document types.

The research investigates three domains: (1) the current codebase state and what specifically needs to change in each file, (2) prompt engineering patterns for multi-agent quality (including the anti-context-poisoning decision), and (3) the .msg file creation capability required by the deliverable packaging decision. The primary finding is that all 12 phase requirements (REVQ-01 through REVQ-06, DLGT-01 through DLGT-04, COLB-01, COLB-02) can be implemented purely through markdown file rewrites — the infrastructure is sound, the behavioral specifications are not.

**Primary recommendation:** Implement the three plans in sequence: (01-01) SKILL.md rewrite with aggressiveness definitions, interaction model, and quality gates; (01-02) document-reviewer upgrade with disposition table format and anti-context-poisoning framing; (01-03) contract-reviser, document-drafter, and delegation model upgrades with briefing templates and delegation logging. Add a write_msg utility to docx-tools for the .msg deliverable format.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Sara's Interaction Model
- **Intake**: Smart defaults + confirm — Sara infers representation, deal context, and aggressiveness from the document and available context, presents her assumptions, and asks the partner to confirm or correct (not a rigid questionnaire)
- **Approach presentation**: After intake, Sara presents a detailed review plan (steps, focus areas, delegation strategy, expected deliverables) and then offers to discuss — "Here's my plan. Want to discuss anything before I start?" — rather than silently waiting
- **Mid-review check-ins**: Sara pauses at key milestones (after framework building, after paragraph-level review, before redlining) to show progress and get approval before proceeding
- **Final delivery**: Package + cover note — Sara delivers the complete transmittal package with a brief cover note summarizing what she did and what needs partner attention

#### Quality Loop Transparency
- **Full visibility**: Sara narrates the delegation cycle to the partner — what she sent to the subagent, what came back, what feedback she gave, and when it finally met her standards
- **Observe only**: The partner sees the quality loop happening but Sara manages it herself — no intervention points during the loop; the partner reviews only the final accepted output
- **Partner-ready standard**: Sara only accepts subagent work she'd be comfortable putting in front of a partner — precise language, correct cross-references, specific legal rationale for every change
- **Detailed delegation log**: Every delegation and review round logged to prompt-log.md with timestamps, what was sent, what came back, and what feedback was given (DLGT-04)

#### Subagent Prompt Design (Anti-Context-Poisoning)
- **Critical**: Never prompt subagents as "juniors" or low-level associates — framing agents as junior-quality produces junior-quality output
- Subagent prompts must frame the agent as an experienced, high-caliber attorney producing top-quality work
- Sara's quality gate still applies (she reviews before accepting), but the prompt framing sets the bar high, not low
- General principle: avoid any prompt language that could poison the quality context

#### Deliverable Packaging
- **Transmittal format**: Structured memo with formal sections — Deal Summary, Review Scope, Key Changes, Open Items
- **Risk flagging over strategy**: Sara identifies risks and their severity but does not recommend negotiation strategy — the partner decides the approach
- **Open items**: Organized by contract provision (DD, reps, default remedies, etc.) so each item maps to where it lives in the document; embedded as a section in the transmittal memo, not a separate file
- **Disposition table**: Included as an appendix to the transmittal — the full Accept/Revise/Delete/Insert/Comment breakdown so the partner can see exactly what Sara reviewed and her reasoning
- **Delivery format**: .msg file for MS Outlook (Windows) plus markdown summary in chat. The .msg includes both the clean version and redline version as attachments
- **Email body**: The transmittal memo text is the email body; attachments are the clean docx, redline docx, and disposition table appendix

### Claude's Discretion

- Aggressiveness level definitions (1-5 scale) — calibrate based on existing lessons learned: Level 4-5 requires every paragraph examined with a disposition; coverage floors informed by "19 of 170 is not enough" and "35+ entries at Level 4, 40+ at Level 5 for 150-paragraph PSA"
- Exact milestone check-in points and what Sara shows at each
- Prompt-log.md structure and formatting
- How Sara formats her detailed review plan at the approach presentation step

### Deferred Ideas (OUT OF SCOPE)

- **VBA redline comparison**: Explore using Word VBA macro to run a redline comparison (modify text in a clean copy, then invoke Word's built-in Compare Documents) as an alternative to inserting track changes programmatically — could be more reliable for complex edits. Add as a todo to investigate.
- **Negotiation strategy recommendations**: Sara currently flags risks only; future enhancement could add negotiation strategy mode where she recommends what to push, concede, or trade
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REVQ-01 | Sara examines every paragraph and assigns a disposition (Accept/Revise/Delete/Insert/Comment) at aggressiveness Level 4-5 | SKILL.md rewrite adds aggressiveness level definitions with explicit scope requirements; document-reviewer produces Section A disposition table as mandatory output; coverage floor enforced in quality gate |
| REVQ-02 | Sara builds practice-area-specific analysis framework (target concept list + target risk list) before starting clause-by-clause review | Contract-review-workflow.md already defines Step 3; SKILL.md rewrite makes it a hard gate — Sara cannot proceed to Step 4 without a written analysis-framework.md; mid-review check-in after framework building |
| REVQ-03 | Sara drafts full replacement paragraph language with specific legal rationale for each revision | Contract-reviser prompt rewrite requires full paragraph text with rationale per change; anti-context-poisoning framing ensures high-caliber drafting; delegation briefing template mandates defined-terms injection |
| REVQ-04 | Sara verifies cross-references and conforming changes before compiling final revision set | Contract-reviser output format requires "Conforming Changes Required" section; Sara runs reconciliation pass after all batches; quality gate checks cross-references before redline_docx invocation |
| REVQ-05 | Sara delivers complete transmittal package (redline + transmittal memo + open items list) for every contract review | SKILL.md defines transmittal package as the unit of delivery; .msg file creation via write_msg utility; open items embedded in transmittal memo by provision; disposition table as appendix |
| REVQ-06 | Sara includes market standard citations in every substantive markup | Contract-reviser prompt requires "Market Rationale" field for every revision; document-reviewer disposition table includes market-standard assessment column; SKILL.md quality gate rejects revisions without rationale |
| DLGT-01 | Every subagent delegation includes representation, aggressiveness, target risk list, paragraph IDs, defined terms, and explicit output format | Delegation briefing template defined in delegation-model.md; SKILL.md mandates template use; prompt-log.md records every delegation with full template contents |
| DLGT-02 | Sara iteratively reviews junior work product and sends it back with specific feedback until it meets her standards (quality loop pattern) | SKILL.md quality loop section defines review criteria, feedback format, and minimum one round of revision before acceptance; quality loop narrated to partner per transparency decision |
| DLGT-03 | Sara's review of junior work is exacting — she checks legal reasoning, drafting precision, cross-reference accuracy, and market standard compliance before accepting | SKILL.md quality gate checklist with explicit checks: legal reasoning, drafting precision, cross-references, market standards, defined term consistency, coverage completeness |
| DLGT-04 | Sara logs every delegation and review cycle in prompt-log.md | Prompt-log.md format defined in SKILL.md with structured entries: timestamp, direction, purpose, full content, output file, review outcome |
| COLB-01 | Sara asks clarifying questions before starting complex work (representation, deal context, aggressiveness level, client priorities) | SKILL.md interaction model: smart defaults + confirm; Sara presents inferred assumptions and asks for corrections; practice area set at session start |
| COLB-02 | Sara proposes her approach and checks in with the partner before finalizing major work product | SKILL.md milestone check-ins at three points: after framework building, after paragraph-level review, before redlining; approach presentation step after intake |
</phase_requirements>

## Standard Stack

This phase is entirely prompt engineering — no new libraries for the behavioral rewrite itself. The one exception is the .msg file creation capability required by the deliverable packaging decision.

### Core (Files Being Rewritten)

| File | Current Size | Purpose | What Changes |
|------|-------------|---------|--------------|
| `skills/sara/SKILL.md` | 250 lines | Sara persona, orchestration, quality standards | Major rewrite: add aggressiveness definitions, interaction model (smart defaults, check-ins), quality gate checklist, delegation logging requirements, transmittal package enforcement, .msg delivery |
| `agents/document-reviewer.md` | 88 lines | Document review, issue spotting | Major rewrite: anti-context-poisoning framing (remove "junior" identity), add disposition table output format (Section A + Section B), minimum entry counts, paragraph ID requirements |
| `agents/contract-reviser.md` | 138 lines | Batch paragraph revision | Moderate rewrite: anti-context-poisoning framing, delegation briefing template input format, market rationale field, conforming changes section, defined-terms consistency check |
| `agents/document-drafter.md` | 85 lines | First-pass drafting | Moderate rewrite: anti-context-poisoning framing, transmittal memo template, .msg package assembly instructions |
| `agents/legal-researcher.md` | 80 lines | Legal research | Light rewrite: anti-context-poisoning framing, structured output format for framework building integration |
| `skills/sara/references/delegation-model.md` | 95 lines | Delegation patterns | Major rewrite: briefing template format, mandatory context fields, quality loop protocol, delegation logging format |
| `skills/sara/references/contract-review-workflow.md` | 406 lines | 7-step review process | Moderate update: add Step 5.5 (disposition table), milestone check-in gates, transmittal format change (structured memo, embedded open items, .msg packaging), disposition table appendix |
| `skills/sara/references/work-product-standards.md` | 83 lines | Document type formatting | Moderate update: transmittal memo format change (Deal Summary, Review Scope, Key Changes, Open Items), .msg packaging standard, disposition table appendix format |
| `commands/sara.md` | 17 lines | Slash command entry | Light update: mention smart defaults interaction model |

### Supporting (New Capability)

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| .msg file creation | Produce Outlook-ready email with attachments | Python utility using `independentsoft.msg` library (commercial, $299) OR low-level OLE construction via `olefile` (open source, BSD) OR custom CFBF writer |

### .msg Creation Options Evaluated

| Option | License | Cost | Maturity | Can Create with Attachments | Recommendation |
|--------|---------|------|----------|----------------------------|----------------|
| `independentsoft.msg` (MSG PY) | Proprietary | $299 one-time | Production/Stable (v1.6, 2019) | Yes — full API for recipients, body, attachments | Best API, but proprietary and $299 |
| `Aspose.Email for Python` | Commercial | Subscription | Production | Yes — comprehensive email creation | Overkill and expensive for single use case |
| `olefile` + custom MSG structure | BSD | Free | Write features marked "new/untested" | Theoretically possible but complex | Risky — MSG internal structure is complex |
| Custom Python script using `compoundfiles` | Free | Free | Low-level | Would need to implement MSG spec from scratch | Not recommended — too much work for this phase |
| `extract-msg` | GPL v3 | Free | Good for reading | No — read-only library | Cannot create .msg files |
| `outlook-msg` | Apache | Free | Stale (2019) | No — read-only | Cannot create .msg files |

**Recommendation (Claude's discretion):** Use `independentsoft.msg` if the $299 cost is acceptable — it has the cleanest API and creates fully compliant MSG files with attachments, recipients, and HTML body. If cost is a concern, build a minimal `write_msg.py` utility using `olefile` that constructs the minimum viable MSG structure (subject, body text, file attachments). The MSG OLE format is documented in [MS-OXMSG] and while complex, a "good enough" writer for this specific use case (email with text body + 2-3 file attachments) is feasible. A third option: defer .msg creation to Phase 2 or later and deliver as a zip file or markdown + attachments in Phase 1, adding .msg when the packaging tool is ready.

**Important note:** The .msg creation is the only piece of Phase 1 that requires new Python code. Everything else is markdown file rewriting.

## Architecture Patterns

### Recommended File Structure After Phase 1

No structural changes to the project layout. All changes are to existing files:

```
skills/sara/
├── SKILL.md                           # REWRITTEN: interaction model, aggressiveness defs, quality gates
└── references/
    ├── contract-review-workflow.md    # UPDATED: Step 5.5, milestone gates, transmittal format
    ├── delegation-model.md            # REWRITTEN: briefing template, quality loop, logging
    └── work-product-standards.md      # UPDATED: transmittal format, .msg standard

agents/
├── legal-researcher.md               # UPDATED: anti-context-poisoning framing
├── document-reviewer.md              # REWRITTEN: disposition table, anti-poisoning, entry counts
├── contract-reviser.md               # REWRITTEN: briefing template, market rationale, anti-poisoning
└── document-drafter.md               # UPDATED: anti-context-poisoning, transmittal drafting

docx-tools/
└── core/
    └── msg_writer.py                 # NEW (optional): .msg file creation utility
```

### Pattern 1: Anti-Context-Poisoning Agent Framing

**What:** Remove all "junior associate" and "3rd-year" framing from subagent prompts. Replace with expert-level framing that sets expectations for top-quality output.

**Why (user decision, confirmed by research):** The user decided this based on the observation that framing agents as "junior-quality" produces junior-quality output. Research confirms this directionally: while basic persona labels ("expert" vs. "novice") show inconsistent effects on factual accuracy tasks (PromptHub research, 2025), the anti-pattern of *self-limiting* framing is well-documented. Telling an agent it is a "2nd-year associate" or "junior" creates a context where the model patterns its output quality to match that framing — not by producing factually wrong content, but by producing less thorough, less precise, less confident output. The research suggests that *detailed, specific* expert framing is more effective than generic labels.

**Implementation pattern:**

Current (document-reviewer.md):
```markdown
You are a junior associate at the firm. Sara, a senior associate, has
asked you to review a document. She expects meticulous work...
Your Role: You are a 3rd-year associate handling document review.
```

Rewritten:
```markdown
You are an experienced attorney conducting a detailed document review.
You produce thorough, precise analysis that meets the highest
professional standards — every provision examined, every risk identified
with specific language and legal rationale, every cross-reference
verified. Your work product is the kind a senior partner would
trust without extensive re-review.
```

**Key principles for the rewrite:**
- Frame as experienced attorney, not junior
- Describe the *quality of output expected*, not the seniority level
- Include specific quality markers (thorough, precise, every provision, legal rationale)
- Do not remove Sara's review gate — she still reviews before accepting
- Sara's delegation language changes too: "I'm assigning this to you" not "I need a junior to handle this"

**Confidence:** MEDIUM. The user decision is locked. The research shows persona framing effects are measurable but variable. The strongest evidence is against *negative* framing (telling an agent it is low-quality). The rewrite removes that negative framing and adds detailed quality expectations, which is the approach research supports most strongly.

### Pattern 2: Smart Defaults + Confirm Interaction Model

**What:** Sara infers deal context from the document before asking questions. She presents assumptions and asks for confirmation/correction rather than asking from scratch.

**Implementation pattern:**

Current (SKILL.md, Receiving Assignments section):
```markdown
1. Parse the ask
2. Assess scope
3. Identify gaps — ask 1-3 targeted clarifying questions
4. Propose approach
5. Execute
```

Rewritten:
```markdown
1. Parse the ask and the document
2. Infer context: representation (from document language and partner's
   framing), deal type (from document structure), aggressiveness
   (default 3 unless context suggests otherwise), commercial context
3. Present assumptions: "Based on my read, we're representing the buyer
   in this PSA. The document is seller-drafted, roughly 170 paragraphs,
   standard structure. I'd suggest Level 4 aggressiveness given [reason].
   Does that match your expectations, or should I adjust?"
4. Confirm or correct with partner
5. Present detailed review plan with steps, focus areas, expected
   deliverables, and delegation strategy
6. Offer to discuss: "Here's my plan. Want to discuss anything before
   I start?"
7. Execute with milestone check-ins
```

**Key principle:** Sara demonstrates competence by showing she understands the assignment before asking for input. This is how a real senior associate operates — they don't ask "who is the client?" when the engagement letter says "representing Buyer."

**Confidence:** HIGH. This is a behavioral specification, not a technical implementation. The pattern is straightforward to express in SKILL.md.

### Pattern 3: Milestone Check-In Gates

**What:** Sara pauses at defined points during the review to show progress and get approval before proceeding.

**Recommended check-in points (Claude's discretion):**

| Milestone | What Sara Shows | When to Pause |
|-----------|----------------|---------------|
| After Intake (Step 1) | Confirmed assumptions: representation, deal type, aggressiveness, commercial context | Always — this is the "smart defaults + confirm" step |
| After Framework Building (Step 3) | Analysis framework: N target concept categories, M target risk patterns, key focus areas | Always — partner may redirect focus |
| After Paragraph-Level Review (Step 5/5.5) | Coverage summary: X paragraphs reviewed, Y revisions, Z acceptances; top 5 risks; disposition breakdown | Always at Level 4-5; optional at Level 1-3 |
| Before Redlining (Step 6) | Revision plan: N batches planned, estimated revision count, any "FLAG FOR SARA" items resolved | Always — last chance to adjust before the redline is built |
| Final Delivery (Step 7) | Complete transmittal package with cover note | Always |

**What Sara shows at each check-in:**
- A brief, structured summary (not a data dump)
- Key decisions she made and why
- What she plans to do next
- Any items needing partner input

**Confidence:** HIGH. Behavioral specification.

### Pattern 4: Structured Delegation Briefing Template

**What:** Every subagent delegation uses a mandatory template that packs all required context.

**Template for contract-reviser delegations (DLGT-01):**
```markdown
## Delegation Briefing — [Batch N of M]

**Matter:** [matter name]
**Representation:** [buyer/seller/tenant/etc.]
**Aggressiveness:** [1-5]
**Batch scope:** Paragraphs [p_X through p_Y] — [Section description]

### Paragraphs in This Batch
[Full text of each paragraph with paragraph IDs]

### Risk Map Entries for This Batch
[Filtered risk entries — only those matching paragraph IDs in this batch]

### Concept Map (Full)
[Complete concept map for cross-reference context]

### Document Outline
[Section headings with paragraph IDs for cross-reference verification]

### Defined Terms
[All defined terms from extract_structure]

### Prior Batch Changes (if batch > 1)
[Summary of revisions from prior batches that may affect this batch]

### Output Requirements
- Save to: [path]
- Format: [structured per contract-reviser output spec]
- Every revision must include: full replacement paragraph, changes made,
  risks addressed, conforming changes needed, market rationale
```

**Confidence:** HIGH. This is a structured specification. The template format is well-grounded in existing delegation-model.md patterns and the contract-review-workflow.md Step 6b requirements.

### Pattern 5: Quality Loop with Narration

**What:** Sara reviews subagent output, narrates the review to the partner, sends work back with specific feedback if it falls short, and only accepts when it meets her standards.

**Quality loop protocol:**
1. Sara dispatches delegation (logged to prompt-log.md)
2. Sara receives output
3. Sara reviews against quality gate checklist:
   - Legal reasoning: Is every revision legally sound?
   - Drafting precision: Is proposed language clean and specific?
   - Cross-references: Are all section references accurate?
   - Market standards: Does every revision cite market rationale?
   - Defined terms: Does proposed language use this agreement's terms?
   - Coverage: Are all paragraphs in the batch addressed?
4. Sara narrates to partner: "Received the reviewer's first pass. They covered 45 of 47 paragraphs in this batch — missing p_62 and p_63. The indemnification analysis is solid but they used 'Material Adverse Change' when this agreement uses 'Material Adverse Effect.' Sending back with corrections."
5. If deficient: Sara sends back with specific, written feedback
6. If acceptable: Sara incorporates into her work product
7. Sara must send work back at least once before accepting (per success criterion 5)

**Key: "At least once" requirement.** Success criterion 5 says Sara must send work back at least once. This does not mean artificial rejection — it means Sara reviews thoroughly and provides improvement feedback even on good work. A real senior associate always finds something to improve.

**Confidence:** HIGH. Behavioral specification grounded in existing delegation-model.md patterns.

### Anti-Patterns to Avoid

- **Generic "You are an expert" framing:** Research shows simple expertise labels have minimal effect. The rewrite must include *specific quality markers* — what "expert" output looks like, not just the label.
- **Artificial rejection for the "at least once" requirement:** The quality loop should produce genuine improvement feedback, not manufactured complaints. If the first pass is truly excellent, Sara's feedback should be refinements ("tighten the language in p_47" or "add a market rationale to the deposit provision change"), not fabricated problems.
- **Over-narrating the quality loop:** The partner wants to see that Sara is thorough, not read every line of every delegation. Keep narration to: what was sent, what came back (summary), what feedback was given (key points), when it was accepted.
- **Transmittal memo as afterthought:** The transmittal memo is the most important deliverable — it tells the partner what to focus on. Draft it from the risk map (the authoritative priority ranking), not by summarizing the redline after the fact.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| .msg file creation | Custom OLE compound file writer from scratch | `independentsoft.msg` library ($299) or `olefile`-based minimal writer | MSG internal OLE structure is complex with many required MAPI properties; hand-rolling risks producing files Outlook rejects |
| Disposition table format | Free-form markdown output from document-reviewer | Structured table format in the agent prompt with mandatory columns | Free-form output varies unpredictably; structured format ensures every row has paragraph ID, disposition, reasoning, market assessment |
| Delegation briefing template | Ad-hoc prompt construction per delegation | Template with required fields defined in delegation-model.md | Consistent template ensures DLGT-01 compliance; ad-hoc prompts drift toward vagueness over time |
| Quality gate checklist | Implicit review standards | Explicit checklist in SKILL.md with named items Sara checks | Implicit standards are not enforceable; explicit checklist is a prompt engineering tool that forces completeness |
| Aggressiveness level definitions | Vague "push harder" descriptions | Tabular definition with scope requirements, coverage floors, and entry count minimums | Vague definitions produce the "aggressiveness only changes tone, not scope" pitfall documented in PITFALLS.md |

**Key insight:** This phase is entirely about making implicit behavioral expectations explicit. Every problem in the first PSA review came from Sara not having specific enough instructions about what "thorough" means, what a "complete" deliverable includes, and how much context a subagent needs.

## Common Pitfalls

### Pitfall 1: Anti-Context-Poisoning Overcorrection

**What goes wrong:** Removing all role framing from subagent prompts makes them generic. The rewrite removes "You are a 3rd-year associate" but replaces it with nothing, or with such generic framing ("You are an experienced attorney") that the agent has no specific behavioral anchoring.

**Why it happens:** The anti-context-poisoning decision correctly identifies that "junior" framing hurts quality. But the fix is not to remove all framing — it is to replace it with *high-quality, specific* framing that describes the expected output quality in detail.

**How to avoid:** Each rewritten agent prompt must include:
1. A *specific* expertise framing (not generic "expert")
2. Detailed quality markers for this agent's specific task type
3. Explicit output format with mandatory fields
4. Rejection criteria — what makes output unacceptable

**Warning signs:** Subagent output becomes generic/unfocused after the rewrite; output quality is similar or worse than before despite "expert" framing.

### Pitfall 2: Disposition Table Becomes a Checkbox Exercise

**What goes wrong:** The document-reviewer produces a disposition table where every paragraph gets "Accept" except the obvious problems. The table technically exists (REVQ-01 met) but adds no analytical value.

**Why it happens:** Requiring a disposition for every paragraph without requiring *reasoning* for every disposition creates an incentive to mark non-obvious paragraphs as "Accept" with minimal thought.

**How to avoid:** Require a brief reasoning field for every disposition, including "Accept." For Accept dispositions, the reasoning should state why the provision is acceptable (e.g., "Standard mutual jury waiver — market for institutional transactions" or "Seller's AS-IS language is strong but not unusual for this market"). This forces the reviewer to actually read and evaluate each paragraph.

**Warning signs:** More than 70% of dispositions are "Accept" with identical or near-identical reasoning phrases; zero "Comment" or "Insert" dispositions; no info-severity findings.

### Pitfall 3: Prompt Length Explosion

**What goes wrong:** The rewritten SKILL.md and agent prompts become so long that they consume a large fraction of the context window before Sara even starts working. The behavioral specifications crowd out the document being reviewed.

**Why it happens:** Converting implicit expectations to explicit specifications naturally produces longer prompts. Each user decision (interaction model, quality loop transparency, deliverable packaging, anti-context-poisoning) adds specification text.

**How to avoid:** Keep the core SKILL.md focused on behavioral rules and decision-making. Move detailed formats (disposition table structure, briefing template, prompt-log format) to reference files that Sara loads on demand. The existing pattern (SKILL.md references `contract-review-workflow.md` and `delegation-model.md`) is correct — extend it rather than inlining everything.

**Warning signs:** SKILL.md exceeds 500 lines; agent prompts exceed 200 lines; Sara's initial context load leaves insufficient room for a 170-paragraph document.

### Pitfall 4: .msg File Fails Silently

**What goes wrong:** Sara produces a .msg file that looks correct but Outlook rejects it, fails to display attachments, or corrupts the email body. The partner cannot open the deliverable.

**Why it happens:** The MSG format is an OLE Compound File with specific MAPI property requirements. Minimal implementations may miss required properties (message class, store support mask, recipient display types) that Outlook needs.

**How to avoid:** If using `independentsoft.msg`, follow their documented API closely — it handles MAPI property requirements. If building a custom writer, test every generated .msg file in actual Outlook (Windows) before shipping. Create a test fixture in the docx-tools test suite that generates a sample .msg and validates its structure.

**Warning signs:** .msg files open in Outlook but show garbled text or missing attachments; files fail to open entirely; attachments are present but cannot be saved from Outlook.

### Pitfall 5: Quality Loop Becomes Infinite

**What goes wrong:** Sara's quality gate is so strict that she sends work back 3-4 times on every delegation, burning context window and time without meaningful improvement after the first round.

**Why it happens:** The "at least once" requirement combined with an exacting quality gate creates a tendency to find issues even when the output is good enough. Each round of revision consumes context window.

**How to avoid:** Define a maximum of 2 revision rounds per delegation. After 2 rounds, Sara either accepts with minor self-edits or handles the task herself. The existing delegation-model.md already suggests a 3-round limit — keep it. The "at least once" requirement means Sara always gives feedback; it does not mean she always sends the full work back.

**Warning signs:** Context window approaching limits during a single delegation cycle; diminishing returns on revision quality after round 1; Sara and the subagent going in circles on subjective style points.

## Code Examples

### Example 1: Aggressiveness Level Definitions (for SKILL.md)

```markdown
## Aggressiveness Levels

| Level | Scope | Coverage | Minimum Entries (150-para PSA) | Disposition Required |
|-------|-------|----------|-------------------------------|---------------------|
| 1 (Conservative) | Flag high-severity risks only; accept market terms | Key provisions only | 10-15 | No — risk map only |
| 2 (Moderate) | Flag high and medium risks; light markup | Major provisions | 15-25 | No — risk map only |
| 3 (Balanced) | Flag all risks above info; market-standard alternatives | All substantive provisions | 25-35 | Recommended |
| 4 (Aggressive) | Every paragraph examined; maximize client position | Every paragraph | 35+ revisions | Required — Section A disposition table |
| 5 (Maximum) | Every paragraph examined; propose new protections not in original | Every paragraph + new provisions | 40+ revisions | Required — Section A disposition table |

**Level 4-5 requires Step 5.5:** Before proceeding to redline preparation (Step 6),
Sara must produce a complete paragraph-level disposition table (Section A) covering
every paragraph in the document. Each paragraph receives one of:
- **Accept** — provision is acceptable as drafted (with brief reasoning)
- **Revise** — provision needs modification (with specific proposed change)
- **Delete** — provision should be removed (with reasoning)
- **Insert** — new provision needed after this paragraph (with proposed text)
- **Comment** — provision needs a comment bubble without text change (with comment text)

**Coverage floor enforcement:** If the disposition table contains fewer than
[minimum entries] revision entries, Sara flags this to the partner before proceeding:
"My review produced [N] revision entries on a [M]-paragraph document. At Level [X],
I'd expect [minimum]+. Should I look deeper, or does this coverage seem right for
this document?"
```

### Example 2: Document-Reviewer Output Format (for document-reviewer.md)

```markdown
## Required Output Format

Your review must contain two sections:

### Section A: Paragraph Disposition Table

For EVERY paragraph in the document (not just flagged items):

| Para ID | Section Ref | Disposition | Reasoning | Market Assessment | Risk Severity |
|---------|-------------|-------------|-----------|-------------------|---------------|
| p_1 | Preamble | Accept | Standard preamble identifying parties; no issues | Market | — |
| p_15 | 3.1(a) | Revise | Deposit goes hard on Day 1 with no DD period protection; need soft deposit through DD expiration | Below market — standard is soft deposit through DD period | High |
| p_42 | 5.2 | Comment | AS-IS disclaimer is broad but standard for this market; flag for partner awareness | Market for institutional deals | Info |
| p_63 | 7.1(b) | Insert | No buyer indemnification cap exists; need to add standard cap language after this paragraph | Missing — market standard includes cap at 10-15% of purchase price | High |

### Section B: Thematic Risk Map

Group related risks by theme, showing how provisions interact:

#### Theme: Due Diligence Protection
- p_8 (Section 2.3): 30-day DD period with no extension right [HIGH]
- p_12 (Section 3.1): Deposit goes hard immediately [HIGH]
- p_15 (Section 3.2): No termination right during DD [HIGH]
- **Compound risk:** These three provisions together eliminate buyer's
  ability to exit without losing deposit. Standard market: soft deposit
  through DD period with termination right.
```

### Example 3: Prompt-Log Entry Format (for SKILL.md)

```markdown
---
### 2026-02-18 14:32 — Delegation: Document Review (Batch 1)
**Direction:** Sara → document-reviewer
**Purpose:** First-pass paragraph-level review of PSA Sections 1-4 (pp. p_1 through p_42)

**Briefing sent:**
> [Representation: Buyer | Aggressiveness: 4 | Batch: 1 of 4]
> [42 paragraphs with full text and paragraph IDs]
> [12 target risk categories from analysis framework]
> [Defined terms: Purchase Price, Seller, Buyer, Property, Due Diligence Period, ...]
> [Output: Section A disposition table + Section B thematic risk map]
> [Save to: Sara-Work-Product/psa-review/junior-work/reviewer/batch-1-review.md]

**Output file:** Sara-Work-Product/psa-review/junior-work/reviewer/batch-1-review.md

---
### 2026-02-18 14:45 — Review: Document Review (Batch 1) — Round 1
**Direction:** Sara reviewing document-reviewer output
**Outcome:** SEND BACK — 3 issues

**Feedback given:**
> 1. p_15 (deposit provision): Your disposition says "Accept" but the deposit goes
>    hard on Day 1 with no DD period protection. This should be "Revise" — standard
>    market is soft deposit through the DD period. Please re-evaluate.
> 2. Missing market rationale on 8 of your 42 disposition entries. Every entry needs
>    a brief market assessment, including Accept dispositions.
> 3. Section B risk map does not connect the DD period (p_8), deposit (p_12), and
>    termination right (p_15) as a compound risk. These interact — flag the compound effect.

---
### 2026-02-18 15:02 — Review: Document Review (Batch 1) — Round 2
**Direction:** Sara reviewing document-reviewer revised output
**Outcome:** ACCEPTED — incorporated into analysis

**Notes:** Deposit provision correctly reclassified. Market rationale added to all entries.
Compound risk identified in Section B. Minor style edits made by Sara before incorporating.
---
```

### Example 4: Transmittal Memo Structure (for work-product-standards.md)

```markdown
## Contract Review Transmittal Memo

**To:** [Partner name]
**From:** Sara
**Date:** [Date]
**Re:** Review of [Document Type] — [Property/Deal Name]

### Deal Summary
[2-3 sentence description: parties, property, transaction type,
purchase price, key dates]

### Review Scope
- **Representation:** [Buyer/Seller/etc.]
- **Aggressiveness Level:** [1-5] — [brief description of what that means]
- **Document:** [filename], [N] paragraphs, [date of document]
- **Coverage:** [X] paragraphs reviewed, [Y] revision entries, [Z] accepted,
  [W] commented
- **Focus areas:** [top 3-5 areas of focus from analysis framework]

### Key Changes (Top 5-10)
For each key change:
1. **[Section Ref] — [Brief Title]** [Severity: HIGH/MEDIUM]
   - **Issue:** [What the current language does and why it is a risk]
   - **Change:** [What was revised and the market rationale]
   - **Partner note:** [Anything requiring partner judgment or client input]

### Open Items
Organized by contract provision:

#### Due Diligence
| Item | Section | Issue | Severity | Notes |
|------|---------|-------|----------|-------|
| DD period length | 2.3 | 30 days, no extension right | High | Market: 45-60 days with 15-day extension |

#### Representations & Warranties
[...]

#### Default & Remedies
[...]

### Disposition Table (Appendix)
[Full Section A table from document-reviewer output]
```

## State of the Art

| Old Approach (Current) | New Approach (Phase 1) | Why Changed |
|------------------------|------------------------|-------------|
| Subagents framed as "junior associates" (2nd/3rd year) | Subagents framed as experienced attorneys with specific quality markers | Anti-context-poisoning decision — junior framing produces junior output |
| Sara asks questions from scratch (rigid questionnaire feel) | Sara infers context, presents assumptions, asks for corrections | Smart defaults + confirm interaction model — demonstrates competence |
| Silent execution until final delivery | Milestone check-ins at 3-4 defined points | Partner visibility into progress and opportunity to redirect |
| Quality loop invisible to partner | Full narration of delegation cycle | Transparency builds trust; partner sees Sara's standards |
| Free-form subagent delegation prompts | Mandatory briefing template with required fields | DLGT-01 compliance; prevents vague delegation that produces generic output |
| Transmittal memo as optional appendage | Transmittal memo is THE primary deliverable; open items embedded; disposition table as appendix | Locked decision: structured memo with Deal Summary, Review Scope, Key Changes, Open Items |
| Redline + memo + open items as separate files | Single .msg file with body text + attachments ready to forward | Locked decision: .msg for Outlook delivery |
| Aggressiveness affects tone only | Aggressiveness affects scope, coverage floor, and entry count minimums | Pitfall 8 prevention: "19 of 170 is not enough" at Level 4 |
| Risk map as sole review output | Disposition table (Section A) + thematic risk map (Section B) required at Level 4-5 | REVQ-01: every paragraph gets a disposition |
| No minimum entry counts | Hard floor: 35+ at Level 4, 40+ at Level 5 for 150-paragraph PSA | Calibrated from lessons learned |

## Open Questions

1. **MSG library licensing decision**
   - What we know: `independentsoft.msg` is the best API for .msg creation ($299 commercial license). Open-source alternatives either cannot create .msg files (extract-msg, outlook-msg) or require low-level OLE construction (olefile).
   - What's unclear: Whether the $299 cost is acceptable, or whether a minimal olefile-based writer is preferred, or whether .msg delivery should be deferred.
   - Recommendation: Ask the user. If cost is acceptable, use independentsoft.msg. If not, build a minimal writer or deliver as zip+markdown in Phase 1 and add .msg in a later phase.

2. **Disposition table at Level 1-3**
   - What we know: User decision requires disposition table at Level 4-5. The "Claude's Discretion" section leaves Level 1-3 behavior to us.
   - What's unclear: Should Level 3 produce a partial disposition table (flagged items only) or should it remain risk-map-only?
   - Recommendation: Level 3 produces a risk map with optional disposition table. Level 1-2 produces risk map only. This creates a clear behavioral gradient across the scale.

3. **Document-reviewer vs. Sara for disposition table**
   - What we know: The disposition table is a paragraph-level artifact covering every paragraph. The document-reviewer subagent is the natural producer, but context window limits may prevent a single agent from processing 170 paragraphs in one pass.
   - What's unclear: Should the disposition table be produced by the document-reviewer in batches (like the contract-reviser), or should Sara produce it herself from the risk map?
   - Recommendation: Document-reviewer produces the disposition table in batches (same batching pattern as contract-reviser). Sara reviews each batch and compiles the final table. This is consistent with the existing architecture pattern and avoids context window issues.

4. **Prompt-log.md verbosity vs. utility**
   - What we know: DLGT-04 requires logging every delegation and review cycle. Full delegation briefings can be 1000+ words each. A PSA review might have 15-20 log entries.
   - What's unclear: Should prompt-log.md contain the full briefing text (maximally transparent but very long) or summaries with file references?
   - Recommendation: Log the full briefing text for the first delegation of each type; log summaries with file references for subsequent delegations of the same type. Always log full review feedback. This balances transparency with readability.

5. **"At least once" feedback requirement interpretation**
   - What we know: Success criterion 5 requires Sara to send work back at least once before accepting.
   - What's unclear: Does this mean literally every delegation gets sent back, or is it satisfied if Sara provides improvement feedback (even on good work) and the subagent incorporates it?
   - Recommendation: Interpret as "Sara always provides substantive feedback." On good first passes, Sara provides refinement feedback ("tighten the language in p_47, add market rationale to the deposit change") rather than rejecting the entire output. This avoids artificial rejection while ensuring Sara is genuinely reviewing.

## Sources

### Primary (HIGH confidence)
- Existing codebase: Direct analysis of all 9 files being modified — `skills/sara/SKILL.md`, `agents/document-reviewer.md`, `agents/contract-reviser.md`, `agents/document-drafter.md`, `agents/legal-researcher.md`, `commands/sara.md`, `skills/sara/references/contract-review-workflow.md`, `skills/sara/references/delegation-model.md`, `skills/sara/references/work-product-standards.md`
- `.planning/REQUIREMENTS.md`: All 12 phase requirements (REVQ-01 through REVQ-06, DLGT-01 through DLGT-04, COLB-01, COLB-02)
- `.planning/research/PITFALLS.md`: 8 identified pitfalls, all addressed by Phase 1
- `.planning/research/FEATURES.md`: Feature landscape and MVP definition
- `.planning/research/ARCHITECTURE.md`: System architecture and data flow patterns
- `.planning/phases/01-behavioral-foundation/01-CONTEXT.md`: User decisions constraining this phase
- Project MEMORY.md: Lessons learned from first PSA review — "19 of 170 is not enough", "never send a naked redline", "aggressiveness must change scope not just calibration"

### Secondary (MEDIUM confidence)
- [PromptHub: Role-Prompting Research](https://www.prompthub.us/blog/role-prompting-does-adding-personas-to-your-prompts-really-make-a-difference) — Basic persona labels show inconsistent effects; detailed expert framing more effective; anti-self-limiting framing validated
- [WaterCrawl: Role Prompting Guide](https://watercrawl.dev/blog/Role-Prompting) — Role prompting reliably improves specificity, style, and domain alignment
- [LearnPrompting: Role Prompting](https://learnprompting.org/docs/advanced/zero_shot/role_prompting) — Expert personas with detailed descriptions outperform simple labels
- [Claude Code Subagent Documentation](https://code.claude.com/docs/en/sub-agents) — Official subagent creation patterns, context isolation, skill injection
- [independentsoft.msg documentation](https://www.independentsoft.de/msgpy/tutorial/addattachment.html) — MSG file creation API with attachment support
- [independentsoft.msg PyPI](https://pypi.org/project/independentsoft.msg/) — Version 1.6, proprietary license, Python >=3.3
- [outlook-msg PyPI](https://pypi.org/project/outlook-msg/) — Version 1.0.0, Apache license, read-only (cannot create)
- [extract-msg PyPI](https://pypi.org/project/extract-msg/) — Version 0.51+, GPL v3, read-only (cannot create)
- [olefile documentation](https://olefile.readthedocs.io/en/latest/Howto.html) — OLE2 read/write, BSD license, write features "new and not thoroughly tested"

### Tertiary (LOW confidence)
- [arXiv 2507.03405](https://arxiv.org/pdf/2507.03405) — Prompt Engineering Guidelines for LLMs, 2025 — general persona prompting research; not specific to legal domain
- [arXiv 2512.08769](https://arxiv.org/html/2512.08769v1) — Multi-agent instruction adherence degradation — context for delegation quality concerns

## Metadata

**Confidence breakdown:**
- Architecture patterns: HIGH — All patterns are behavioral specifications implemented as markdown file rewrites; no technical risk
- Anti-context-poisoning: MEDIUM — User decision is locked and directionally supported by research; specific effectiveness depends on prompt details
- .msg creation: MEDIUM — Multiple library options identified; licensing/cost decision needed from user; technical implementation is straightforward once library is chosen
- Aggressiveness definitions: MEDIUM — Coverage floor numbers (35+ at L4, 40+ at L5) are grounded in lessons learned but need empirical calibration against actual reviews
- Quality loop protocol: HIGH — Behavioral specification; straightforward to implement in SKILL.md

**Research date:** 2026-02-18
**Valid until:** 2026-04-18 (60 days — behavioral specifications are stable; .msg library landscape unlikely to change)
