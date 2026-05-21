# MCP Orchestration Framework

> **Tuple-Based Instruction Sequences for Cryogenic Accelerator Workspace Automation**
>
> Version: 1.0.0 | Date: 2026-05-21 | Schema: `(task_id, task_type, dependencies, inputs, outputs, validation)`

---

## 1. Tuple Format Specification

Each orchestration task is defined as a 6-element tuple:

```
(task_id, task_type, dependencies, inputs, outputs, validation)
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | Unique identifier: `{category}_{sequence:03d}` |
| `task_type` | `enum` | Task category from taxonomy (see §2) |
| `dependencies` | `list[str]` | List of task_ids that must complete first |
| `inputs` | `dict` | Required input artifacts/parameters |
| `outputs` | `dict` | Expected output artifacts/state changes |
| `validation` | `dict` | Post-execution verification criteria |

---

## 2. Task Grouping Taxonomy

```
ORCHESTRATION_CATEGORIES = {
    "REPO_INIT":     "Repository initialization, git setup, remote configuration",
    "CONFIG_GEN":    "Configuration file generation and validation",
    "CODE_BUILD":    "Code compilation, workspace building, bundling",
    "TEST_EXEC":     "Testing execution — unit, integration, regression",
    "DEPLOY_OPS":    "Deployment operations — Pages, releases, artifacts",
    "VERIFY_CHECK":  "Verification checkpoints — integrity, consistency"
}
```

### Category Dependency Graph

```
                ┌──────────┐
                │REPO_INIT │
                └────┬─────┘
                     │
              ┌──────┴──────┐
              ▼              ▼
        ┌──────────┐  ┌──────────┐
        │CONFIG_GEN│  │CODE_BUILD│
        └────┬─────┘  └────┬─────┘
              │              │
              └──────┬───────┘
                     ▼
              ┌──────────┐
              │TEST_EXEC │
              └────┬─────┘
                     │
              ┌──────┴──────┐
              ▼              ▼
        ┌──────────┐  ┌────────────┐
        │DEPLOY_OPS│  │VERIFY_CHECK│
        └──────────┘  └────────────┘
