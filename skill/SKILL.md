---
name: cryogenic-accelerator-level1
description: Use in cryogenic-accelerator-workspace to census, modernize, repair, innovate, or perpetuate bridge/RTM/physics capability; run Level-1 checks; coordinate independent physics receipts; and apply measured PCA or Bradley-Terry diagnostics while preserving engineering source and child authority boundaries.
---

# Cryogenic Accelerator Level 1

1. Read `LEVEL1.md` and `level1/ssot.json`.
2. Run `python level1/runtime.py census` and `python level1/runtime.py mip`.
3. Reuse `config/engineering_data.yaml`, `src/physics_validator.py`, and `workspace_build.py`; do not clone the physics/build stack.
4. Run `python level1/runtime.py orchestrate` for blocks, agents, role and federation targets.
5. PCA accepts only measured numeric rows; BT accepts only explicit pairwise outcomes. Missing/insufficient inputs DEFER.
6. Run `python level1/runtime.py self-test` before claiming Level-1.0. Synthetic fixtures test code only.
7. Independent physics receipts may support challenge/review but may not self-promote QPS contract truth, compliance or child disposition.
