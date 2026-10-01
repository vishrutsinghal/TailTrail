# Requirement Completion & Impact Map — Detailed Feature Analysis

Covers `scripts/requirement-completion.py` (the gate) and
`scripts/requirement-impact-map.py` (the scout): what each part does, what
needs fixing or improving, and exactly how downstream systems consume them.
Verified by 5/5 unit tests plus live runs on branch `tailtrail_v2`.

## 1. Feature anatomy

### 1a. Completion gate (`requirement-completion.py`, 36 lines)

Single function `gate(root, run_id, receipts_path, record=True)` plus CLI.
For every anchor requirement and every tier in its validation contract, it
sorts evidence receipts into a severity-ordered verdict per tier:

- `fail` / `timed-out` / `blocked` / `unavailable` — any reported
  non-pass of that flavor (authoritative failure dominates pass).
- `unverified` — a `pass` exists but only label-quality (`declared`):
  claimed, not proven.
- `insufficient` — no passing evidence at all.
- Silence (no finding) — an authoritative (`trusted`/`attested`) `pass`
  covers the tier.

`complete` is true only with zero findings. Optionally persists the verdict
(`completion-gates/gate-N.json`) and appends a `completion_gate` ledger event.

### 1b. Impact map (`requirement-impact-map.py`, 52 lines)

`map_impact(root, run_id, changed)` parses every repo `.py` file with `ast`
(symbol defs; bare-name call sites), intersects the actual changed paths with
each requirement's approved `likely_paths`, and emits per requirement:
changed symbols, **callers**, **tests**, a `mapped`/`new-drift`
classification, and `selected_controls` (always `completion-review` +
`focused-validation`; plus `architecture-fitness` when callers or required
paths exist; plus `behavior-harness` when scenarios exist). Persists to
`impact-maps/map-N.json` with a `requirement_impact_mapped` event. The
payload states its own boundary: *"callers and tests are candidates, not
completion proof."*

## 2. Purpose of each part

| Part | Purpose |
|---|---|
| Tier loop + severity ordering | One deterministic verdict per requirement per tier; worst outcome wins so partial proof never reads as complete |
| Trust hierarchy (`trusted`/`attested` vs `declared`) | Separates *proven* from *claimed*; the spine of the whole gate |
| Failure dominance | An authoritative `fail` kills the tier even beside passes — no averaging away breakage |
| AST symbol/call extraction | Grounds "what changed" in code facts, not assertions |
| Changed ∩ likely_paths join | Binds reality to the approved boundary per requirement |
| `mapped` / `new-drift` classification | Names scope escapes at creation time, not incident time |
| Caller/test discovery | Surfaces the tests you didn't know you needed and the callers you didn't know you had |
| Control selection | Routes follow-up evidence (which harness must still run) from findings, not from memory |
| Ledger events + versioned artifacts | Every verdict and map is append-only, fingerprinted, reviewable |

## 3. How downstream systems utilize it

| Consumer | Consumes | How |
|---|---|---|
| `completion-report.py` | Gate verdicts | `complete` feeds overall status; per-tier findings feed requirement rows; missing proof blocks `complete` |
| `debug-correction.py:175` | Impact maps | Expected changed paths mapped *before* proposing a correction — blast radius stated up front |
| `context-continuity.py:126` | Latest impact map | Slice transitions inherit changed paths, callers, tests |
| `harness-checkpoint.py` flows | Both (indirect) | Checkpoint requirement states mirror gate semantics; drift mirrors map classification |
| Host/agent review | Map JSON via CLI | `impact-map --changed` for human blast-radius review |
| Closure `finalize`/`close` | Gate + report chain | Refuses `complete` while findings stand (verified: `replan-required`) |

## 4. Fixes needed (defects, not wishes)

1. **Nothing open.** The two candidate defects investigated this session
   (map accuracy, gate trust logic) both verified correct under test.
   No failing behavior is known.

