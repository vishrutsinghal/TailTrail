# AI-DLC → TailTrail: Adoption Guide

Every significant mechanism found across the AI-DLC Harness Engineer Guide
and Developer Reference (~40 pages, three parallel reads), what it does,
how TailTrail can use it — and what to refuse. Governing rule throughout:
**adopt machinery, never identity.** TailTrail's individuality lives in
five decisions that are non-negotiable (Section 1). Everything else is
evaluated against them.

## 1. What makes TailTrail TailTrail (do not dilute)

1. **Evidence-bound scope.** Ownership derives from repository relationships,
   not declarations. No feature may grant edit authority on words alone.
2. **Fail-closed questions.** Ambiguity blocks with an answerable question;
   nothing silently resolves, nothing auto-approves.
3. **Approval-gated authority.** Managed writes, anchors, and closure each
   require explicit approval. No silent upgrades, ever.
4. **Recorded reasoning.** Decisions persist as artifacts (locks, anchors,
   receipts, proposals) — reviewable, replayable, auditable.
5. **Smallest-change discipline.** One file per requirement where possible;
   reuse before invention; no parallel abstractions.

Any adoption that weakens these five is rejected regardless of merit.
Each verdict below names which principle it serves or would violate.

## 2. Adopt (machinery that strengthens the five)

### 2a. Compile-time validation + `--check` drift guards
- **What:** `aidlc-graph compile` hard-errors on stem≠slug, duplicate
  slugs, multi-producers, unknown sensor IDs; CI byte-compares generated
  output so hand-edits fail loudly.
- **TailTrail use:** a `doctor`-level validator cross-checking scope
  decision ↔ matrix fingerprints ↔ anchor contracts ↔ thresholds, plus
  byte-compare on generated reports. Would have caught this session's
  matrix-staleness, fingerprint-split, and threshold-drift bugs pre-runtime.
- **Serves:** principles 1 (evidence integrity) and 4 (auditability).
- **Adaptation:** validate TailTrail's own artifacts (fingerprints,
  contracts, thresholds), not AI-DLC's schema. Same ritual, own content.

### 2b. Audit-first atomicity + emitter ownership
- **What:** emit-before-mutate, throw-before-touching-state, per-clone
  audit shards, tool-owned emitters — the model never writes audit rows.
- **TailTrail use:** per-run audit sharding in the ledger; a construction
  rule (not convention) that hosts never emit ledger events directly.
- **Serves:** principles 3 and 4. Currently true by convention; make it
  true by construction.

### 2c. Sensors: pull-authored deterministic checks
- **What:** a registry of runnable checks (`id`, command, advisory vs
  blocking severity, `fire_on: write|gate`); stages pull checks by name
  instead of hardcoding them.
- **TailTrail use:** generalizes the thin/depth gates into a check
  registry backing validation contracts — checks become data (listable,
  versionable, team-extensible) rather than code paths.
- **Serves:** principles 1 (evidence-graded checks) and 5 (reuse over
  invention). Keep TailTrail's gate semantics; adopt only the
  registry + severity + pull pattern.

### 2d. Strict-additive rules + filename-as-scope
- **What:** rule layers concatenate, never override; scope derives from
  filename, eliminating override-ordering bugs. Plus `stale_after` dates
  baked into the format.
- **TailTrail use:** policy packs + learnings governance adopt both
  verbatim — including expiry dates, which answer the stale-learnings rot
  structurally instead of by sweeps.
- **Serves:** principles 4 and 5. No adaptation needed; it's pure discipline.

### 2e. Verification-command receipts
- **What:** a human-approved command (SHA-256 pinned, length-capped)
  gating construction checkpoints, with recorded proofs.
- **TailTrail use:** close the "approved what, exactly?" gap in managed
  execution — bind the command hash to the approval, so receipts prove
  *which* command ran under *whose* approval, not just that *a* command ran.
- **Serves:** principles 3 and 4. Additive to existing receipts.

