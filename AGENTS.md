# Repository Agent Contract

## Mission

Own nuclear-power evidence for this repository: reactor status, capacity, construction, generation and other nuclear supply observations represented by the project. Produce primary-source-backed, reproducible records and derived views.

## Canonical authority

- Prefer IAEA, national regulators/operators, official statistical agencies and other primary sources appropriate to each field.
- Preserve reactor/facility identity, geography, status/effective date, capacity/generation units, source URL, retrieval time and revision/provenance fields required by the owning dataset.
- Keep observed reactor/fleet facts distinct from energy-price assumptions, forecasts and investment conclusions.
- Other finance repositories should reference versioned nuclear artifacts here rather than duplicate reactor/capacity authorities.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, canonical datasets/manifests, workflows/tests and public outputs.
2. Continue the existing canonical workline for the same outcome before creating another collector, dataset or branch.
3. Prefer newly verified reactor/fleet records, status/revision corrections, reproducible capacity/generation views, public read-back, then simplification.
4. Require identity/date/unit provenance before accepting a record or comparison.
5. Run focused deterministic checks and verify the exact reviewed revision before merge.
6. Stop at the fixed point; do not add forecasts or country coverage solely to increase record counts.

## Merge and release are separate

### PR merge conditions

A PR may merge when the repository-local nuclear-data contract is correct on the exact head revision: identity/status/date/unit semantics and provenance hold, focused tests pass, generated artifacts are reproducible where affected, and no unresolved review or correctness blocker remains.

A future reactor status change, live IAEA/regulator fetch after merge, public deployment, or real-world project completion is **not** a merge condition unless the PR specifically changes the release/live-acquisition mechanism and that mechanism must be validated before merge.

### Product/data release conditions

Release is a separate post-merge decision. Treat nuclear data/views as released only after the merged `main` revision is read back and the release requirements in scope are actually executed, including fresh primary-source collection when required, published/generated artifacts, public surface if any, deployment identity, and rollback/rebuild path.

A merged PR does not prove a reactor/project outcome or production release. A release/live-source blocker may block release without invalidating a correctly merged repository change. Report merge and release independently.

## Boundaries

- `operational`, `under construction`, `planned`, `suspended`, `shutdown` and unknown states must not be conflated.
- Do not infer capacity, completion dates, generation, utilization or restart outcomes not supported by primary evidence.
- Do not execute commodity/equity trades or account actions.
- Unobserved source, CI, deployment or future-project outcomes remain unverified.

## Completion report

Report verified nuclear records/revisions Before -> After, primary source/canonical artifact, Issue/PR/commit/check evidence, then report `merged` and `released` separately with direct evidence for each. Include duplication/manual work removed and the remaining blocker.