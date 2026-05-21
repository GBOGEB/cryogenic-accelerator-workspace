#!/bin/bash
# Apply CI workflow files to .github/workflows/
# Run this from the repo root: bash docs/ci-workflows/apply.sh
set -e

if [ ! -d docs/ci-workflows ]; then
  echo "❌ Please run this script from the repository root."
  exit 1
fi

mkdir -p .github/workflows
cp docs/ci-workflows/ci-test.yml .github/workflows/ci-test.yml
cp docs/ci-workflows/ci-build.yml .github/workflows/ci-build.yml
cp docs/ci-workflows/ci-deploy.yml .github/workflows/ci-deploy.yml
if [ -d .github/workflows/.github/workflows ]; then
  rm -r .github/workflows/.github/workflows
fi
echo "✅ Workflow files applied to .github/workflows/"
echo "Now commit and push: git add .github/workflows/ && git commit -m 'ci: apply workflow updates' && git push"
