# CI/CD Workflow Reference Files

This directory contains the **complete, production-ready** GitHub Actions workflow files for the cryogenic accelerator workspace.

## Workflow Suite (6 Workflows)

| File | Environment | Trigger | Purpose |
|------|------------|---------|---------|
| `ci-test.yml` | `testing` | Push main/develop, PRs | Schema validation, physics unit tests, integration tests, coverage |
| `ci-build.yml` | `staging` | Push main | Bundle build, manifest generation, artifact upload |
| `ci-deploy.yml` | `production` | Push main | GitHub Pages deployment, production badge |
| `ci-release.yml` | `production` | Tag `v*.*.*` | Automated GitHub Releases with bundle attachment |
| `ci-validate-pr.yml` | — | Pull requests | PR metadata, code quality, diff analysis, physics regression |
| `ci-schedule.yml` | `testing` → `staging` | Nightly 02:00 UTC | Full sweep, drift detection, dependency health |

## Pipeline Architecture

```
                    ┌─────────────────────────────────────────────────┐
                    │             TRIGGER EVENTS                       │
                    ├──────────┬──────────┬───────────┬───────────────┤
                    │ push     │ PR       │ tag       │ cron          │
                    │ main     │ opened   │ v*.*.*    │ 0 2 * * *     │
                    └────┬─────┴────┬─────┴─────┬─────┴──────┬────────┘
                         │          │           │            │
                    ┌────▼────┐┌────▼─────┐┌───▼───┐ ┌──────▼──────┐
                    │ci-test  ││ci-val-pr ││release │ │ci-schedule  │
                    │         ││          ││       │ │             │
                    │ schema  ││ metadata ││ build  │ │ temp sweep  │
                    │ physics ││ quality  ││ hash   │ │ drift check │
                    │ integr. ││ diff     ││ notes  │ │ dep health  │
                    │ integ.  ││ regress. ││ upload │ │ nightly bld │
                    └────┬────┘└──────────┘└───┬───┘ └─────────────┘
                         │                      │
                    ┌────▼────┐            ┌────▼────┐
                    │ci-build │            │ GitHub  │
                    │         │            │ Release │
                    │ rebuild │            │ page    │
                    │ manifest│            └─────────┘
                    │ artifact│
                    └────┬────┘
                         │
                    ┌────▼─────┐
                    │ci-deploy │
                    │          │
                    │ Pages    │
                    │ deploy   │
                    │ ══════   │
                    │PRODUCTION│
                    └──────────┘
```

## Activation

After merging this PR, copy the workflow files to `.github/workflows/`:

```bash
# Option A: Use the apply script
bash docs/ci-workflows/apply.sh

# Option B: Manual copy
cp docs/ci-workflows/ci-*.yml .github/workflows/
git add .github/workflows/
git commit -m "ci: activate complete workflow suite"
git push
```

> **Note:** Writing to `.github/workflows/` requires a token with the `workflow` scope.
> The Abacus AI GitHub App token cannot write to this path (platform restriction).
> Use the GitHub web editor or a PAT with workflow permissions.

## Test Matrix

| Test | Runner | Dependencies | Validates |
|------|--------|-------------|-----------|
| YAML schema | ubuntu-latest | pyyaml, jsonschema | engineering_data.yaml structure |
| JSON schema | ubuntu-latest | jsonschema | knowledge_topology.json structure |
| Graph integrity | ubuntu-latest | — | No broken outbound_links |
| HeliumPropertyEngine | ubuntu-latest | numpy | Enthalpy calculations (7 tests) |
| Mass balance | ubuntu-latest | numpy, pyyaml | verify_mass_balance (6 tests) |
| Workspace gen | ubuntu-latest | numpy, pyyaml | workspace_build.py end-to-end |
| Tarball verify | ubuntu-latest | — | Archive extraction + entry count |
| Topology anchors | ubuntu-latest | — | File anchors exist on disk |
| HTML structure | ubuntu-latest | — | DOCTYPE, head, body, title |
| Sensitive data | ubuntu-latest | — | No leaked tokens/keys |
| Python syntax | ubuntu-latest | — | All .py files compile |

## Environments

Create these in **Settings → Environments**:

| Environment | Used By | Purpose |
|-------------|---------|---------|
| `testing` | ci-test, ci-schedule | Validation and test runs |
| `staging` | ci-build, ci-deploy (build), ci-schedule | Bundle builds, pre-deploy |
| `production` | ci-deploy (deploy), ci-release | Live deployment, releases |
