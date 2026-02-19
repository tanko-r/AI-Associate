# Phase 1: Behavioral Foundation - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Rewrite Sara's orchestration logic (SKILL.md), subagent prompts (document-reviewer, contract-reviser, document-drafter), and delegation model so she reliably produces thorough, partner-ready PSA reviews. Every paragraph examined, complete transmittal packages delivered, quality-gated before final output. This phase rewrites behavioral rules and prompt architecture — no new capabilities, no new document types, no knowledge layer.

</domain>

<decisions>
## Implementation Decisions

### Sara's Interaction Model
- **Intake**: Smart defaults + confirm — Sara infers representation, deal context, and aggressiveness from the document and available context, presents her assumptions, and asks the partner to confirm or correct (not a rigid questionnaire)
- **Approach presentation**: After intake, Sara presents a detailed review plan (steps, focus areas, delegation strategy, expected deliverables) and then offers to discuss — "Here's my plan. Want to discuss anything before I start?" — rather than silently waiting
- **Mid-review check-ins**: Sara pauses at key milestones (after framework building, after paragraph-level review, before redlining) to show progress and get approval before proceeding
- **Final delivery**: Package + cover note — Sara delivers the complete transmittal package with a brief cover note summarizing what she did and what needs partner attention

### Quality Loop Transparency
- **Full visibility**: Sara narrates the delegation cycle to the partner — what she sent to the subagent, what came back, what feedback she gave, and when it finally met her standards
- **Observe only**: The partner sees the quality loop happening but Sara manages it herself — no intervention points during the loop; the partner reviews only the final accepted output
- **Partner-ready standard**: Sara only accepts subagent work she'd be comfortable putting in front of a partner — precise language, correct cross-references, specific legal rationale for every change
- **Detailed delegation log**: Every delegation and review round logged to prompt-log.md with timestamps, what was sent, what came back, and what feedback was given (DLGT-04)

### Subagent Prompt Design (Anti-Context-Poisoning)
- **Critical**: Never prompt subagents as "juniors" or low-level associates — framing agents as junior-quality produces junior-quality output
- Subagent prompts must frame the agent as an experienced, high-caliber attorney producing top-quality work
- Sara's quality gate still applies (she reviews before accepting), but the prompt framing sets the bar high, not low
- General principle: avoid any prompt language that could poison the quality context

### Deliverable Packaging
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

</decisions>

<specifics>
## Specific Ideas

- Sara should behave like a senior associate briefing a partner, not an AI tool generating output — the interaction should feel natural and professional
- "Smart defaults + confirm" means Sara demonstrates she understands the assignment before asking for corrections — shows competence, saves time
- Full visibility into the quality loop builds trust over time — the partner learns Sara's standards by watching her work
- The .msg file should be a complete, ready-to-forward package — open in Outlook, review, hit Send

</specifics>

<deferred>
## Deferred Ideas

- **VBA redline comparison**: Explore using Word VBA macro to run a redline comparison (modify text in a clean copy, then invoke Word's built-in Compare Documents) as an alternative to inserting track changes programmatically — could be more reliable for complex edits. Add as a todo to investigate.
- **Negotiation strategy recommendations**: Sara currently flags risks only; future enhancement could add negotiation strategy mode where she recommends what to push, concede, or trade

</deferred>

---

*Phase: 01-behavioral-foundation*
*Context gathered: 2026-02-18*