### 2f. Question rituals with receipts
- **What:** 2-option defaults, conditional 3rd option, batch limits
  (4 questions / 4 options), verbatim user-input recording,
  summary-confirmation receipts, accept-as-is escape hatch after 3rd
  rejection (a stop rule, not surrender — it records the override).
- **TailTrail use:** unify the three homegrown questionnaires (official
  Q&A, TASK-Q1, SCOPE-Q1) under one ritual: batch discipline, confirmation
  receipts, and a single stop rule replacing the per-feature caps.
- **Serves:** principle 2 (answerable questions) and 4. TailTrail keeps
  its question *content*; adopts the *ritual*.

## 3. Adapt (good bones, TailTrail shape required)

### 3a. Content-addressed anchors + trust ladder (informational → signed)
- **What:** source listings with SHA-256; receipts graduating by
  authenticity, not just integrity.
- **TailTrail use:** adopt progressively — integrity now (already have
  fingerprints), higher rungs only when artifacts cross trust boundaries
  (CI, remotes, multi-host). Do not build signing infrastructure
  speculatively.
- **Constraint:** must never slow the local loop; higher rungs opt-in per run.

### 3b. Plugin mechanism (additive-only contributions)
- **What:** N-way merge with set-union structure, ordered sentinel splices
  for prose, drop-with-attribution, content-hashed idempotency, per-plugin
  doctor checks.
- **TailTrail use:** the distribution model for policy packs + host
  adapters — modify behavior without forking. Adopt the *seam*
  (contributions, sentinels, sidecar provenance), not their manifest
  schema or marketplace machinery.
- **Constraint:** TailTrail stays single-checkout-first; plugin surfaces
  must not recreate the launcher-skew class of bug (two copies drifting).

### 3c. Engine/conductor split + in-flight immutability
- **What:** deterministic routing separated from execution quality;
  learnings apply next workflow, never mid-flight.
- **TailTrail use:** largely already true (Navigator vs managed
  execution; sweep-then-apply learnings). Adopt explicitly as doctrine:
  write down that no learning, threshold, or policy change takes effect
  mid-run, and enforce it where currently conventional.
- **Constraint:** doctrine + enforcement points only, no rearchitecture.

## 4. Refuse (would dilute TailTrail)

- **Swarm/mob execution.** TailTrail's single-host managed execution is
  auditability, not a missing feature. Revisit only on multi-agent demand.
  (Violates nothing directly — but solves nothing we have.)
- **14-agent persona roster.** Ceremony without capability here; host +
  task-type model covers the ground cheaper. (Violates 5.)
- **Per-harness generated projections.** Justified at 7 harnesses; with
  our launcher skew still open, generated copies would drift. Fix skew
  first; reconsider after. (Threatens 4.)
- **Silent auto-promotion of any kind** (learnings, scopes, modes).
  Directly violates 2 and 3. Their escape-hatch rule is acceptable only
  because it *records the override* — adopt that half alone (see 2f).
- **Trust ladder above informational** until a real boundary crossing
  needs it. (Violates 5: speculation.)

## 5. Suggested adoption order

1. Compile-time validator (`doctor` + contracts cross-check) — converts
   this session's costliest bug classes into build errors.
2. Question ritual unification — one ritual, three questionnaires, plus
   the universal stop rule.
3. Optional detailed plan-to-closure record — lets a user request, study,
   question, revise, and approve an exact implementation plan without making
   every small task pay the same documentation cost.
4. Sensor registry behind validation contracts — grows the thin/depth
   gates into team-extensible data.
5. Verification-command receipts — closes the approval-specificity gap.
6. Audit emitter ownership + per-run sharding — construction-grade
   auditability.
7. Plugin seam for policy packs — when distribution pressure appears.
8. Trust ladder rungs — when artifacts cross trust boundaries.

Each item is sized as one focused run. None requires another first,
except (6) benefits from (1)'s validator covering the new seams.

## 6. Architecture comparison

