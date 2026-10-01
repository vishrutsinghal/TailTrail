# Session Work Phases — Full Detail

- Date: 2026-09-27. Status: PLAN — nothing below is approved or implemented except Phase 0 (shipped).
- Parent evidence: `aidlc-docs/dry-run-evidence-log.md` (DR1–DR5), session pushes `c7a2782` → `0597912` on `vis/tailtrail_v2`.
- Convention: each item lists problem, evidence, design, files, tests, acceptance, risks, size. Open a `tailtrail start` per item (or per phase where stated), resolve scope, get `approve`, implement, regress, report, push on instruction.

## Phase 0 — Shipped (context, no work)

Compiler content pinning + rebase; ownership drift split + rebind; scope-answer channel + bounded dialogue; interpretation scaffold + dry-run + shim + resolve-uncertain; conversation-safe intake; thin/deep gates; packet identity split + superseded-v2; QA seed resolution; archive verbs; mode breadth + `--from-run`; CI fixture + stamp fixes. All pushed. Dry runs DR1–DR5 logged (DR3 partial).

---

## Phase 1 — Correctness gaps (execute first, in the given order)

### 1.4 Launcher-skew warning (do first: smallest, unblocks debugging honesty)

- **Problem.** The `tailtrail` launcher silently runs stale installed code (`D:\PD\venvs\...`) while the checkout moves on. Burned two debugging sessions this session (a QA approval failure misread as a product bug; one eval misfire). Any developer comparing launcher vs checkout output gets contradictory results with no signal why.
- **Evidence.** Launcher banner warning text itself; approval fingerprint mismatch on an installed-code lock verified with checkout code.
- **Design.** On startup, compare installed package version/revision against checkout (`VERSION` file or package manifest vs installed metadata). On mismatch, print a loud warning naming both revisions and which tree is authoritative for the current directory. No behavior change, no removal — warning only.
- **Files.** Launcher entrypoint + version source of truth (locate at plan time; likely `scripts/tailtrail.py` invocation path + install manifest).
- **Tests.** Skewed-environment simulation (point launcher at a stale copy in tmp): warning names both revisions, exit code unchanged. Clean-environment: no warning.
- **Acceptance.** Warning fires if and only if revisions differ; zero behavior change otherwise.
- **Risks.** Version-source ambiguity (which file is truth?) — resolve by reading, not assuming, at plan time.
- **Size.** Small (1–2 files, <50 lines + tests).

### 1.1 Tighten `DEEP_EDGE_KINDS` (DR3 finding)

- **Problem.** Structural edges (`loads-module`, `imports-module`) count as behavior proof, so lexical pile-on (4 weak edges, wrong file) resolves with high confidence. Observed live twice on the memoization goal.
- **Evidence.** DR3 log entry: owner `navigator.legacy.py` resolved on asserts-behavior-guard + raises-behavior-error + defines-symbol (shallow) + loads-module (currently deep). Recalibration: 12 historical resolutions, only compiler.py + ownership.py lack behavior/test edges.
- **Design.** Drop `imports-module`/`loads-module` from `DEEP_EDGE_KINDS` in `scripts/navigator_scope.py`; deep = behavior/caller/proof-only (tested-by, calls-symbol, captures/writes/catches/renders-*, defines-behavior-handler). Medium strength still counts (established precedent). Thin check (`_thin_owner_evidence`) runs first, unchanged.
- **Files.** `scripts/navigator_scope.py` (constant + docstring), `tests/test_navigator_scope.py` (DepthGateTests additions).
- **Tests.** Pile-on without behavior edges asks (memoization shape); deep-backed resolves; medium deep counts; thin-first ordering preserved; the 2 flipped historical shapes assert ask-with-reason (lock the cost visibly).
- **Acceptance.** Full scope suites green; calibration re-run confirms exactly the 2 known flips and no others.
- **Risks.** Over-asking on genuinely structural ownership (config/manifest-style modules owned via dependency edges) — mitigated by the cheap answer round + explicit-path bypass, both already shipped.
- **Size.** Small (<30 lines + tests).

### 1.3 Amendment audit (judgment, no code expected)

- **Problem.** Five mid-flight scope expansions were approved on disclosure (approvals freshness check, task-start answer wiring ×2, release schema + classifier, plus any from this phase). Disclosure without verification is trust without checking.
- **Evidence.** Session commit messages + run reports (each records its amendment and justification).
- **Design.** Re-read the five expansions against their locks in one sitting. Output per expansion: entailed (stands), needs-revert, or needs-retroactive-amendment. No code changes unless the audit finds a violation — the deliverable is the verdict table.
- **Files.** None (read-only). Record verdicts in this doc under a dated addendum.
- **Acceptance.** Every expansion has a verdict; any violation gets its own fix item.
- **Risks.** Hindsight bias — judge each against what was known and disclosed at the time, not against later knowledge.
- **Size.** Half a day of judgment.

### 1.2 Close-out receipts feature (the #1 burden)

- **Problem.** `close` demands requirement-linked receipts only the executor produces; agent-executed, fully-tested work can never close. Every session run shares this failure.
- **Evidence.** `close` error text ("must contain at least one requirement-linked receipt") against 160+ passing tests; prior lock `start-20260926163104-d257bf` is stale — needs a fresh `approve` on a restated lock.
- **Design (approved shape).** Record verb in `scripts/closure-recorder.py` (requirement ID + command + result + hash → ledger at checkpoints); acceptance of agent receipts in `scripts/closure-finalizer.py`; event type in `scripts/run-ledger.py`. Same bar as executor receipts (hash-bound, requirement-linked) — new recorder, not lower standard. Seed `--changed` with tests/schemas from the first Start so closure scope matches (practice half).
- **Files.** The three above + closure receipt tests (locate existing closure test files at plan time).
- **Tests.** Record → accept → close succeeds on agent evidence; forged/tampered receipt rejected; executor receipts unaffected (regression).
- **Acceptance.** A fully-tested agent run closes with status success on recorded receipts; close still fails with zero receipts.
- **Risks.** Scope says recorder/finalizer/ledger — if acceptance logic actually lives in `closure-close.py`, stop and re-scope (same lesson as the task-start wiring amendments: verify file ownership before editing).
- **Size.** Medium (verb + acceptance + event + tests).

