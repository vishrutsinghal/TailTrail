# AIDLC Upstream Improvement Plan (TailTrail)

- Date: 2026-09-26. Status: DISCUSSION DRAFT — nothing here is approved or implemented.
- Upstream source: `awslabs/aidlc-workflows` v2.10.0 (local copy at `Downloads/aidlc-workflows-main`, outside repo).
- Local projection: `.tailtrail/official-aidlc` v1.0.1 (35 files: rules + rule-details only; no engine, hooks, sensors, memory, scopes, agents, skills, plugins).
- Parent session context: Navigator graph-packet stages 0a–6, compiler content pinning + rebase, ownership drift split + rebind, scope-answer channel, interpretation scaffold, conversation-safe intake, thin-evidence gate — all pushed to `vis/tailtrail_v2` September 2026.
- How to resume: pick one item below, open a `tailtrail start` with its goal line, resolve scope, get `approve`, implement per its acceptance list.

## Standing principle (do not trade away)

TailTrail leads upstream in evidence cryptography: content-pinned compiler plans
(`scripts/workflow_runtime/compiler.py`), CRLF-normalized scope hashing, fingerprint-bound
host-scope proposals (`navigator_scope.validate_host_proposal` / `record_host_proposal`),
ownership rebind baselines (`scripts/workflow_runtime/ownership.py`), thin-evidence gate
(`navigator_scope._thin_owner_evidence`). Upstream hashes are audit trails, not decision
fingerprints. Every item below must compose with — never weaken — that property.

## Feature map (upstream → TailTrail → verdict)

| Upstream (v2.10.0) | TailTrail analogue | Verdict |
|---|---|---|
| 33 stages / 5 phases, scope-selected (classic/enterprise/feature/…) | Guided delivery + DWR templates + Lite/Standard/Full | Behind on breadth, ahead on exactness |
| Prose gates + hook-enforced guards (PreToolUse exit-2) | Planning Lock + approvals + validators | Rough parity, different layer |
| Sensors (deterministic doc checks, OK/GAP/ORPHAN, fail-closed) | Contracts/schemas, fingerprints, freshness | Behind: no standalone sensor runner |
| Attest (`resolve` commit→Units, `anchor` pointers; verified/drifted/unattested) | Nothing (identity/freshness adjacent) | Missing entirely |
| AIDA multi-model review, adversarial passes, review budget, findings ledger | Review stages, Code Review Graph Lite | Behind on review depth |
| Memory 5-layer chain + diary + learnings ritual | Learnings advisory + completion-learning | Behind on persistence |
| Question fences (max 4×4, ≥2 options, built-in Other, verbatim logging) | SCOPE-Q1 / MAT questions + `--scope-owner` channel | Near parity; polish gap |
| Scope-owned ceremony toggles (`--sensors`, `--learnings`, `--summary-confirmation`) | Mode selection only | Missing: per-run ceremony control |
| Intent archive/unarchive; parked attempts restore byte-exactly | Nothing (the "graveyard" burden) | Missing — direct burden fix |
| Plugin overlays (additive stages/sensors, never edits core) | Monolithic scripts per concern | Architectural gap |
| Outcomes pack (`OUTCOMES.md` handover) | completion-report | Near parity; handover artifact nicer |
| Session-cost tracking, replay skill | Local token estimates only | Missing, small |
| 19 session hooks (audit-log, record-human-turn, runtime-integrity, statusline) | session-control + ledger (partial) | Partial; ideas portable |
| One core + thin per-harness shims (7 harnesses) | codex/copilot/claude trichotomy | Behind — root of `--host` friction |

---

## Item 6 — Refresh local pack v1.0.1 → v2.10.0 (do first)

- **Problem.** Ten versions of drift on the rules Standard mode bridges against. Current manifest pins
  official revision v1.0.1 (commit e49341d); upstream is at v2.10.0 with Classic scope v1,
  attest, autonomy grants, archive/unarchive, and ceremony toggles the local pack never saw.
- **Evidence.** `.tailtrail/official-aidlc/manifest.json` + `VERSION`; upstream `CHANGELOG.md`
  2.9.0–2.10.0 entries (Classic v1 flow, `attest resolve/anchor`, intent archive, per-intent ceremony flags).
- **Implementation.**
  1. Replace `.tailtrail/official-aidlc/aws-aidlc-rules` + `aws-aidlc-rule-details` trees from the
     v2.10.0 download; bump `VERSION` + `manifest.json` (keep `source: https://github.com/awslabs/aidlc-workflows`).
  2. Re-run the compatibility check the bridge performs (see `scripts/official-aidlc-bridge.py`
     preflight: file integrity over the manifest) and confirm `compatible`.
  3. Regression: `test_workflow_*official*`, aidlc-bridge suites, plus one Standard-mode Start
     smoke to confirm the bridge still attaches.