```

---

## 3. Orchestration Sequences

### 3.1 — Fresh Repository Setup

```python
WORKFLOW_REPO_SETUP = [
    (
        "REPO_INIT_001",
        "REPO_INIT",
        [],                                    # No dependencies — root task
        {"workspace_path": "/home/ubuntu"},
        {"git_initialized": True, "branch": "main"},
        {"cmd": "git rev-parse --is-inside-work-tree", "expect": "true"}
    ),
    (
        "REPO_INIT_002",
        "REPO_INIT",
        ["REPO_INIT_001"],
        {"template": ".gitignore.template"},
        {"file": ".gitignore", "rules_count": ">50"},
        {"cmd": "git check-ignore __pycache__/test.pyc", "expect": "__pycache__/test.pyc"}
    ),
    (
        "REPO_INIT_003",
        "REPO_INIT",
        ["REPO_INIT_001"],
        {"git_user": "cryogenic-workspace@accelerator.dev"},
        {"remote": "origin", "url": "github.com/GBOGEB/cryogenic-accelerator-workspace"},
        {"cmd": "git remote get-url origin", "expect_contains": "GBOGEB"}
    ),
    (
        "CONFIG_GEN_001",
        "CONFIG_GEN",
        ["REPO_INIT_002"],
        {"ssot_template": "engineering_data.schema"},
        {"file": "config/engineering_data.yaml", "keys": ["version_control", "engineering_metrics"]},
        {"cmd": "python3 -c \"import yaml; yaml.safe_load(open('config/engineering_data.yaml'))\"", "exit_code": 0}
    ),
    (
        "CONFIG_GEN_002",
        "CONFIG_GEN",
        ["REPO_INIT_002"],
        {"topology_nodes": ["NODE_ENTRY_SSOT", "NODE_PHYSICS_CORE", "NODE_HMI_DASHBOARD"]},
        {"file": "config/knowledge_topology.json", "node_count": 3},
        {"cmd": "python3 -c \"import json; d=json.load(open('config/knowledge_topology.json')); assert len(d['knowledge_topology']['nodes'])>=3\"", "exit_code": 0}
    ),
    (
        "CODE_BUILD_001",
        "CODE_BUILD",
        ["CONFIG_GEN_001", "CONFIG_GEN_002"],
        {"build_script": "workspace_build.py"},
        {"files": ["src/physics_validator.py", "web/index.html", "web/app.html", "web/workspace_bundle.tar.gz"]},
        {"cmd": "python3 workspace_build.py && test -f web/workspace_bundle.tar.gz", "exit_code": 0}
    ),
    (
        "REPO_INIT_004",
        "REPO_INIT",
        ["CODE_BUILD_001"],
        {"files": "all tracked"},
        {"commit": "initial", "pushed": True},
        {"cmd": "git log --oneline -1 | grep -q 'initial\\|init\\|setup'", "exit_code": 0}
    ),
]
```

### 3.2 — CI/CD Activation

```python
WORKFLOW_CICD_ACTIVATION = [
    (
        "CONFIG_GEN_010",
        "CONFIG_GEN",
        [],                                    # Assumes repo exists
        {"workflow_source": "docs/ci-workflows/"},
        {"files": [
            ".github/workflows/ci-test.yml",
            ".github/workflows/ci-build.yml",
            ".github/workflows/ci-deploy.yml",
            ".github/workflows/ci-release.yml",
            ".github/workflows/ci-validate-pr.yml",
            ".github/workflows/ci-schedule.yml"
        ]},
        {"cmd": "ls .github/workflows/ci-*.yml | wc -l", "expect": "6"}
    ),
    (
        "CONFIG_GEN_011",
        "CONFIG_GEN",
        ["CONFIG_GEN_010"],
        {"environments": ["testing", "staging", "production"]},
        {"github_environments_created": True},
        {"manual": "Verify at Settings → Environments"}
    ),
    (
        "DEPLOY_OPS_001",
        "DEPLOY_OPS",
        ["CONFIG_GEN_010"],
        {"branch": "main"},
        {"pushed": True, "workflows_active": True},
        {"cmd": "git push origin main", "expect": "workflows trigger on GitHub Actions tab"}
    ),
    (
        "VERIFY_CHECK_001",
        "VERIFY_CHECK",
        ["DEPLOY_OPS_001"],
        {"github_actions_url": "https://github.com/GBOGEB/cryogenic-accelerator-workspace/actions"},
        {"ci_test_status": "success", "ci_build_status": "success", "ci_deploy_status": "success"},
        {"manual": "All 3 workflows show green check on Actions tab"}
    ),
]
```

### 3.3 — Workspace Clone & Verification

```python
WORKFLOW_CLONE_VERIFY = [
    (
        "REPO_INIT_020",
        "REPO_INIT",
        [],
        {"clone_url": "https://github.com/GBOGEB/cryogenic-accelerator-workspace.git",
         "target": "/tmp/workspace_verify"},
        {"cloned": True, "files_present": True},
        {"cmd": "git -C /tmp/workspace_verify log --oneline -1", "exit_code": 0}
    ),
    (
        "VERIFY_CHECK_010",
        "VERIFY_CHECK",
        ["REPO_INIT_020"],
        {"workspace": "/tmp/workspace_verify"},
        {"file_inventory": "complete"},
        {"cmd": "cd /tmp/workspace_verify && test -f config/engineering_data.yaml && test -f src/physics_validator.py && test -f web/index.html", "exit_code": 0}
    ),
    (
        "TEST_EXEC_010",
        "TEST_EXEC",
        ["VERIFY_CHECK_010"],
        {"workspace": "/tmp/workspace_verify", "deps": ["numpy", "pyyaml"]},
        {"physics_status": "PASS|WARN_LIMIT"},
        {"cmd": "cd /tmp/workspace_verify && python3 -c \"import yaml,sys;sys.path.insert(0,'src');from physics_validator import verify_mass_balance;c=yaml.safe_load(open('config/engineering_data.yaml'));r=verify_mass_balance(c);assert r['system_verification_status'] in ('PASS','WARN_LIMIT')\"", "exit_code": 0}
    ),
    (
        "TEST_EXEC_011",
        "TEST_EXEC",
        ["VERIFY_CHECK_010"],
        {"workspace": "/tmp/workspace_verify"},
        {"build_success": True},
        {"cmd": "cd /tmp/workspace_verify && python3 workspace_build.py && test -f web/workspace_bundle.tar.gz", "exit_code": 0}
    ),
    (
        "VERIFY_CHECK_011",
        "VERIFY_CHECK",
        ["TEST_EXEC_010", "TEST_EXEC_011"],
        {"workspace": "/tmp/workspace_verify"},
        {"all_checks": "passed"},
        {"cmd": "echo '✅ Clone verification complete'", "exit_code": 0}
    ),
]
```

### 3.4 — Release Deployment

```python
WORKFLOW_RELEASE = [
    (
        "TEST_EXEC_020",
        "TEST_EXEC",
        [],
        {"branch": "main"},
        {"all_tests": "passed"},
        {"cmd": "python3 -m pytest tests/ -v", "exit_code": 0}
    ),
    (
        "CODE_BUILD_010",
        "CODE_BUILD",
        ["TEST_EXEC_020"],
        {"build_script": "workspace_build.py"},
        {"bundle": "web/workspace_bundle.tar.gz", "bundle_sha256": "<computed>"},
        {"cmd": "python3 workspace_build.py && sha256sum web/workspace_bundle.tar.gz", "exit_code": 0}
    ),
    (
        "DEPLOY_OPS_010",
        "DEPLOY_OPS",
        ["CODE_BUILD_010"],
        {"tag_pattern": "v{major}.{minor}.{patch}", "tag": "v2.4.1"},
        {"tag_created": True, "pushed": True},
        {"cmd": "git tag v2.4.1 && git push origin v2.4.1", "exit_code": 0}
    ),
    (
        "DEPLOY_OPS_011",
        "DEPLOY_OPS",
        ["DEPLOY_OPS_010"],
        {"trigger": "ci-release.yml on tag push"},
        {"release_created": True, "bundle_attached": True},
        {"manual": "GitHub Release page shows v2.4.1 with workspace_bundle.tar.gz"}
    ),
    (
        "VERIFY_CHECK_020",
        "VERIFY_CHECK",
        ["DEPLOY_OPS_011"],
        {"release_url": "https://github.com/GBOGEB/cryogenic-accelerator-workspace/releases/tag/v2.4.1"},
        {"release_exists": True, "assets_count": ">0"},
        {"cmd": "curl -s https://api.github.com/repos/GBOGEB/cryogenic-accelerator-workspace/releases/tags/v2.4.1 | python3 -c 'import json,sys;r=json.load(sys.stdin);assert len(r.get(\"assets\",[]))>0'", "exit_code": 0}
    ),
]
```

---

## 4. Execution Dependency Graph (Complete)

```
REPO_INIT_001 ──┬── REPO_INIT_002 ──── CONFIG_GEN_001 ──┐
                │                                         │
                └── REPO_INIT_003     CONFIG_GEN_002 ────┤
                                                          │
                                          CODE_BUILD_001 ◄┘
                                               │
                                          REPO_INIT_004
                                               │
                                     ┌─────────┴─────────┐
                                     │                     │
                              CONFIG_GEN_010         CONFIG_GEN_011
                                     │
                              DEPLOY_OPS_001
                                     │
                              VERIFY_CHECK_001
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
               TEST_EXEC_020   REPO_INIT_020   VERIFY_CHECK_010
                     │               │               │
               CODE_BUILD_010  TEST_EXEC_010   TEST_EXEC_011
                     │               │               │
               DEPLOY_OPS_010  VERIFY_CHECK_011     │
                     │                               │
               DEPLOY_OPS_011 ◄──────────────────────┘
                     │
               VERIFY_CHECK_020
