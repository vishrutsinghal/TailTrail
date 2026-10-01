# AI-DLC → TailTrail: Adoption Guide

This is a review and implementation guide based on the AI-DLC user guides,
architecture references, harness-engineering material, and the current
TailTrail implementation. It explains what each mechanism does, what
TailTrail already has, how to add the useful part, how to validate it, and
what to refuse. Governing rule throughout:
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

## 7. Review scope and evidence base

This section makes the recommendations reviewable instead of treating the
upstream design as a feature checklist.

### 7.1 TailTrail implementation inspected

The proposals below are grounded in these existing TailTrail surfaces:

| Concern | Existing TailTrail surface | Why it matters |
|---|---|---|
| Workflow selection and stage order | `scripts/workflow_runtime/templates.py` | Already provides named templates and ordered stages; profiles should wrap this instead of replacing it. |
| Deterministic plan compilation | `scripts/workflow_runtime/compiler.py` | Already produces a fingerprinted execution plan; the missing work is cross-artifact validation and richer stage contracts. |
| Durable event storage and replay | `scripts/workflow_runtime/storage.py`, `scripts/workflow_runtime/state.py`, `scripts/workflow_runtime/projection.py` | Already provides the right event-journal foundation; no second state store should be introduced. |
| Stage-to-adapter routing | `scripts/workflow_runtime/adapter_catalog.py` | Natural home for capability declarations and adapter compatibility checks. |
| Broad run ledger | `scripts/run-ledger.py` | Central event vocabulary exists, but emitter ownership and producer coverage are not yet explicit contracts. |
| Context routes | `scripts/route-context.py` | TailTrail already selects focused context by route; AI-DLC conditional modules should strengthen this instead of adding personas. |
| Feature/test inventory | `tailtrail-registry.json` | A useful source for a coverage ratchet if it is validated rather than trusted blindly. |
| Lifecycle guidance | `AIDLC.md` | TailTrail already has minimal, standard, and comprehensive depth. Workflow profiles should map onto these established terms. |

This is a design proposal. Example JSON and command names are illustrative
until the relevant implementation run approves a final schema and CLI.

### 7.2 AI-DLC material used

The main upstream references are:

- [Workflow profiles](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/workflow-profiles.md)
- [Phases and stages](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/04-phases-and-stages.md)
- [Scopes, depth, and test](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/05-scopes-and-depth.md)
- [State and audit](https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/10-state-and-audit.md)
- [Architecture](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/01-architecture.md)
- [Plane architecture](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/02-plane-architecture.md)
- [Stage protocol](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/04-stage-protocol.md)
- [Sensor system](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/07-sensor-system.md)
- [Rule system](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/08-rule-system.md)
- [Testing strategy](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/09-testing.md)
- [State machine](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/12-state-machine.md)
- [Runtime graph](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/13-runtime-graph.md)
- [Stage definition](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/15-stage-definition.md)
- [Artifact vocabulary](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/16-artifact-vocabulary.md)
- [Skill/engine boundary](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/17-skill-system.md)
- [Plugin mechanism](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/18-plugin-mechanism.md)
- [Supply-chain security](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/19-supply-chain-security.md)
- [Commit provenance](https://github.com/awslabs/aidlc-workflows/blob/main/docs/reference/20-commit-provenance.md)
- [Harness scopes](https://github.com/awslabs/aidlc-workflows/blob/main/docs/harness-engineering/04-scopes.md)
- [All AI-DLC documentation](https://github.com/awslabs/aidlc-workflows/tree/main/docs)

The recommendation is not to copy these files. The useful ideas are their
explicit contracts, compile-time checks, transaction boundaries, and clear
separation of authored policy from generated runtime state.

## 8. Decision summary

| Proposal | Verdict | Priority | TailTrail-specific outcome |
|---|---|---:|---|
| Cross-artifact compiler/doctor validation | Adopt now | P0 | Invalid plans and drift fail before execution. |
| Stage input/output artifact contracts | Adopt now | P0 | Every stage declares what it consumes, produces, and proves. |
| Event emitter ownership and audit atomicity | Adopt now | P0 | Each event has one responsible producer and mutation cannot outrun audit. |
| Result-validity projection | Adopt now | P0 | “Completed once” is separated from “still valid now.” |
| Route capability policy | Adopt now | P1 | Network, mutation, approval, and project requirements become inspectable data. |
| TailTrail workflow profiles | Adapt now | P1 | A stable user-facing facade over existing templates and lifecycle depth. |
| Sensor/check registry | Adapt now | P1 | Reusable deterministic checks without importing AI-DLC scope semantics. |
| Verification-command receipts | Adopt now | P1 | Approval is tied to the exact command and context that ran. |
| Unified question ritual | Adapt now | P1 | Consistent ambiguity handling while preserving TailTrail question content. |
| Configuration placement and in-flight immutability | Adopt now | P1 | Policy, runtime state, learnings, and generated data stop leaking into one another. |
| Strict-additive rule layers and filename scope | Adapt now | P1 | Extensions can add constraints but cannot silently weaken safeguards. |
| Stage-exit learning rituals | Adopt now | P1 | Existing learning machinery is used at deterministic touchpoints. |
| Deterministic engine/conductor boundary | Adopt now | P1 | Runtime transitions stay mechanical while judgment remains explicit and evidenced. |
| Transaction engine for framework/config mutation | Adapt later | P2 | Multi-file TailTrail configuration changes become rollback-safe. |
| Additive plugin seam | Adapt later | P2 | Policy packs and adapters can extend without forks or silent overrides. |
| Deterministic recovery packet | Adopt later | P2 | Resume depends on artifacts and events, not chat memory. |
| Coverage registry and ratchet | Adopt later | P2 | Registry claims are checked against real tests and features. |
| Provenance trust ladder | Defer | P3 | Integrity now; authenticity only at a real trust boundary. |
| Agent/persona or swarm model | Refuse | — | TailTrail remains capability- and evidence-oriented. |

## 9. Detailed implementation dossiers

### 9.1 Cross-artifact compiler and `doctor` validator

**Problem.** TailTrail has individually fingerprinted artifacts, but an
artifact can be internally valid while disagreeing with another artifact.
Examples include a plan referencing an unknown adapter, a threshold changing
after approval, or a stage claiming evidence that its adapter cannot emit.

**Proposed design.** Add one read-only validation service used by both plan
compilation and `doctor`. It should load a normalized snapshot of the active
workflow definition and validate relationships, not just JSON shape.

Minimum checks:

1. Every template and stage ID is unique and stable.
2. Every stage adapter exists and declares the capabilities required by the
   stage.
3. Every produced artifact type has exactly one canonical producer unless it
   is explicitly declared mergeable.
4. Every consumed artifact is produced by an earlier stage or supplied as a
   workflow input.
5. Every blocking check ID exists in the check registry.
6. Every stage result event has a registered emitter owner.
7. Plan policy, threshold, scope, and approval fingerprints match the inputs
   used to compile the plan.
8. Generated projections reproduce byte-for-byte from canonical inputs.
9. Registry-referenced test files and implementation paths exist.
10. Unknown fields are either rejected or explicitly namespaced for extension;
    they must not be silently ignored.

Illustrative output:

```json
{
  "type": "tailtrail-contract-validation",
  "status": "blocked",
  "checked_fingerprint": "sha256:...",
  "issues": [
    {
      "code": "unknown-stage-check",
      "path": "templates.delivery.stages[4].checks[0]",
      "value": "security-scan",
      "severity": "blocking",
      "remediation": "register the check or remove the reference"
    }
  ]
}
```

**Integration points.** Keep pure validation logic near
`scripts/workflow_runtime/compiler.py`; expose it through the existing command
surface rather than creating a separate daemon. Compilation should call it
before saving a plan. `doctor` should call the same function against all
registered definitions.

**Failure behavior.** Validation is read-only and fail-closed. It must report
all independent issues in deterministic order, never repair files implicitly,
and never replace an approved fingerprint on the user's behalf.

**Incremental delivery.** First validate template, adapter, and stage
references. Next add artifact producer/consumer validation. Then add generated
output byte comparison and registry coverage. Each increment should extend the
same issue schema.

**Acceptance checks.** A focused test should intentionally introduce an
unknown adapter, duplicate producer, stale fingerprint, and nondeterministic
ordering. Each case must block with a stable issue code. Running the validator
twice on unchanged input must produce identical bytes.

**Non-goal.** This is not a general JSON-schema framework and should not become
an auto-fixer.

### 9.2 Stage input/output artifact contracts

**Problem.** TailTrail templates define order and prerequisites, but the data
flow between stages is less explicit than the control flow. AI-DLC's stage and
artifact vocabulary shows the value of treating stage inputs and outputs as a
compile-time contract.

**Proposed design.** Enrich each TailTrail stage declaration with a small,
TailTrail-owned contract:

```json
{
  "stage_id": "implementation",
  "consumes": [
    {"artifact": "planning-lock", "required": true, "freshness": "current"},
    {"artifact": "scope-evidence", "required": true, "freshness": "current"}
  ],
  "produces": [
    {"artifact": "source-change-receipt", "cardinality": "one-or-more"}
  ],
  "checks": ["allowed-paths", "source-change-present"],
  "required_capabilities": ["workspace-read", "workspace-write"],
  "completion_policy": "all-required-outputs-valid"
}
```

The names above are examples, not a final schema. Keep the vocabulary small:
planning decisions, scope evidence, approvals, execution evidence, validation
receipts, completion receipts, and recovery/correction artifacts.

**Artifact registry.** Each artifact type should declare its schema version,
canonical producer, consumers, fingerprint fields, freshness dependencies,
and whether multiple producers may merge it. Renames after the vocabulary is
public should be treated as breaking changes; additions can be compatible.

**Workspace-change guard.** A construction stage must not complete merely
because documentation artifacts exist. If the approved task requires source
mutation, completion requires an allowed-path source change receipt tied to
the current scope fingerprint. Documentation-only tasks can explicitly opt
out through a compiled task classification, never by an adapter deciding late.

**Integration points.** Start in `scripts/workflow_runtime/templates.py` and
`adapter_catalog.py`; let the compiler resolve artifact dependencies into the
existing plan. Store actual stage results in the current event journal rather
than in a new artifact database.

**Acceptance checks.** Compilation must reject missing producers, later-stage
producers, unregistered artifact names, incompatible adapter capabilities, and
two exclusive producers. A documentation-only workflow and a code-change
workflow should demonstrate the source-change guard in opposite directions.

### 9.3 Event emitter ownership and audit-first atomicity

**Problem.** `scripts/run-ledger.py` centrally lists event names, but a central
name list alone does not establish who may emit each event or whether the audit
record and state mutation have one transaction boundary.

**Proposed design.** Add an event contract registry with:

- event type and schema version;
- one owning service/module;
- permitted command or adapter emitters;
- whether it precedes, follows, or atomically accompanies mutation;
- idempotency key rules;
- projection handlers that consume it;
- redaction classification for payload fields.

Illustrative entry:

```json
{
  "event_type": "workflow_stage_result_recorded",
  "owner": "workflow-runtime",
  "emitters": ["stage-result-recorder"],
  "mutation_order": "audit-before-projection",
  "idempotency_key": ["workflow_id", "stage_id", "attempt", "result_hash"],
  "sensitive_fields": []
}
```

The storage layer, not arbitrary callers, should construct envelope fields
such as sequence, previous hash, timestamp, and event hash. Callers provide a
typed intent payload; they should not be able to forge journal metadata.

**Atomicity policy.** For journal-backed state, append the durable event first
and rebuild/update the projection from it. For multi-file framework changes,
use the transaction design in Section 9.13. Application source edits remain
ordinary workspace changes and are not forced through this machinery.

**Drift guard.** Validate both directions: every registered event must have an
owner and test; every emitted event literal must exist in the registry. This
prevents unused declarations and undeclared emitters.

**Acceptance checks.** Simulated failure between event append and projection
write must recover through replay. Duplicate idempotency keys must not create a
second logical transition. An unauthorized emitter must fail before journal or
projection mutation.

### 9.4 Result validity as a projection, separate from completion

**Problem.** A stage may have completed successfully and later become stale
because source, policy, approval, dependency, or command inputs changed. A
single `completed` flag cannot represent both history and present validity.

**Proposed design.** Preserve immutable completion history, then derive current
validity:

```json
{
  "stage_id": "validation",
  "completion": {"status": "completed", "event_sequence": 84},
  "validity": {
    "status": "stale",
    "reasons": ["source-fingerprint-changed"],
    "evaluated_at_sequence": 91,
    "required_action": "rerun-stage"
  }
}
```

Suggested validity reasons include source drift, scope drift, policy drift,
approval expiry, command drift, upstream-artifact invalidation, adapter-version
change, and missing evidence. The projection should compute these reasons from
recorded fingerprints; it must not rewrite the original completion event.

**Propagation.** Invalidating one artifact should invalidate only downstream
stages that consume it. Avoid resetting the whole workflow. The compiler's
artifact dependency graph provides the affected subgraph deterministically.

**UX rule.** Display both facts: “completed at event 84” and “currently stale
because source changed.” Do not collapse this to “failed,” which loses history,
or “completed,” which overstates present confidence.

**Acceptance checks.** Tests should change each fingerprint class separately,
prove only dependent stages become stale, and prove restoring an exact prior
input can revalidate without inventing a second completion event.

### 9.5 Route capability and authority policy

**Problem.** Context routing answers what guidance a route receives, but a
strong runtime also needs a declarative answer to what that route may do.

**Proposed design.** Extend route metadata with an auditable capability policy:

```json
{
  "route": "qa",
  "project_required": true,
  "mutation_scope": "workspace-only",
  "network": "approval-required",
  "destructive_actions": "prohibited",
  "requires_stage_approval": false,
  "allowed_artifacts": ["validation-receipt", "failure-evidence"],
  "context_modules": ["testing", "evidence", "failure-handling"]
}
```

The policy should distinguish read, workspace mutation, external mutation,
network, dependency change, destructive action, and approval authority. It
must never claim to enforce host permissions it cannot actually control; where
enforcement is external, report the rule as a required precondition and record
the host decision.

**Conditional context.** Use the same route record to select the minimum
relevant context modules. This borrows AI-DLC's conditional stage modules but
keeps TailTrail's route model and avoids role/persona proliferation.

**Acceptance checks.** Every registered route needs a capability declaration.
Unknown capabilities block compilation. A route that lacks dependency-change
authority must be unable to produce a dependency approval receipt.

### 9.6 TailTrail workflow profiles

**Problem.** AI-DLC profiles give users a compact way to select rigor without
manually choosing every stage. TailTrail already has templates and lifecycle
depth, so copying AI-DLC profile names or semantics would create a competing
model.

**Proposed design.** A TailTrail profile is a stable, user-facing policy bundle
that resolves to an existing template, lifecycle depth, checks, approval
points, and evidence minimums.

Recommended initial profiles:

| TailTrail profile | Typical work | Template/depth intent | Important behavior |
|---|---|---|---|
| `focused` | Small, well-bounded change | `small-change` + minimal | Still requires scope evidence and focused validation; fewer checkpoints, not fewer safeguards. |
| `delivery` | Normal feature/fix | `delivery` + standard | Planning, implementation, validation, completion evidence. |
| `assured` | Security, migration, risky or broad work | `risk-sensitive` + comprehensive | Stronger approval, negative-path evidence, recovery and release checks. |
| `review` | Read-only assessment | `review-only` | Must not silently gain write authority. |
| `discovery` | Repository understanding | `repository-discovery` | Produces evidence and recommendations, not implementation approval. |
| `debug` | Reproduction and root-cause work | `debug-investigation` | Separates proven cause from proposed correction. |

Resolution should be deterministic and recorded:

```json
{
  "requested_profile": "delivery",
  "resolved_template": "delivery",
  "resolved_depth": "standard",
  "policy_escalations": ["dependency-change"],
  "effective_profile": "delivery+dependency-gate",
  "resolution_fingerprint": "sha256:..."
}
```

**Escalation rule.** Risk evidence may increase rigor but never silently lower
it. If a user requests `focused` and the compiler detects a restricted folder,
dependency mutation, broad ownership impact, or release operation, it should
propose the higher profile and require approval where authority changes.

**Compatibility rule.** Existing template IDs remain canonical internal IDs.
Profiles are a facade, not a migration that renames stored plans.

**Acceptance checks.** The same inputs must always resolve to the same profile.
Tests must cover every escalation trigger, ensure read-only profiles cannot
write, and prove an explicit higher-rigor request is never downgraded.

### 9.7 Sensor/check registry

**Problem.** Checks embedded directly in stages are hard to list, reuse,
version, and audit. AI-DLC's pull-authored sensor model is useful, but TailTrail
should keep its own evidence and gate semantics.

**Proposed design.** Define deterministic checks as data with a narrow runner:

```json
{
  "id": "source-change-present",
  "version": "1",
  "runner": "builtin",
  "fire_on": ["stage-gate"],
  "severity": "blocking",
  "inputs": ["approved-scope", "workspace-diff"],
  "timeout_seconds": 10,
  "success_contract": "at-least-one-approved-source-path-changed"
}
```

Use built-in Python functions for checks that need structured data. External
commands should be reserved for project validation and must use the receipt
model in Section 9.8. Do not store shell fragments in general policy when a
typed built-in check is possible.

Checks need stable IDs, explicit versions, deterministic ordering, advisory or
blocking severity, bounded runtime, structured results, and a declared trigger
such as compile, write, stage gate, completion, or release.

**Security.** Registry extensions are code or command authority. Project-local
checks must not become trusted merely because a JSON file names them. Require
the existing approval and capability boundary before executing an external
check, and record the exact resolved executable/arguments.

**Acceptance checks.** Unknown check IDs block compilation. Advisory failures
remain visible without blocking. Blocking failures prevent the transition.
Timeout and malformed result cases fail closed with stable error codes.

### 9.8 Verification-command receipts

**Problem.** A generic statement that validation ran is weaker than evidence
of the exact approved command, context, inputs, and result.

**Proposed design.** Split the record into an approval intent and execution
receipt:

```json
{
  "approval": {
    "command_argv": ["python3", "-m", "unittest", "tests.test_example"],
    "command_hash": "sha256:...",
    "working_directory": "project-relative/path",
    "environment_allowlist_hash": "sha256:...",
    "scope_fingerprint": "sha256:..."
  },
  "execution": {
    "started_at": "...",
    "exit_code": 0,
    "stdout_digest": "sha256:...",
    "stderr_digest": "sha256:...",
    "duration_ms": 1234,
    "runner_identity": "local-host"
  }
}
```

Store argv as an array, not an interpolated shell string. Cap command and
captured-output sizes, redact secrets, and retain digests when raw output is too
large or sensitive. Record relevant environment names and fingerprints, not
secret values.

If the command, working directory, scope, or allowed environment changes after
approval, the approval no longer authorizes execution. A failed command still
gets a receipt; failure evidence must never disappear because it did not pass.

**Acceptance checks.** Changing one argument changes the command hash. A
receipt cannot attach to a different scope fingerprint. Secrets in configured
environment fields are redacted. Non-zero exit, timeout, signal, and missing
executable are all distinct structured results.

### 9.9 Unified question and confirmation ritual

**Problem.** TailTrail has several question flows with similar intent but
different batching, confirmation, and stop behavior. Inconsistent rituals
increase ambiguity and make approvals hard to compare.

**Proposed design.** Create one question envelope while preserving the
domain-specific content of planning, scope, and official AI-DLC questions.

Each batch records:

- question ID, reason, and decision affected;
- evidence already inspected;
- two recommended mutually exclusive options, adding a third only when real;
- default/recommendation with its tradeoff;
- exact user response, including free-form text;
- normalized interpretation proposed by TailTrail;
- user confirmation of that interpretation;
- revisions and rejection count;
- final status: confirmed, explicitly accepted as-is, deferred, or blocked.

Keep batches small (normally no more than four questions and four choices per
question). After repeated rejection, offer “record my answer as-is” rather
than endlessly paraphrasing. This is not auto-approval: the verbatim response
and explicit acceptance become the decision artifact.

**Authorization lineage.** Later plans and receipts should reference the
confirmed question-answer fingerprint. If a material answer changes, derived
approvals become stale through the validity projection.

**Acceptance checks.** No unanswered required question can be normalized as an
approval. Free-form answers round-trip verbatim. Revisions retain history.
Changing an approved material answer invalidates only dependent decisions.

### 9.10 Configuration placement and in-flight immutability

**Problem.** AI-DLC's plane architecture highlights a useful distinction:
who authors data and how long it lives. Without an explicit placement rule,
policy, generated state, project memory, and per-run decisions can leak into
one another.

**Proposed matrix.** TailTrail should classify every durable file or record:

| | Continuous across runs | Frozen for one run |
|---|---|---|
| Framework/team-authored | stage definitions, route capabilities, check registry, policy defaults | compiled effective policy and profile snapshot |
| Project/user-authored | active project policy, approved durable learnings | planning lock, approved scope, question answers, command approvals |
| Runtime-generated | append-only learning candidates and compatibility metadata | events, projections, receipts, correction packets, recovery packet |

Generated state must not overwrite authored policy. A run compiles an
effective immutable snapshot; later changes create a rebase proposal or affect
the next run. They do not silently change the meaning of a live workflow.

**Fingerprinting.** The compiled plan should record the fingerprints of every
continuous input it used. At a transition, compare current fingerprints with
the frozen snapshot and route drift through the validity/rebase mechanism.

**Acceptance checks.** Editing policy mid-run does not silently change the
active plan. A subsequent run sees the new policy. Explicit rebase records old
and new fingerprints and identifies which approvals must be renewed.

### 9.11 Strict-additive rule layers and filename-scoped policies

**Problem.** Override precedence makes the final policy hard to explain and
allows an extension loaded later to weaken an earlier safeguard. AI-DLC's
additive rule model is a useful default because it makes contributions monotonic.

**Proposed design.** Separate three operations explicitly:

- **add:** introduce a new rule or additional constraint;
- **refine:** make an existing rule more restrictive within its declared
  extension contract;
- **replace/remove:** a governed migration that requires compatibility review
  and explicit approval, never normal layering behavior.

Ordinary project, team, plugin, or route layers may add or refine only. If two
rules overlap, both apply. If they cannot both be satisfied, compilation reports
a policy conflict; load order must not decide the winner.

Where practical, derive scope from stable placement or filename conventions so
the rule's applicability is inspectable without executing code. A possible
layout is illustrative:

```text
policy/
  global/*.json
  routes/qa/*.json
  profiles/assured/*.json
  stages/validation/*.json
```

The directory/filename supplies declared scope, while the file content supplies
the rule. The validator must confirm they agree and reject an embedded scope
that tries to escape its placement.

**Expiry and ownership.** Temporary exceptions and project learnings need an
owner, justification, `review_after` or `stale_after` date, and replacement
path. Expiry does not silently delete a rule: it creates a blocking or advisory
review state according to policy. Core safeguards should not support expiry.

**Conflict explanation.** The compiled policy should show every contributing
rule, source file, version, resulting constraint, and conflict. This makes
“why is this blocked?” answerable without knowing merge order.

**Acceptance checks.** Reversing layer load order must produce identical
effective policy. A plugin that attempts to remove a blocking rule must fail.
Expired temporary rules must become visible. Filename/content scope mismatch
must block compilation.

### 9.12 Stage-exit learning rituals

**Problem.** TailTrail's learning system is already richer than the upstream
diary model, but sophistication does not guarantee consistent use.

**Proposed design.** Add three deterministic touchpoints:

1. **Start:** retrieve only applicable approved learnings and record whether
   each was used, rejected, or irrelevant.
2. **Stage exit:** ask whether a durable, non-sensitive fact would prevent
   repeated discovery or error. Default to no candidate; do not create noise.
3. **Closure:** reconcile candidates, evidence, outcome, expiry, ownership, and
   promotion status.

Candidates should remain quarantined until supported and approved. Every
durable learning needs source evidence, scope, confidence, owner, creation
date, review/expiry date, and supersession link. Negative learning (“this
approach is unsafe here”) should be first-class but never weaken an explicit
project or safety policy.

Learnings approved during a run apply to the next run unless an explicit plan
rebase is approved. This preserves reproducibility.

**Acceptance checks.** A candidate cannot become active from repetition alone.
Expired learnings are excluded or flagged according to policy. Retrieval logs
attribution. A learning that conflicts with active policy is rejected, not
merged by precedence tricks.

### 9.13 Transaction engine for framework/config mutations

**Problem.** Plugin installation, registry changes, profile updates, or policy
pack application may touch several files. Per-file atomic writes do not make a
multi-file operation atomic.

**Proposed design.** Use a small transaction protocol only for TailTrail-owned
framework/configuration mutations:

1. Resolve and validate all targets; reject paths outside allowed roots.
2. Capture precondition hashes and a recovery manifest.
3. Stage new files in a temporary directory on the same filesystem.
4. Run schema, cross-artifact, and compatibility validation on the staged view.
5. Acquire a bounded lock.
6. Verify precondition hashes still match.
7. Replace files deterministically, recording each completed step.
8. Re-run validation and emit a completion receipt.
9. On failure, restore from the manifest and record rollback status.

Do not route ordinary application edits through this engine; Git and the
workspace remain the appropriate change/review mechanism for user code.

**Crash recovery.** A transaction journal must distinguish prepared,
committing, committed, rolling-back, and recovery-required. A later `doctor`
run should detect an incomplete transaction and offer an explicit recovery
action rather than guessing.

**Acceptance checks.** Inject failure after each commit step and verify either
the old or new consistent state is recoverable. Concurrent precondition drift
must abort before replacement. Path traversal and symlink escape must fail
closed.

### 9.14 Additive plugin seam

**Problem.** Teams need to add policy packs, checks, and host adapters without
forking TailTrail. Traditional override-based plugins make final behavior hard
to explain and can recreate launcher/version skew.

**Proposed design.** Limit plugins to explicitly declared contribution points:

- new route definitions or context modules;
- new checks using an approved runner type;
- new adapter definitions;
- additive policy rules;
- documentation fragments at named sentinels.

No plugin may replace core safety rules, remove an existing blocking check, or
write arbitrary files. Contributions use stable IDs, declared compatibility,
content hashes, and deterministic merge ordering. ID collisions fail unless a
specific mergeable contract exists.

Each installation gets a provenance sidecar containing source, resolved
version/commit, content digest, declared contributions, compatibility result,
and install transaction receipt. `doctor` validates both the plugin and the
effective merged result.

**When to implement.** Wait until at least two real extensions would otherwise
fork the same core surface. Before then, keep a documented internal registry;
premature marketplace/discovery/signing work would violate smallest-change
discipline.

**Acceptance checks.** Applying the same plugin twice is idempotent. Removing
it removes only attributed contributions. A plugin cannot weaken an existing
rule. Two plugins with conflicting exclusive producers block deterministically.

### 9.15 Deterministic recovery packet

**Problem.** Resume must not depend on the model remembering a conversation.
TailTrail has durable events and projections; the remaining opportunity is a
small, explicit recovery read order and packet.

**Proposed design.** Generate a derived, replaceable recovery packet containing:

- workflow/run identity and active plan fingerprint;
- last durable event and verified journal hash;
- current stage plus completed/currently-valid distinction;
- unresolved required questions and approvals;
- active scope and allowed mutation paths;
- failed/blocked checks and correction packet links;
- exact next permitted transitions;
- relevant evidence/receipt references;
- continuous-input drift detected since suspension.

The packet is a projection, never canonical state. It must rebuild from the
compiled plan, journal, and artifacts. Resume first verifies those sources,
then uses the packet for efficient context loading.

**Acceptance checks.** Delete the packet and reproduce identical content from
canonical inputs. Corrupt the journal chain and ensure resume blocks. A stale
packet must be detected by its source fingerprint rather than trusted.

### 9.16 Coverage registry and ratchet

**Problem.** `tailtrail-registry.json` contains valuable feature-to-test
relationships, but a registry can become aspirational unless its claims are
checked against the filesystem and actual executed tests.

**Proposed design.** Add a read-only coverage validator that checks:

- every registered implementation and test path exists;
- every workflow template, adapter, event owner, check, artifact type, and
  route is attributed to at least one feature;
- every P0 contract has positive, negative, replay/recovery, and drift tests;
- deleted or renamed tests cannot leave stale registry claims;
- coverage does not fall below a checked-in baseline without an explicit,
  reviewed baseline update.

Do not infer behavioral coverage solely from filenames. The first version can
validate existence and declarations; later versions may ingest structured test
receipts. Keep the ratchet deterministic and explain every uncovered item.

**Acceptance checks.** A missing test path, unregistered stage, or reduced P0
test category must fail with a precise feature ID. Adding an unrelated feature
must not reorder the whole report.

### 9.17 Integrity and provenance trust ladder

**Problem.** Hashes prove integrity relative to recorded bytes; they do not
prove who created an artifact. AI-DLC's provenance work is useful when
artifacts cross a real trust boundary, but signing everything locally would add
cost without improving the local threat model.

**Proposed ladder.** Make the trust level explicit:

1. **Recorded:** identity, timestamp, and content stored without integrity
   proof.
2. **Integrity:** content hash and hash-chain/replay verification.
3. **Reproducible:** canonical inputs and tool version reproduce the output.
4. **Authenticated:** CI/service identity signs an attestation.
5. **Policy-verified:** trusted identity, protected environment, and policy
   checks are verified at release consumption time.

TailTrail should target levels 2–3 locally using mechanisms it largely already
has. Levels 4–5 should be added only for CI, remote handoff, release, regulated
evidence, or multi-host execution. A signature must not be presented as proof
that the underlying decision was correct.

**Acceptance checks.** Every receipt states its trust level. Verification
distinguishes corrupted, unverifiable, unsigned, authenticated, and policy-
rejected states. Missing optional signing infrastructure must not break the
local workflow when only integrity was required.

### 9.18 Deterministic engine and judgment-bearing conductor boundary

**Problem.** A runtime becomes difficult to test when transition mechanics and
open-ended reasoning are mixed. Conversely, a purely mechanical engine cannot
decide ambiguous requirements, interpret repository evidence, or ask the user
for authority.

**Proposed design.** Name the boundary without rearchitecting the existing
runtime:

- The **engine** validates event schemas, checks preconditions, calculates
  allowed transitions, appends events, rebuilds projections, verifies hashes,
  evaluates registered deterministic checks, and refuses invalid mutations.
- The **conductor** gathers evidence, selects among engine-offered actions,
  drafts questions and proposals, explains tradeoffs, and requests approvals.
- The **user/host boundary** grants authority and executes capabilities that
  TailTrail itself cannot safely or truthfully claim.

The conductor may propose a transition but should not construct raw state or
bypass the engine. The engine may report ambiguity but should not invent the
missing intent. Every conductor decision passed to the engine references the
evidence and confirmation fingerprint that supports it.

**Machine-readable transition response.** Given the same compiled plan,
journal, and current artifacts, the engine should return the same ordered set
of allowed actions and blocking reasons:

```json
{
  "current_stage": "validation",
  "allowed": ["record-check-result"],
  "blocked": [
    {
      "transition": "complete-stage",
      "reason": "blocking-check-incomplete",
      "check_id": "focused-tests"
    }
  ],
  "state_fingerprint": "sha256:..."
}
```

**In-flight learning rule.** New reasoning, policy, or learning may cause the
conductor to propose a rebase, correction, or next-run change; it must not
mutate engine rules underneath the current state fingerprint.

**Acceptance checks.** Transition calculation must be deterministic and pure.
An attempted direct projection mutation must not survive replay. Repeating a
conductor proposal with a stale state fingerprint must be rejected and
re-evaluated against current state.

## 10. Architecture-derived improvements beyond the original shortlist

The deeper architecture references add several important ideas that are easy
to miss when reading only the workflow-profile guide.

### 10.1 Keep two graph views, but only one source of truth

TailTrail already has the pieces for two useful views:

- a stable compiled control plan: stages, dependencies, capabilities, gates;
- a mutable derived execution projection: attempts, results, validity,
  retries, and current position.

The plan should never be rewritten merely because execution advanced. The
projection should never become authority for what the plan originally allowed.
Cross-validation should prove every projected stage and transition belongs to
the plan. This gets the value of AI-DLC's runtime graph without adding another
canonical graph format.

### 10.2 Separate stage completion, output lineage, and authorization

A stage output is trustworthy only when three lines connect:

1. the stage was authorized under a specific plan/scope/approval fingerprint;
2. the output was produced by the registered adapter/check/command;
3. the output still validates against its upstream artifacts and current
   policy snapshot.

Receipts should carry these references. This prevents a valid-looking artifact
from being attached to the wrong run or reused after its authority changed.

### 10.3 Make artifact naming a compatibility surface

Once external policy packs or adapters consume artifact IDs, names become API.
Use additive changes for compatible releases. Deprecations require an alias or
migration period. Renames/removals need an explicit major compatibility event
and a validator that identifies affected consumers.

### 10.4 Compile only the context needed for the stage

AI-DLC's conditional modules reinforce TailTrail's existing context routes.
The compiler should resolve a context manifest from stage, route, profile,
risk, and active policy. The runtime loads that manifest and records its
fingerprint. This makes context selection deterministic and debuggable while
keeping role/persona systems out.

Example:

```json
{
  "stage_id": "validation",
  "context_modules": [
    "project-policy",
    "approved-scope",
    "validation-contract",
    "relevant-learnings"
  ],
  "excluded_reason": {
    "release-policy": "not a release workflow"
  },
  "context_fingerprint": "sha256:..."
}
```

### 10.5 Use explicit placement and authority for generated outputs

Generated reports and recovery packets are useful caches, not policy. Their
headers should identify canonical inputs, generator version, fingerprint, and
regeneration command. Hand edits either fail validation or are clearly placed
in a separate authored overlay. This eliminates ambiguous half-generated files.

## 11. Recommended delivery roadmap

Each phase should be its own reviewable implementation run. Do not combine all
items into one rewrite.

### Phase 0 — Baseline and naming freeze

- Inventory current templates, stages, adapters, routes, event types, artifact
  names, and registry mappings.
- Decide canonical IDs and mark experimental IDs explicitly.
- Add characterization tests for compiler determinism and journal replay before
  changing schemas.
- Produce no runtime behavior change beyond missing-reference diagnostics.

**Exit evidence:** checked-in inventory, deterministic baseline receipts, and
documented compatibility rules.

### Phase 1 — Contract validator (P0)

- Implement the shared cross-artifact validation service.
- Validate templates, stages, adapters, routes, and event references.
- Integrate it into compilation and `doctor`.
- Return deterministic structured issue codes.

**Exit evidence:** negative fixtures for each reference error, repeatability
test, and proof that validation mutates no workflow state.

### Phase 2 — Artifact data flow and validity (P0)

- Add stage consumes/produces declarations and artifact registry.
- Compile the data-flow graph and reject missing/multiple producers.
- Add completion-versus-validity projection and targeted invalidation.
- Add the source-change guard for mutation-required tasks.

**Exit evidence:** dependency graph fixtures, drift tests, and replay proof.

### Phase 3 — Audit ownership and exact receipts (P0/P1)

- Define event emitter ownership.
- Move envelope construction fully into the storage boundary.
- Add idempotency rules and bidirectional registry/emitter checks.
- Add exact verification-command approval and execution receipts.

**Exit evidence:** failure-injection recovery, unauthorized-emitter tests,
redaction tests, and duplicate-event tests.

### Phase 4 — Profiles, routes, and checks (P1)

- Add the TailTrail profile facade over existing templates/depth.
- Add route capability declarations and context manifests.
- Introduce the typed check registry and migrate one gate at a time.
- Preserve existing CLI/template compatibility.

**Exit evidence:** complete profile resolution matrix, escalation tests,
capability-denial tests, and advisory/blocking check behavior.

### Phase 5 — Human decisions and learning rituals (P1)

- Unify question envelopes and confirmation receipts.
- Propagate question/approval fingerprints into plans and outputs.
- Add learning retrieval at start and candidate reconciliation at stage exit
  and closure.
- Enforce next-run-only activation unless a rebase is approved.

**Exit evidence:** verbatim round-trip tests, revision history tests,
authorization-lineage invalidation, and learning-conflict tests.

### Phase 6 — Distribution and operational maturity (P2/P3)

- Build the framework/config transaction engine when a real multi-file
  mutation requires it.
- Add the plugin seam when two real extensions need the same stable surface.
- Add deterministic recovery packets and coverage ratchet.
- Add authenticated provenance only at the first real cross-host/CI/release
  trust boundary.

**Exit evidence:** crash-injection rollback, plugin idempotency/removal,
packet regeneration, coverage-baseline enforcement, and trust-level verification.

## 12. Cross-feature validation matrix

| Failure or risk | Validator | Artifact contracts | Validity projection | Audit/receipts | Profile/route policy | Recovery |
|---|---:|---:|---:|---:|---:|---:|
| Unknown stage/adapter/check | ✓ | ✓ |  |  | ✓ |  |
| Wrong or missing stage output | ✓ | ✓ | ✓ | ✓ |  | ✓ |
| Source/policy changes after validation | ✓ | ✓ | ✓ | ✓ |  | ✓ |
| Command differs from approval |  |  | ✓ | ✓ | ✓ | ✓ |
| Unauthorized route mutation | ✓ |  |  | ✓ | ✓ | ✓ |
| Event appended twice | ✓ |  |  | ✓ |  | ✓ |
| Projection write fails |  |  | ✓ | ✓ |  | ✓ |
| Generated report hand-edited | ✓ |  | ✓ | ✓ |  | ✓ |
| Learning changes a live plan | ✓ |  | ✓ | ✓ | ✓ | ✓ |
| Plugin weakens a core safeguard | ✓ | ✓ |  | ✓ | ✓ |  |

The matrix is intentionally overlapping. High-value invariants should be
checked at compile time and at the mutation boundary, with replay/recovery as a
third defense where durable state is involved.

## 13. Review checklist for each implementation proposal

Before approving any dossier above, answer:

1. Which concrete failure does this prevent in the current TailTrail design?
2. Is there an existing helper, registry, journal, projection, or command that
   should own it?
3. What is canonical state, and what is only a generated view or cache?
4. Which exact fingerprint binds the decision, authority, input, and output?
5. Does failure happen before mutation, and is recovery deterministic?
6. Can the feature silently broaden scope, lower rigor, or upgrade authority?
7. What sensitive information may appear in events, receipts, or commands, and
   how is it redacted?
8. What is the smallest negative test that proves fail-closed behavior?
9. What compatibility promise applies to IDs, schemas, events, and artifacts?
10. Is this needed by a real workflow now, or is it speculative machinery?

## 14. Explicit non-goals and identity safeguards

The following remain outside this adoption plan:

- no copy of AI-DLC's persona roster, swarm topology, or organization model;
- no replacement of repository-derived ownership with declared scope files;
- no silent profile escalation that grants new write or external authority;
- no policy override precedence where a later layer can remove a safeguard;
- no second canonical event store, workflow state machine, or artifact database;
- no automatic promotion of learning candidates;
- no signing/attestation infrastructure without a real trust-boundary consumer;
- no plugin marketplace before a stable, constrained extension contract exists;
- no transaction wrapper around ordinary source-code edits;
- no claim that more stages automatically means more assurance.

The intended result is recognizably TailTrail: repository evidence determines
scope, questions fail closed, approval determines authority, reasoning remains
durable, and every mechanism earns its complexity by preventing a demonstrated
failure class.
