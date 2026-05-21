#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# CI/CD Workflow Activation Script
# Copies workflow files from docs/ci-workflows/ to .github/workflows/
# Requires: git push with workflow-scope token
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEST="$REPO_ROOT/.github/workflows"

echo "═══════════════════════════════════════"
echo "  CI/CD Workflow Activation"
echo "═══════════════════════════════════════"
echo "  Source: $SCRIPT_DIR"
echo "  Target: $DEST"

mkdir -p "$DEST"

COPIED=0
for wf in "$SCRIPT_DIR"/ci-*.yml; do
  name=$(basename "$wf")
  cp "$wf" "$DEST/$name"
  echo "  ✅ $name → .github/workflows/$name"
  COPIED=$((COPIED + 1))
done

# Clean up nested duplicates if any
if [ -d "$DEST/.github" ]; then
  echo "  🧹 Removing nested .github/ duplicate"
  rm -rf "$DEST/.github"
fi

echo "═══════════════════════════════════════"
echo "  $COPIED workflows copied"
echo ""
echo "  Next steps:"
echo "    cd $REPO_ROOT"
echo "    git add .github/workflows/"
echo "    git commit -m 'ci: activate complete workflow suite'"
echo "    git push"
echo "═══════════════════════════════════════"