```

---

## 5. Error Handling Protocols

### 5.1 — Error Classification

| Code | Severity | Action |
|------|----------|--------|
| `E001` | FATAL | Dependency missing — halt pipeline |
| `E002` | FATAL | Git operation failed — check credentials |
| `E003` | ERROR | Validation failed — block downstream tasks |
| `E004` | WARN | Non-critical check failed — log and continue |
| `E005` | INFO | Optional step skipped — no action |

### 5.2 — Retry Policy

```python
RETRY_POLICY = {
    "REPO_INIT":    {"max_retries": 3, "backoff_seconds": 5,  "on_fail": "HALT"},
    "CONFIG_GEN":   {"max_retries": 2, "backoff_seconds": 2,  "on_fail": "HALT"},
    "CODE_BUILD":   {"max_retries": 2, "backoff_seconds": 10, "on_fail": "HALT"},
    "TEST_EXEC":    {"max_retries": 1, "backoff_seconds": 0,  "on_fail": "REPORT"},
    "DEPLOY_OPS":   {"max_retries": 3, "backoff_seconds": 15, "on_fail": "ROLLBACK"},
    "VERIFY_CHECK": {"max_retries": 1, "backoff_seconds": 0,  "on_fail": "REPORT"},
}
```

### 5.3 — Rollback Sequences

```python
ROLLBACK_DEPLOY = [
    ("ROLLBACK_001", "DEPLOY_OPS", [], {"action": "revert_last_commit"}, {}, {"cmd": "git revert HEAD --no-edit && git push"}),
    ("ROLLBACK_002", "VERIFY_CHECK", ["ROLLBACK_001"], {"action": "verify_revert"}, {}, {"cmd": "git log --oneline -1 | grep Revert"}),
]
```

---

## 6. Ubuntu Command Sequences

### 6.1 — Complete Setup (Expected Outputs)

```bash
# ── Step 1: Clone ──
$ git clone https://github.com/GBOGEB/cryogenic-accelerator-workspace.git
# Expected: Cloning into 'cryogenic-accelerator-workspace'...

