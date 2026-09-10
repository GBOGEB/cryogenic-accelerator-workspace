# GBOGEB Level 1 — Cryogenic Accelerator Workspace

Status: `PC1_CONTROL_PLANE`
Target: `LEVEL_1_0`
Role: `BRIDGE_RTM_PHYSICS_WORKER`

## Index

Level-1 human navigator. Machine state: `level1/ssot.json`; gate manifest: `level1/manifest.json`; reusable skill: `skill/`; executable Level-1 kernel arrives in PC2.

Existing capability is already substantial and is reused: `config/engineering_data.yaml` is the engineering SSOT, `src/physics_validator.py` is a real physics runtime, and `workspace_build.py` regenerates the workspace and outward bundle. Level-1 binds these into a common federation/control contract rather than cloning them.

MIP cycles: PC1 census/control, PC2 executable skill/runtime/agents, PC3 DMAIC + measured-only PCA/BT + CI orchestration proof. Structural targets are 0.3333 -> 0.7500 -> 1.0000; observed Level-1.0 requires executed green PC3 proof.

## AOD

AOD = **Architecture–Orchestration–Decision**.

### Architecture

Owns accelerator-workspace engineering configuration, local physics validation, build/regeneration and bridge/RTM worker outputs.

### Orchestration

Local flow: `engineering_data SSOT -> physics validator -> build -> artifact/receipt`. Federated flow may forward exact-SHA/source/output evidence through the routing hub to KEB/DOW and child disposition.

### Decision authority

May determine local config/runtime/build validity and emit independent physics receipts. Must not self-promote those receipts into QPS contractual truth, bidder acceptance or compliance; source class and parent/child authority remain explicit.