Same problem (guardrailed AI-driven delivery), mirrored structure,
opposite centers of gravity: **AI-DLC is methodology compiled down;
TailTrail is evidence compiled up.** Everything below follows from that.

| Layer | AI-DLC | TailTrail | Delta |
|---|---|---|---|
| Source of truth | Hand-authored Markdown (`core/`) | Repository evidence (graph, fingerprints) | Author-trust vs repo-trust; requirement interpretation exists to supply intent evidence can't |
| Compilation | `compile` → `stage-graph.json` + `scope-grid.json`, validated, byte-compared | Navigator decide → scope evidence + Planning Lock, fingerprinted | Same shape; theirs hard-errors on drift, ours never cross-validates — the validator gap |
| Runtime | Deterministic engine + thin conductor | Navigator routing + managed execution + DWR | Closest match; their engine is dumber by design, ours needs gates because it's smarter |
| State | `aidlc-state.md` + 3 nested machines + 108-event taxonomy | Run ledger (JSONL) + lock states | Theirs human-readable, ours machine-first; steal audit-first atomicity |
| Scope | File-authored scopes transposed to grid | Computed per run (candidates → owners) | Declared vs derived; keep TailTrail's synthesis (anchors constrain derived scope) |
| Agents | 14 persona files | Host + 4-bucket task-type gate | Individuality in miniature: do not converge |
| Execution | Conductor + swarm referee + verification commands | Managed execution + receipts + DWR | Adopt human-binds-command-hash receipts |
| Learning | Diary → gate → dated rules, next-workflow-only | V3 journal + governance + retrieval + refresh | Ours more engineered; theirs more *used* — gap is ritual touchpoints, not schema |
| Extensibility | Additive plugin seam | Ad-hoc adapters + packs | Copy the seam when distribution pressure arrives, not before |
| Multi-harness | 7 runtimes via generated projections | 1 checkout + 1 stale launcher | Fix skew before borrowing anything here |

Candidate structural adoptions: (1) plan-level cross-check validator,
(2) verification-command receipts, (3) per-stage learning rituals.

## 7. Optional detailed plan-to-closure record

### 7.1 Decision

**Adopt as an optional pre-approval action.** TailTrail should add
`Generate detailed implementation plan` beside the existing approve, question,
revise, and reject choices. The action produces one human-readable Markdown
record that the user can review asynchronously, question by section, request
changes to, and approve by exact revision. After implementation, closure adds
the factual outcome to the same readable record without rewriting the approved
plan.

This adopts AI-DLC's useful habit of durable planning artifacts without copying
its questionnaire-oriented document set. TailTrail keeps one task-centered
record and continues to use repository evidence, a Planning Lock, an immutable
approved anchor, evidence receipts, and the Completion Report as canonical
machine state.

### 7.2 Problem and user-control goal

The compact Start report is intentionally efficient, but some users need more
time and detail before granting source-write authority. Today they can ask
questions or request revisions, yet the information remains spread across the
Start report, discussion receipts, scope evidence, Planning Lock, and later
closure artifacts. That makes careful offline review harder than it should be.

The new option should let the user:

1. keep the fast compact approval path for a small, obvious change;
2. explicitly request a detailed plan when the task deserves closer review;
3. read the saved Markdown file at their own pace;
4. ask questions using stable requirement, step, test, and risk identifiers;
5. request an append or revision without granting implementation authority;
6. approve the exact reviewed revision and fingerprint; and
7. return after implementation to see plan-versus-actual results and closure
   evidence in the same document.

The feature is a control improvement, not extra ceremony by default.

### 7.3 Proposed approval menus

Before a detailed plan exists, the host-facing choice set should be:

```text
TailTrail plan is ready.

1. Approve the current plan
2. Generate a detailed implementation plan
3. Ask a question
4. Request changes
5. Reject the plan
```

Selecting option 2 is explicit authority for bounded, read-only planning work
only. It does not approve implementation, tests, scanners, dependency changes,
Git mutations, publication, or deployment.