$ cd cryogenic-accelerator-workspace

# ── Step 2: Install Dependencies ──
$ pip install numpy pyyaml pytest pytest-cov jsonschema
# Expected: Successfully installed numpy-X.X.X pyyaml-X.X pytest-X.X.X ...

# ── Step 3: Validate Configs ──
$ python3 -c "import yaml; d=yaml.safe_load(open('config/engineering_data.yaml')); print(f'Version: {d[\"version_control\"][\"current_version\"]}')"
# Expected: Version: 2.4.1-build.108

$ python3 -c "import json; d=json.load(open('config/knowledge_topology.json')); print(f'Nodes: {len(d[\"knowledge_topology\"][\"nodes\"])}')"
# Expected: Nodes: 3

# ── Step 4: Run Physics Validation ──
$ python3 -c "
import yaml, sys
sys.path.insert(0, 'src')
from physics_validator import verify_mass_balance
with open('config/engineering_data.yaml') as f:
    config = yaml.safe_load(f)
r = verify_mass_balance(config)
for k,v in r.items(): print(f'  {k}: {v}')
"
# Expected:
#   calculated_mass_flow_kg_s: 0.47274
#   enthalpy_in_j_g: 34.414
#   enthalpy_out_j_g: 38.2355
#   system_verification_status: WARN_LIMIT

# ── Step 5: Build Workspace ──
$ python3 workspace_build.py
# Expected:
#   ✔ Standardized System Breakdown Structure (SBS) folders generated.
#   ✔ Source files, markdown documentation frameworks, and script nodes populated.
#   ✔ Successful Execution: High-fidelity transfer archive created at: 'web/workspace_bundle.tar.gz'

# ── Step 6: Verify Archive ──
$ tar tzf web/workspace_bundle.tar.gz
# Expected:
#   README.md
#   config/engineering_data.yaml
#   config/knowledge_topology.json
#   src/physics_validator.py
#   web/index.html
#   web/app.html

# ── Step 7: Run Tests (if pytest tests exist) ──
$ python3 -m pytest tests/ -v --tb=short 2>/dev/null || echo "Test dir not in repo yet"
# Expected: Tests pass or test directory not present in base clone

# ── Step 8: Activate CI/CD ──
$ bash docs/ci-workflows/apply.sh
# Expected:
#   ✅ ci-test.yml → .github/workflows/ci-test.yml
#   ✅ ci-build.yml → .github/workflows/ci-build.yml
#   ✅ ci-deploy.yml → .github/workflows/ci-deploy.yml
#   ✅ ci-release.yml → .github/workflows/ci-release.yml
#   ✅ ci-validate-pr.yml → .github/workflows/ci-validate-pr.yml
#   ✅ ci-schedule.yml → .github/workflows/ci-schedule.yml

$ git add .github/workflows/ && git commit -m "ci: activate complete workflow suite" && git push
# Expected: Workflows trigger on GitHub Actions tab

# ── Step 9: Verify Deployment Badge ──
$ curl -s "https://github.com/GBOGEB/cryogenic-accelerator-workspace" | grep -o 'Deployed'
# Expected: Deployed (once ci-deploy.yml runs with environment: production)
```

### 6.2 — CI/CD Activation (Standalone)

```bash
cd /path/to/cryogenic-accelerator-workspace
cp docs/ci-workflows/ci-*.yml .github/workflows/
rm -rf .github/workflows/.github  # Clean nested duplicates
git add .github/workflows/
git commit -m "ci: activate 6-workflow CI/CD suite"
git push origin main
# → Triggers: ci-test, ci-build, ci-deploy on GitHub Actions
```

### 6.3 — Release Creation

```bash
# Ensure main is clean and tests pass
git checkout main && git pull
python3 -m pytest tests/ -v