---

## Phase 2 — Ergonomics (batch after Phase 1)

### 2.1 Single-invocation answers
- **Problem.** Every answer costs a minimum of two Starts (block, then re-invoke). DR1 evidence.
- **Design.** Accept answers on a blocked Start's output directly — needs a persisted Q&A handshake (question ID + packet fingerprint carried in the blocked report, answer submitted against it). Bounded by existing round caps; fingerprints re-validated, never trusted blind.
- **Files.** `task-start.py` (blocked-report handshake) + `navigator_scope.py` (answer-against-handshake validation) + tests.
- **Acceptance.** Today's two-round flow still works; one-round flow resolves identically; stale handshakes fail loudly.
- **Risks.** Handshake persistence format becomes a compatibility surface — version it from day one.
- **Size.** Medium.

### 2.2 `--scaffold-interpretation` envelope emission
- **Problem.** Scaffold → convert → dry-run → start is four commands plus Windows encoding friction (DR2 evidence).
- **Design.** One flag emitting the validated base64 envelope directly (scaffold + validate + encode in a single invocation). Reuses existing functions; no new validation logic.
- **Files.** `requirement-interpretation-draft.py` + tests.
- **Acceptance.** Output identical to the manual chain byte-for-byte on sample goals; failure modes unchanged (loud, exit 2).
- **Risks.** Minimal — composition only.
- **Size.** Small.

### 2.3 Archive follow-throughs (DR4 findings)
- **Problem.** Lockfiles hashed into manifests (noise, not evidence); archive verbs unreachable via the `tailtrail session` router.
- **Design.** Exclude `*.lock`/lockfiles from `_manifest_files`; route `archive`/`unarchive`/`list` through `tailtrail session` subcommands (thin dispatch, existing conventions).
- **Files.** `run-ledger.py`, `session-control.py`, `tailtrail.py` router (verify ownership at plan time — router may belong elsewhere), tests.
- **Acceptance.** Manifests contain evidence files only; router-invoked verbs match direct-invocation results byte-for-byte.
- **Risks.** Router ownership ambiguity — confirm file scope in planning or split the item.
- **Size.** Small.

### 2.4 Fast pre-push subset + timings
- **Problem.** Regression confidence costs 15+ minutes wall-clock; nothing tracks suite slowdowns (DR5 evidence).
- **Design.** Name the fast subset (discovery + scope + routing + session-control ≈ 1 min per DR5), record per-suite timings in the dry-run log each run, flag on 2× slowdown vs baseline.
- **Files.** Docs + log convention only; possibly a runner script if repetition justifies it.
- **Acceptance.** Documented subset, first timings baseline recorded.
- **Risks.** None material.
- **Size.** Trivial.

### 2.5 Shell-pattern docs
- **Problem.** Every Windows dry run tripped UTF-16 redirects and BOM base64 handling (DR1/DR2 evidence).
- **Design.** Document the conversion pattern (read-bytes, detect BOM, strip) in TAILTRAIL-COMMANDS.md or a contributor note; optionally a tiny `scripts/` UTF-8 read helper if three or more call sites warrant it.
- **Acceptance.** A new operator can copy-paste the pattern and succeed first try.
- **Risks.** None.
- **Size.** Trivial.

---

## Phase 3 — Evidence depth (one investigation run each)

### 3.1 Sensor runner
Standalone deterministic doc/evidence checks (IDs present, sections complete, orphans flagged; OK/GAP/ORPHAN, fail-closed), runnable pre-close. New module + read-only verb + synthetic-evidence tests. Advisory receipts first; enforcing only by later explicit decision.

### 3.2 Attest provenance
Read-only `attest resolve` mapping commits/diffs to reviewed Units (verified/drifted/unattested/indeterminate), then `attest anchor` pointers as ledger events. Reuses compiler fingerprints + approval ledger. Tests on synthetic git fixtures.

### 3.3 Proof-seeding diagnosis
Why relevant tests get `excluded` for some goals (stem matching? status mapping? read budgets?). Read-only diagnosis first (like the completed seeding diagnosis that closed its item with no code change); fix only what the diagnosis names, in a file the evidence supports.

### 3.4 Pack refresh v1.0.1 → v2.10.0
Read-only tree swap + compatibility re-verification + bridge smoke. Check golden fixtures quoting old rule paths first.

---

## Phase 4 — Structural directions (investigation runs before any code)

- **Ceremony toggles:** per-run `--sensors/--learnings/--summary-confirmation` instead of mode-global ceremony.
- **Question polish:** option caps, guaranteed Other, verbatim answer logging.
- **Host-identity neutralization:** open string + capability flags replacing the trichotomy; blast radius spans every host check, schema enum, golden fixture, and MCP tool schema — do not start casually.

---

## Execution order

Phase 1 in listed order (launcher warning → depth → audit → close-out) — audit sits after code lands so it reviews everything, close-out last as the heaviest. Then Phase 2 as one batch, Phase 3 one item at a time, Phase 4 only via dedicated investigation runs.
