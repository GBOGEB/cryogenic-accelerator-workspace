# CI/CD Workflow Files

These are the complete workflow files for the cryogenic-accelerator-workspace CI/CD pipeline.

## Environment Tracking

| Workflow | Environment | Purpose |
|----------|------------|---------|
| ci-test.yml | `testing` | Config validation, physics tests, integrity checks |
| ci-build.yml | `staging` | Bundle rebuild, manifest, artifact upload |
| ci-deploy.yml | `production` | GitHub Pages deployment → "Deployed" badge |

## How to Apply

```bash
bash docs/ci-workflows/apply.sh
```

## Key Feature: Deployment Badges

The `environment: name: production` declaration in ci-deploy.yml is what makes GitHub show the green "Deployed to production" badge on the repository sidebar.