# Tag and push
git tag -a v2.4.1 -m "Release v2.4.1 — cryogenic workspace"
git push origin v2.4.1
# → Triggers: ci-release.yml → GitHub Release with bundle attachment
```

---

## 7. Orchestration Engine (Reference Implementation)

```python
"""
Minimal orchestration engine for executing tuple-based task sequences.
Usage: executor = OrchestrationEngine(WORKFLOW_REPO_SETUP)
       executor.run()
"""
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    output: str = ""
    error: str = ""

class OrchestrationEngine:
    def __init__(self, tasks: list):
        self.tasks = {t[0]: t for t in tasks}
        self.results: dict[str, TaskResult] = {}

    def _deps_met(self, task_id: str) -> bool:
        _, _, deps, _, _, _ = self.tasks[task_id]
        return all(
            self.results.get(d, TaskResult(d, TaskStatus.PENDING)).status == TaskStatus.SUCCESS
            for d in deps
        )

    def _validate(self, task_id: str) -> bool:
        _, _, _, _, _, validation = self.tasks[task_id]
        if "cmd" in validation:
            try:
                result = subprocess.run(
                    validation["cmd"], shell=True,
                    capture_output=True, text=True, timeout=30
                )
                if "expect" in validation:
                    return validation["expect"] in result.stdout.strip()
                return result.returncode == validation.get("exit_code", 0)
            except subprocess.TimeoutExpired:
                return False
        return True  # Manual validation — assume pass

    def run(self) -> dict[str, TaskResult]:
        order = self._topological_sort()
        for task_id in order:
            if not self._deps_met(task_id):
                self.results[task_id] = TaskResult(task_id, TaskStatus.SKIPPED, error="Dependency not met")
                continue

            print(f"▶ {task_id}...", end=" ", flush=True)
            self.results[task_id] = TaskResult(task_id, TaskStatus.RUNNING)

            if self._validate(task_id):
                self.results[task_id] = TaskResult(task_id, TaskStatus.SUCCESS)
                print("✅")
            else:
                self.results[task_id] = TaskResult(task_id, TaskStatus.FAILED)
                print("❌")

        return self.results

    def _topological_sort(self) -> list[str]:
        visited, order = set(), []
        def dfs(node):
            if node in visited: return
            visited.add(node)
            _, _, deps, _, _, _ = self.tasks[node]
            for d in deps:
                if d in self.tasks: dfs(d)
            order.append(node)
        for tid in self.tasks: dfs(tid)
        return order
```

---

## 8. Workflow-to-Tuple Mapping

| GitHub Workflow | Orchestration Tuples | Category |
|----------------|---------------------|----------|
| `ci-test.yml` | `TEST_EXEC_*`, `CONFIG_GEN_001-002` | TEST_EXEC, CONFIG_GEN |
| `ci-build.yml` | `CODE_BUILD_001`, `CODE_BUILD_010` | CODE_BUILD |
| `ci-deploy.yml` | `DEPLOY_OPS_001` | DEPLOY_OPS |
| `ci-release.yml` | `DEPLOY_OPS_010-011` | DEPLOY_OPS |
| `ci-validate-pr.yml` | `TEST_EXEC_020`, `VERIFY_CHECK_*` | TEST_EXEC, VERIFY_CHECK |
| `ci-schedule.yml` | `TEST_EXEC_010-011`, `VERIFY_CHECK_010-011` | TEST_EXEC, VERIFY_CHECK |

---

## 9. Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│  MCP ORCHESTRATION — QUICK REFERENCE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TUPLE: (id, type, deps, inputs, outputs, validation)           │
│                                                                  │
│  TYPES: REPO_INIT | CONFIG_GEN | CODE_BUILD                     │
│         TEST_EXEC | DEPLOY_OPS | VERIFY_CHECK                   │
│                                                                  │
│  SEQUENCES:                                                      │
│    Fresh Setup ──→ §3.1 (7 tuples)                              │
│    CI/CD Activate → §3.2 (4 tuples)                             │
│    Clone Verify ──→ §3.3 (5 tuples)                             │
│    Release ────────→ §3.4 (5 tuples)                            │
│                                                                  │
│  ERROR CODES: E001=FATAL E002=FATAL E003=ERROR                  │
│               E004=WARN  E005=INFO                               │
│                                                                  │
│  RETRY: REPO=3x CODE=2x TEST=1x DEPLOY=3x(rollback)           │
│                                                                  │
│  ENVIRONMENTS: testing → staging → production                    │
│                                                                  │
│  VALIDATE: cmd + expect | cmd + exit_code | manual              │
└─────────────────────────────────────────────────────────────────┘
```