After generation, the choices should become:

```text
Detailed plan generated:
.tailtrail/runs/<run-id>/delivery-record.md

1. Approve this exact detailed plan
2. Ask a question about the plan
3. Append or revise the plan
4. Regenerate after additional bounded read-only investigation
5. Return to the compact plan
6. Reject the plan
```

Only one approval target may be active. Once a detailed plan is generated, a
generic approve action must resolve to its current revision or refuse when the
revision is stale, manually altered, or has an unresolved proposal.

### 7.4 Artifact model and ownership

Use one friendly path per run:

```text
.tailtrail/runs/<run-id>/delivery-record.md
```

Retain immutable internal revisions beneath the same run, for example:

```text
.tailtrail/runs/<run-id>/planning/detailed-plan-v1.json
.tailtrail/runs/<run-id>/planning/detailed-plan-v1.md
.tailtrail/runs/<run-id>/planning/detailed-plan-v2.json
.tailtrail/runs/<run-id>/planning/detailed-plan-v2.md
.tailtrail/runs/<run-id>/completion-reports/report-1.json
```

`delivery-record.md` is the current human-readable projection. It is not a new
canonical state store. Its plan data comes from the current Start report,
Planning Lock, structured requirements, scope decision, bounded investigation
receipts, and approved revisions. Its closure data comes from checkpoints,
validation receipts, review results, drift assessment, and the canonical
Completion Report.

The projection should declare at its top:

```yaml
run_id: <run-id>
status: awaiting-plan-approval
plan_revision: 2
plan_fingerprint: sha256:...
generated_from: saved-tailtrail-artifacts
canonical: false
```

The renderer owns the file. A host or model must not fabricate receipt results
or write arbitrary approval state into it.

### 7.5 Detailed plan contents

The pre-approval document should include, when applicable:

- goal, requirement IDs, and acceptance criteria;
- current assumptions, material questions, and explicit exclusions;
- repository understanding and evidence confidence;
- callers, boundaries, and components likely to be affected;
- files to inspect, expected implementation owners, proof-only paths, and
  paths that remain read-only;
- existing helpers, types, conventions, and validation patterns to reuse;
- dependency decision and policy implications;
- ordered implementation steps with prerequisites;
- focused, negative, regression, boundary, and higher-tier validation plans;
- security, privacy, accessibility, compatibility, data, migration, and
  operational risks when applicable;
- rollback, recovery, or correction strategy;
- selected TailTrail controls and why skipped controls are not needed; and
- the exact approval boundary and current approval status.

Every reviewable element should have a stable identifier:

```markdown
### REQ-01 — Retry failed payment capture safely

### STEP-01 — Reuse the existing retry policy

### TEST-01 — Stop after the configured retry limit

### RISK-01 — Preserve request idempotency
```

Stable identifiers let a user ask `Why is STEP-01 required?`, `Add the timeout
case to TEST-01`, or `What evidence supports RISK-01?` without depending on line
numbers or raw chat history.

### 7.6 Generation and bounded investigation

Generation must use the saved plan first. If more detail requires repository
facts, TailTrail may inspect only paths already supported by the scope proposal
or explicitly selected through the existing approved read-only investigation
boundary. It must:

- avoid repository-wide source loading by default;
- record inspected paths and hashes in planning receipts;
- label inferred or unavailable facts honestly;
- keep unresolved ownership or requirement questions blocking;
- never convert an inspection target into an editable owner automatically;
- never execute project code, tests, package managers, scanners, or Git
  mutations as part of plan generation; and
- never create implementation authority from the existence of the document.

If the evidence is insufficient, the generated document should contain a
specific open question rather than an invented implementation step.

### 7.7 Questions, appends, and revisions

Questions remain read-only and should be answered from the exact saved plan
revision plus its referenced evidence. The response should cite stable section
IDs and say when the saved plan does not contain enough evidence.

An append or revision is a proposal, not an in-place invisible edit. It should:

