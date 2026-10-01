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
3. Sensor registry behind validation contracts — grows the thin/depth
   gates into team-extensible data.
4. Verification-command receipts — closes the approval-specificity gap.
5. Audit emitter ownership + per-run sharding — construction-grade
   auditability.
6. Plugin seam for policy packs — when distribution pressure appears.
7. Trust ladder rungs — when artifacts cross trust boundaries.

Each item is sized as one focused run. None requires another first,
except (5) benefits from (1)'s validator covering the new seams.

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
