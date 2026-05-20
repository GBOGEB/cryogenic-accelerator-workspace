# Cryogenic Accelerator Workspace

[![CI — Test & Validate](https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions/workflows/ci-test.yml/badge.svg)](https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions/workflows/ci-test.yml)
[![CI — Build Bundle](https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions/workflows/ci-build.yml/badge.svg)](https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions/workflows/ci-build.yml)
[![CI — Deploy to Pages](https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions/workflows/ci-deploy.yml/badge.svg)](https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions/workflows/ci-deploy.yml)

An integrated, self-documenting environment for cryogenic accelerator facility infrastructure. Engineering configuration mappings link directly to downstream thermodynamic validation modules and interactive visualization layers.

---

## Workspace Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKSPACE TOPOLOGY                       │
│                                                             │
│   config/                    src/                           │
│   ├── engineering_data.yaml  └── physics_validator.py       │
│   │   (SSOT parameters)         (He-4 thermodynamics)      │
│   └── knowledge_topology.json                              │
│       (3-node graph)         web/                           │
│                              ├── index.html (Hub)           │
│   workspace_build.py         ├── app.html (HMI Workbench)  │
│   (Regeneration engine)      └── workspace_bundle.tar.gz   │
│                                                             │
│   .github/workflows/                                        │
│   ├── ci-test.yml    → testing environment                  │
│   ├── ci-build.yml   → staging environment                  │
│   └── ci-deploy.yml  → production environment (Pages)       │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone
git clone https://github.com/GBOGEB/cryogenic-accelerator-workspace.git
cd cryogenic-accelerator-workspace

# Run physics validation
pip install numpy pyyaml
python3 -c "
import yaml, sys; sys.path.insert(0, 'src')
from physics_validator import verify_mass_balance
with open('config/engineering_data.yaml') as f:
    config = yaml.safe_load(f)
print(verify_mass_balance(config))
"

# Regenerate workspace
python3 workspace_build.py

# Open dashboards
open web/index.html   # Discovery Hub
open web/app.html     # Interactive HMI Workbench
```

## CI/CD Pipeline

| Workflow | Environment | Trigger | Purpose |
|----------|------------|---------|---------|
| `ci-test.yml` | `testing` | Push to main/develop, PRs | Config validation, physics tests, integrity checks |
| `ci-build.yml` | `staging` | Push to main | Bundle regeneration, manifest, artifact upload |
| `ci-deploy.yml` | `production` | Push to main | GitHub Pages deployment → **"Deployed" badge** |

### How Deployment Tracking Works

GitHub shows the **"Deployed to production"** badge on the repository sidebar when a workflow job declares an `environment:` with `name: production` and completes successfully. This is configured in `ci-deploy.yml`:

```yaml
deploy:
  environment:
    name: production                              # ← triggers the badge
    url: ${{ steps.deployment.outputs.page_url }} # ← adds "View deployment" link
```

### Environment Hierarchy

```
testing  →  staging  →  production
  │            │            │
  ▼            ▼            ▼
validate    build         deploy
configs     bundle        to Pages
physics     manifest      live URL
integrity   artifact      "Deployed" badge
```

## File Inventory

| File | Purpose | Lines |
|------|---------|-------|
| `config/engineering_data.yaml` | SSOT — He-4 heat loads, mass balances, version control | ~35 |
| `config/knowledge_topology.json` | 3-node knowledge graph (SSOT → Physics → HMI) | ~30 |
| `src/physics_validator.py` | HeliumPropertyEngine + mass balance verification | ~47 |
| `web/index.html` | Discovery hub dashboard | ~100 |
| `web/app.html` | Interactive split-pane HMI with Plotly charts | ~250 |
| `workspace_build.py` | Full workspace regeneration script | ~381 |

## Engineering Domain

```
Domain:   Cryogenic Accelerator Facility
Coolant:  Helium-4 (He-4) near lambda point (4.2–4.5 K)
Formula:  ṁ = Q_total / Δh
Engine:   HeliumPropertyEngine (polynomial fit from NIST data)
Status:   PASS — mass flow within operational limits
```

## License

Proprietary — Systems Design Group