- **Acceptance.** Manifest reports v2.10.0 with integrity clean; bridge preflight passes; no test regressions.
- **Risks.** Rule renames may break golden reply fixtures that quote v1.0.1 rule paths — grep tests for
  `aws-aidlc-rule` references first.
- **Size.** Small (read-only tree swap + verification).

## Item 3 — Standalone sensor runner (evidence depth)

- **Problem.** Nothing machine-checks planning artifacts today: required IDs present, sections
  complete, no orphan references. Close-out leans entirely on human review plus schema shape.
- **Evidence.** Upstream `core/sensors/*.md` (traceability, upstream-coverage, required-sections,
  claim-sources; verdicts OK/GAP/ORPHAN/Deferred/N-A, fail-closed on missing IDs) run via
  `engine sensor-*`. Our closest analogues (`contracts.validate_artifact`, freshness checks) validate
  shape and hashes, never cross-reference completeness.
- **Implementation.**
  1. New module `scripts/requirement-sensors.py` (keep the `-`/`_` naming question for plan time;
     check `scripts/` conventions first): pure functions over evidence dicts —
     `traceability(requirements, candidates, edges)`, `sections(document)`, `orphans(...)`,
     each returning `[{check, status: OK|GAP|ORPHAN, detail}]`.
  2. Runner verb `tailtrail requirements sense --root . --run-id <id>` (or under `test`? decide at
     plan time; prefer a read-only verb near `test plan`), exit 2 with named gaps on failure.
  3. Wire into closure readiness (advisory first: report gaps; enforcing later only by explicit decision).
  4. Tests: synthetic evidence docs (reuse `tests/test_navigator_scope.py` fixture style) — gap,
     orphan, and clean cases; CLI smoke.
- **Acceptance.** Sensor run on a healthy evidence doc reports all-OK; doctored docs (dropped ID,
  orphan edge) fail closed naming the gap; close-out readiness can cite a sensor receipt.
- **Risks.** Scope creep into a full harness — hold the line at doc/evidence checks; no execution,
  no providers, no network.
- **Size.** Medium (new module + verb + tests).

## Item 1 — Attest-style provenance (new capability)

- **Problem.** Neither system answers "was *this* commit actually reviewed?" Our fingerprints bind
  plans and scope; upstream's attest binds commits to reviewed Units with
  verified/drifted/unattested/unverifiable/indeterminate/excluded verdicts.
- **Evidence.** Upstream 2.9.0 `attest resolve` (commit/diff range → Units) + `attest anchor`
  (commit pointers in audit trail). Our side: compiler plan fingerprints + `LEDGER.append_event`
  + review records in `scripts/workflow_runtime/` — the raw materials exist, the mapping doesn't.
- **Implementation.**
  1. Read-only verb first: `tailtrail attest resolve --root . --range <base>...<head>` →
     per-commit verdicts against recorded review/approval artifacts (plan fingerprints, approval
     ledger rows, stage results). No writes.
  2. `attest anchor` records commit pointers as ledger events (new `EVENT_TYPES` entries in
     `scripts/run-ledger.py`, following the `workflow_ownership_rebased` precedent).
  3. Verdicts mirror upstream vocabulary so future pack comparison stays aligned.
  4. Tests: synthetic ledger + git fixture (tmp repo with commits) covering verified, drifted
     (amended after review), and unattested.
- **Acceptance.** Resolve on a reviewed-then-amended fixture reports drifted; untouched history
  reports unattested (never a false verified); anchor round-trips through the ledger.
- **Risks.** Git-history dependence (shallow clones, rebases) — verdict `indeterminate` must exist
  and be honest. Read-only first; writes only via anchor.
- **Size.** Medium-large (new verb + ledger types + git plumbing + tests).

## Item 2 — Archive/unarchive + parked-restore (graveyard fix)

- **Problem.** 300+ stale runs, duplicate locks, abandoned Standard locks; all process debt lands
  on the operator with manual `Remove-Item` cleanup. Upstream retires intents without deleting
  audit trails and restores parked attempts byte-exactly.
- **Evidence.** Session history (eval locks, parked Standard run, manual cleanups); upstream 2.9.0
  `intent archive/unarchive`, `intent list --all`, parked-restore semantics.
- **Implementation.**
  1. `tailtrail archive --run-id <id> [--reason]` → moves `.tailtrail/runs/<id>` to an archive root
     (suggest `.tailtrail/archive/`), appends an archive receipt to the run's `events.jsonl`
     *before* moving (audit continuity), refuses active/approved-unclosed locks unless `--force`
     with rationale (force path must itself be ledger-recorded).
  2. `tailtrail unarchive --run-id <id>` restores byte-exactly (verify by comparing a manifest of
     SHA-256 per file written at archive time).
  3. `resolve_run` ignores archived runs unless explicitly addressed (no behavior change for
     explicit `--run-id`).
  4. Tests: archive/unarchive round-trip byte-equality, active-lock refusal, explicit-ID resolution.