## 5. Improvements needed (ranked)

### 5.0 Implementation phases for item #1 (change-driven refresh)

- **Phase 1 — scoped refresh entry (mapper).** Add a bounded refresh
  function: given verified changed paths, re-extract those files plus
  direct caller/callee neighborhood (existing budgets), merge into the
  container via the current merge API, re-fingerprint touched entries.
  *Exit:* unit tests on temp repos (changed file re-sliced, fingerprints
  rotate, untouched entries byte-identical).
- **Phase 2 — checkpoint wiring.** After checkpoint persistence, pass its
  *verified-only* changed set into the Phase 1 entry. Unverified and
  missing paths never reach refresh. No new stages; one call site.
  *Exit:* live run showing a post-implementation checkpoint triggering a
  scoped refresh with ledger events.
- **Phase 3 — freshness proof.** Demonstrate the loop closing: implement a
  change, refresh, then show the next scope investigation reading fresh
  slices (no stale flags) where it previously read stale ones. Dry-run
  matrix scenario asserting freshness deltas.
  *Exit:* before/after freshness report on a real change.
- **Phase 4 — bounds tuning (CLOSED, no change).** Measured on the
  repo itself (~1200 files, 5 hot finalists): cold expansion ~5s at any
  limit (walk-dominated), warm reads 0.02–0.03s (~200x amortization),
  cache 97KB/116KB/152KB at limits 4/8/16. Defaults (limit 8, cap 5)
  ratified — cost is flat, weight is middle, worst cold case stays
  single-digit seconds inside an already-blocked question flow.

### 5.1 Ranked items

1. **Change-driven graph refresh (decided direction — supersedes unification).**
   Do NOT retire the walker's parsing in favor of the mapper. Instead, after
   implementation, use the impact map's *verified* changed set to drive a
   targeted mapper refresh: changed files plus bounded caller/callee
   neighborhood only, re-fingerprinted on write. This flips graph freshness
   from time-driven (periodic full re-walks) to change-driven (refresh
   exactly what moved). The VCS verification gate is the trust anchor:
   verified changes refresh, unverified ones never touch the graph, so
   phantom claims cannot pollute it. Hooks into the existing checkpoint
   flow post-implementation; no new stages. Effect over time: the cache
   converges on reality from both directions — appetite-shaped growth plus
   change-shaped freshness — with zero scheduled jobs.
2. **Bind receipts to content hashes.** The gate never re-verifies freshness:
   pass the tests, edit the file after, old receipt still satisfies. Stamp
   managed receipts with changed-path fingerprints; downgrade stale passes
   to `unverified` at gate time.
3. **Surface maps in completion.** The richest blast-radius evidence stops
   one step short of the verdict — include per-requirement callers/tests in
   the completion payload (read-only, no new gates).
4. **Live `--staged` mode.** Map `git diff --cached` during work for
   pre-commit drift warnings. Useful; batch it, don't lead with it.
5. **Deliberately not suggested:** retiring the walker (rejected — it gains
   the refresh-driver role instead), weakening declared-never-passes,
   retuning the mapped/new-drift taxonomy, or softening fail-dominance.
6. **Known parser limits (accepted, mapper covers):** Python-only parsing
   and attribute-call blindness remain in the walker. They stop mattering
   once refresh flows through the mapper: the walker's job narrows to the
   requirement join (changed ∩ likely_paths, drift, control selection),
   where exact call completeness was never required.

## 6. Verification record

- `tests/test_requirement_impact_completion.py`: 5/5 (mapping, callers,
  tests, drift, trusted-pass, declared-unverified, fail-dominance).
- Live: doc-scope and infra-scope runs consume both modules without error;
  closure refusal on this run's own scope mismatch ran on these rails.
- Known limits (accepted): Python-only parsing, attribute-call blindness,
  post-hoc batch operation, receipts prove provenance/outcome — not
  correctness.