1. identify the affected stable IDs;
2. record the user-requested change and reason;
3. regenerate structured plan state and the Markdown projection;
4. increment the plan revision;
5. preserve the prior immutable revision;
6. recompute the plan fingerprint; and
7. invalidate any pending approval for the superseded revision.

The existing plan-revision machinery should own these transitions. Do not add a
parallel revision ledger just for Markdown. A request to add a material new
requirement must return to the active requirement authority—TailTrail, official
AI-DLC, or Intent Bridge—rather than silently editing prose.

### 7.8 Exact approval contract

Approval must bind all of the following:

- run and target identity;
- detailed-plan revision;
- detailed-plan structured fingerprint;
- approved requirement and scope fingerprints;
- referenced bounded-investigation receipts; and
- selected validation and safeguard contracts.

The friendly Markdown bytes may also be hashed for tamper detection, but the
structured fingerprint remains authoritative. Approval must fail closed when:

- the file was manually modified after generation;
- the structured revision and Markdown projection disagree;
- a question or revision is still materially unresolved;
- repository or policy evidence required by the plan is stale;
- the plan references an unknown requirement, owner, check, or control; or
- the user names an older revision without an explicit review transition.

Manual Markdown edits should not be silently trusted. A future import command
may validate supported changes and convert them into a normal revision
proposal; until that exists, the safe behavior is to show the mismatch and ask
the user to request the corresponding revision through TailTrail.

### 7.9 Same document after implementation

After approved implementation and closure, TailTrail should add these sections
to `delivery-record.md`:

- Implementation Outcome;
- Files Actually Changed;
- Existing Helpers Reused;
- Dependencies Actually Changed;
- Plan Versus Actual;
- Validation Evidence;
- Review, Security, Quality, and Operational Results;
- Deviations and Approved Amendments;
- Remaining Risks and Deferred Work; and
- Closure Status and canonical artifact references.

The approved plan section must remain byte-stable or reconstructably identical
to the approved revision. Closure fills only result-oriented sections from
saved evidence. A useful comparison table is:

```markdown
| Planned item | Actual result | Disposition | Evidence |
|---|---|---|---|
| STEP-01 | Existing retry policy reused | matched | source-edit receipt |
| TEST-01 | Unit and integration coverage added | expanded | validation receipt |
| RISK-01 | Idempotency preservation verified | satisfied | test + review receipt |
```

Missing evidence must render as `not run`, `unavailable`, `stale`, `blocked`,
or `evidence incomplete`; it must never be converted to `passed`. Material
unapproved deviation keeps closure incomplete and routes to amendment or
bounded correction.

### 7.10 State and lifecycle integration

The feature should reuse the current run rather than introduce another
workflow. Suggested planning substates are projections of existing events:

```text
compact-plan-awaiting-approval
    -> detailed-plan-generating
    -> detailed-plan-awaiting-review
    -> detailed-plan-revision-pending
    -> detailed-plan-awaiting-review
    -> approved
```

Questioning does not change the approval state. Rejection preserves the same
run and feedback path. Returning to the compact plan explicitly retires the
detailed-plan approval target but does not delete its revision history.

After approval, the normal Durable Workflow Runtime remains responsible for
execution, evidence, correction, and closure. The document observes those
systems; it does not become a workflow engine.

### 7.11 Command and host-surface sketch

Reuse the existing planning and closure facades. Illustrative commands are:

```bash
tailtrail planning detailed-plan generate --root . --run-id <run-id>
tailtrail planning detailed-plan show --root . --run-id <run-id>
tailtrail discuss --run-id <run-id> --question "Why is STEP-02 needed?"
tailtrail planning revise --root . --run-id <run-id> --changes '<structured-change>' --approved-proposal
tailtrail approve --run-id <run-id>
tailtrail closure finalize --root . --run-id <run-id>
```

Names are proposals, not a requirement to add a new top-level command. CLI,
MCP, Codex, Copilot, and Claude should expose the same action and return the
same run ID, revision, fingerprint, file path, and next choices.