- **Acceptance.** Round-trip is byte-exact per manifest; audit trail survives inside the archived
  run; auto-resolution never surfaces archived runs.
- **Risks.** Deletion-adjacent feature — the receipt-before-move + force-rationale rules are load
  bearing. No silent pruning, no TTL auto-delete in v1 (propose only).
- **Size.** Medium (session-control area + ledger receipt + tests).

## Item 4 — Scope-owned ceremony toggles (extension)

- **Problem.** Ceremony is mode-global (Lite/Standard/Full). Upstream lets each intent toggle
  sensors, learnings, and summary confirmation independently — "full ritual where uncertainty
  lives, lightweight where it doesn't," per intent rather than per mode.
- **Evidence.** Upstream 2.9.0 per-intent `--sensors/--learnings/--summary-confirmation` +
  transactional `engine config set`. Our `task-start.py` parser + `aidlc_mode_selection` are
  mode-only.
- **Implementation.**
  1. `--sensors on|off`, `--learnings on|off`, `--summary-confirmation on|off` on Start, recorded
     in the Planning Lock (additive lock fields — check lock schema first; additive only).
  2. Enforcement points read the lock fields: sensor runner (Item 3) skipped when off, learnings
     ritual skipped, summary gate enforced when on.
  3. Defaults mirror current behavior exactly (no change unless flags passed).
  4. Tests: flag parsing, lock persistence, each toggle's skip/enforce path.
- **Acceptance.** Default runs byte-identical to today; each toggle independently skips/enforces
  its ceremony with ledger-visible evidence.
- **Risks.** Flag sprawl — three flags max, no more without a new decision. Lock schema must stay
  backward compatible (additive optional fields only).
- **Size.** Small-medium.

## Item 5 — Question protocol polish (small)

- **Problem.** Our answer channel works but isn't auditable to upstream standard: no option cap
  discipline, no guaranteed Other, no verbatim answer logging.
- **Evidence.** Upstream question fences (max 4×4, ≥2 options, built-in Other, `aidlc-log.ts`
  decision/answer verbatim logging) vs our SCOPE-Q1/MAT rendering + `--scope-owner` answers
  recorded only as normalized proposals.
- **Implementation.**
  1. Cap SCOPE-Q1 options display (already 3 via `SCOPE_QUESTION_OPTION_CAP` — verify against
     packet option_evidence, no change likely needed).
  2. Always append an explicit "Other (provide a different known path)" option row in the
     rendered question (renderer-only; the free-text answer path already accepts it).
  3. Log verbatim answers: extend the recorded host-reasoning entry with the raw answer strings
     (alongside the normalized proposal) — additive fields only, schemas checked first.
  4. Tests: Other-row rendering, verbatim log round-trip, schema validity of extended entries.
- **Acceptance.** Every rendered question shows Other; every answered round persists the raw text;
  quality/proposal schemas still validate.
- **Risks.** Minimal — presentation plus additive log fields.
- **Size.** Small.

## Item 7 — Harness-neutral host identity (structural direction, not started)

- **Problem.** Our codex/copilot/claude trichotomy is tech debt upstream solved with one core +
  thin per-harness shims — it is the root of every `--host` friction hit this session
  (proposal host enum, answer-channel host requirement, launcher identity).
- **Evidence.** Upstream `harness/*/manifest.ts` pattern (core projected verbatim; ~5–10 shim
  files per host); our `resolve_host_identity`, proposal `unsupported-host` errors, and the
  opencode+Spark harness matching none of the three.
- **Direction (no design yet).** Host becomes an open string with capability flags, validated
  where identity actually matters (proposal binding, launcher match) instead of a closed enum
  at every boundary. Explicitly NOT scoped — needs its own investigation run first (blast radius:
  every `host in {...}` check, schemas with host enums, golden fixtures, MCP tool schemas).
- **Size.** Large. Do not start casually.

---

## Suggested order and dependencies

1. Item 6 (pack refresh) — cheap, de-risks Standard mode; no dependencies.
2. Items 3 + 1 (sensors, attest) — evidence depth; our comparative advantage doubled down. Independent of each other; both read-only first.
3. Item 2 (archive) — graveyard; independent.
4. Items 4 + 5 (ceremony toggles, question polish) — small, independent.
5. Item 7 (host identity) — standing direction only.

## Open questions for discussion

- Should sensor verdicts gate `close` (enforcing) or stay advisory receipts in v1?
- Does attest `verified` require human-held review records only, or do agent-executed approvals count?
- Archive: is `--force` on active locks acceptable at all, or should active locks be unarchivable, period?
- For ceremony toggles: which three ceremonies exactly (mirror upstream names or TailTrail-native names)?
