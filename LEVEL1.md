# GBOGEB Level 1 — Cryogenic Accelerator Workspace

Status: `PC3_LEVEL1_CANDIDATE`
Target: `LEVEL_1_0`
Role: `BRIDGE_RTM_PHYSICS_WORKER`

## Index

Level-1 human navigator. Machine state: `level1/ssot.json`; gate manifest: `level1/manifest.json`; reusable skill: `skill/`; executable Level-1 kernel: `level1/runtime.py`.

Existing capability is already substantial and is reused: `config/engineering_data.yaml` is the engineering SSOT, `src/physics_validator.py` is a real physics runtime, and `workspace_build.py` regenerates the workspace and outward bundle. Level-1 binds these into a common federation/control contract rather than cloning them.

MIP cycles: PC1 census/control, PC2 executable skill/runtime/agents, PC3 DMAIC + measured-only PCA/BT + CI orchestration proof. Structural target on this branch is 12/12 = 1.0000; observed Level-1.0 requires executed green PC3 proof.

## AOD

AOD = **Architecture–Orchestration–Decision**.

### Architecture

Owns accelerator-workspace engineering configuration, local physics validation, build/regeneration and bridge/RTM worker outputs.

### Orchestration

Local flow: `engineering_data SSOT -> physics validator -> build -> artifact/receipt`. Federated flow may forward exact-SHA/source/output evidence through the routing hub to KEB/DOW and child disposition.

### Decision authority

May determine local config/runtime/build validity and emit independent physics receipts. Must not self-promote those receipts into QPS contractual truth, bidder acceptance or compliance; source class and parent/child authority remain explicit.

## DMAIC

- **Define:** bind role, inputs/outputs, native runtime anchors, authority and the fixed 12-gate denominator.
- **Measure:** run the Level-1 census at the exact tested SHA and record missing gates/native runtime visibility.
- **Analyze:** use MIP gap output first; PCA/BT only use measured observations or explicit comparisons.
- **Improve:** repair the smallest executable gap, reuse the existing physics/build stack and add only authority-safe edges.
- **Control:** exact-head CI compiles and exercises census/MIP/orchestration, proves no-input PCA/BT DEFER, runs self-test and publishes receipts; first red recurses on that exact invariant.

MIP = **Modernize (repair/reuse), Innovate (new useful nodes/edges/functions), Perpetuate (repeat exact-SHA execution and receipts).**

## PCA

PCA is measured multivariate priority evidence, not a physical-property source or governance score. `python level1/runtime.py pca --input rows.json` requires at least three real observations and at least two variables; insufficient or zero-variance data DEFERs. Synthetic self-test rows prove the code only. PCA may inform worker/feature priority but cannot change engineering/compliance credit.

## BT

Bradley–Terry is an observed pairwise priority diagnostic. `python level1/runtime.py bt --input comparisons.json` uses explicit `[winner, loser]` observations and DEFERs with no comparisons. It may rank repair or experiment alternatives, not replace physics validation, source provenance or child disposition.

## Level-1.0 DoV

`LEVEL_1_0` requires all 12 gates true and a green exact-head `Level 1 MIP` workflow. Structure without executed CI remains candidate. No QPS engineering/compliance/negotiation credit is created by the bootstrap.