### 7.12 Implementation reuse points

The smallest maintainable implementation should reuse:

- Start report and Planning Lock readers for the compact plan;
- planning discussion for section-based questions;
- planning investigation for explicitly approved read-only evidence;
- planning revision for append and revise operations;
- approved anchors for immutable requirement and scope identity;
- run ledger events for generation, revision, approval, and closure linkage;
- completion-report aggregation for actual outcomes; and
- existing atomic file and canonical JSON serialization helpers.

Do not add a second plan store, approval system, question engine, or completion
engine. Add one structured detailed-plan projection and one deterministic
Markdown renderer over existing ownership boundaries.

### 7.13 Failure behavior and safeguards

| Condition | Required behavior |
|---|---|
| Detailed generation fails | Preserve compact plan and return a categorical error; create no partial approval target. |
| Required source fact is unknown | Record an open question or `unknown`; do not invent a step. |
| File changes outside TailTrail | Detect hash mismatch and block approval until regeneration or validated revision. |
| Revision requested | Preserve prior revision, create a new proposal, invalidate old pending approval. |
| Material change after approval | Use the normal amendment flow; never rewrite approved plan history. |
| Closure evidence missing | Render evidence incomplete and keep successful closure blocked. |
| Projection write interrupted | Rebuild deterministically from canonical artifacts; never repair canonical state from Markdown. |
| Sensitive content appears | Store only sanitized summaries and artifact references; exclude raw secrets, source bodies, prompts, and logs. |

### 7.14 Focused validation plan

At minimum, add runnable checks proving:

1. the new option appears only for a plan awaiting approval;
2. generating a detailed plan creates no source edit or implementation event;
3. repeated generation from unchanged inputs produces identical structured and
   Markdown content;
4. questions create discussion receipts but do not mutate the plan;
5. appending or revising creates a new revision and changes its fingerprint;
6. approving an old, stale, mismatched, or manually edited revision fails;
7. the approved plan section remains unchanged after closure finalization;
8. plan-versus-actual rows link only to current run evidence;
9. missing or failed checks never render as passed;
10. material drift keeps closure evidence-incomplete;
11. compact approval remains available when detailed planning was not selected;
12. the same semantics and identifiers are returned by CLI and supported host
    adapters; and
13. Windows, macOS, and Linux path rendering remains deterministic.

### 7.15 Incremental delivery

Deliver the feature without coupling every part into the first patch:

1. **Projection MVP:** generate and show a deterministic Markdown plan from
   existing saved planning artifacts.
2. **Review integration:** add menu option, stable section IDs, saved questions,
   and revision regeneration.
3. **Approval binding:** bind exact revision and fingerprint; add tamper and
   staleness checks.
4. **Closure integration:** add evidence-backed actuals and plan-versus-actual
   sections to the same friendly path.
5. **Host conformance:** expose identical behavior through CLI, MCP, and host
   adapters, with negative fixtures for unauthorized shortcuts.

Each increment should be independently usable and keep the compact path
unchanged.

### 7.16 Acceptance criteria

The feature is ready when a user can start one run, choose detailed planning,
review the saved file later, ask a section-specific question, request a plan
append, approve the exact new revision, complete the implementation, and read
evidence-backed closure in the same friendly document—with proof that the
approved plan content did not change after approval.

### 7.17 Non-goals

- Do not generate the detailed file for every task by default.
- Do not copy AI-DLC's full set of question and stage documents.
- Do not make Markdown the canonical approval or evidence store.
- Do not allow document generation to authorize source writes or commands.
- Do not silently import arbitrary manual edits.
- Do not rewrite approved plan sections during closure.
- Do not replace the Planning Lock, approved anchor, DWR, or Completion Report.
- Do not claim the implementation matched the plan without current receipts.

This design strengthens TailTrail's individuality: the user chooses the amount
of planning detail, approval remains exact and explicit, repository evidence
grounds the plan, and one readable record connects intent to verified closure.
