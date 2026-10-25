<#
.SYNOPSIS
    GBOGEB session 2026-05-22 integration — Windows sync & smoke-test script.

.DESCRIPTION
    For each of the user's repo roots (C:\repos and C:\DEV), this script:
      1. Finds (or clones) GBOGEB/ABACUS, CODEX, cryoplant-project, document-organization-system
      2. Fetches all branches
      3. Checks out the new integration PR branches
      4. Runs the session smoke tests (pytest)
      5. Optionally activates the staged CI workflows (*.yml.txt -> .github/workflows/*.yml)

    No tokens are embedded. Authentication relies on your existing `gh auth login`
    and/or Git Credential Manager. Run from an elevated-ish PowerShell where `git`
    (and optionally `gh`, `python`) are on PATH.

.NOTES
    Integration PRs:
      ABACUS            #2433  branch integrate/session-2026-05-22-governance
      CODEX             #1189  branch integrate/session-2026-05-22-assets
      cryoplant-project #2085  branch integrate/session-2026-05-22-hooks
#>

[CmdletBinding()]
param(
    [string[]] $RepoRoots = @('C:\repos', 'C:\DEV'),
    [switch]   $ActivateWorkflows,   # if set, prompts to copy *.yml.txt -> .github/workflows/*.yml
    [switch]   $SkipTests
)

$ErrorActionPreference = 'Stop'

# repo -> integration branch
$Repos = [ordered]@{
    'ABACUS'                       = 'integrate/session-2026-05-22-governance'
    'CODEX'                        = 'integrate/session-2026-05-22-assets'
    'cryoplant-project'            = 'integrate/session-2026-05-22-hooks'
    'document-organization-system' = ''   # reference only, no PR branch
}

function Write-Section($msg) { Write-Host "`n==== $msg ====" -ForegroundColor Cyan }

function Resolve-RepoPath {
    param([string]$RepoName)
    foreach ($root in $RepoRoots) {
        $candidate = Join-Path $root $RepoName
        if (Test-Path (Join-Path $candidate '.git')) { return $candidate }
    }
    return $null
}

function Clone-Repo {
    param([string]$RepoName)
    $targetRoot = $RepoRoots | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $targetRoot) {
        $targetRoot = $RepoRoots[0]
        New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
    }
    $dest = Join-Path $targetRoot $RepoName
    Write-Host "Cloning GBOGEB/$RepoName into $dest ..." -ForegroundColor Yellow
    git clone "https://github.com/GBOGEB/$RepoName.git" $dest
    return $dest
}

function Invoke-SmokeTests {
    param([string]$RepoPath, [string]$RepoName)
    if ($SkipTests) { return }
    Push-Location $RepoPath
    try {
        $py = Get-Command python -ErrorAction SilentlyContinue
        if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
        if (-not $py) { Write-Warning "python not found on PATH; skipping tests for $RepoName"; return }

        switch ($RepoName) {
            'ABACUS' {
                $base = 'integration/gbogeb_session'
                foreach ($sub in @('governance/tests','mcp_server/tests','tests')) {
                    $p = Join-Path $base $sub
                    if (Test-Path $p) { Write-Host "pytest $p" -ForegroundColor Green; & $py.Source -m pytest $p -q }
                }
            }
            'CODEX' {
                $p = 'integrations/gbogeb_session/assets_governance/tests'
                if (Test-Path $p) { Write-Host "pytest $p" -ForegroundColor Green; & $py.Source -m pytest $p -q }
            }
            'cryoplant-project' {
                Write-Host "cryoplant PR is a pointer-only hook; nothing to test." -ForegroundColor DarkGray
            }
            default { Write-Host "No session smoke tests for $RepoName." -ForegroundColor DarkGray }
        }
    } finally { Pop-Location }
}

function Activate-Workflows {
    param([string]$RepoPath, [string]$RepoName)
    if (-not $ActivateWorkflows) { return }
    # staged workflow references live under the session namespace
    $patterns = @(
        'integration/gbogeb_session/governance/docs/ci-workflows-reference',
        'integrations/gbogeb_session/assets_governance/.github/workflows'
    )
    foreach ($rel in $patterns) {
        $refDir = Join-Path $RepoPath $rel
        if (-not (Test-Path $refDir)) { continue }
        $txts = Get-ChildItem -Path $refDir -Filter '*.yml.txt' -ErrorAction SilentlyContinue
        if (-not $txts) { continue }
        Write-Host "`nFound $($txts.Count) staged workflow(s) in $rel" -ForegroundColor Yellow
        $ans = Read-Host "Activate (copy to .github/workflows/*.yml)? Requires a PAT with 'workflow' scope to push. [y/N]"
        if ($ans -notmatch '^[Yy]') { continue }
        $wfDir = Join-Path $RepoPath '.github/workflows'
        New-Item -ItemType Directory -Force -Path $wfDir | Out-Null
        foreach ($t in $txts) {
            $name = $t.Name -replace '\.txt$',''
            Copy-Item $t.FullName (Join-Path $wfDir $name) -Force
            Write-Host "  activated $name" -ForegroundColor Green
        }
        Write-Host "  -> review, then: git add .github/workflows; git commit -m 'ci: activate session workflows'; git push" -ForegroundColor Cyan
    }
}

Write-Host "GBOGEB Session 2026-05-22 — Windows sync" -ForegroundColor Magenta
Write-Host "Repo roots searched: $($RepoRoots -join ', ')"

foreach ($repo in $Repos.Keys) {
    $branch = $Repos[$repo]
    Write-Section "$repo"

    $path = Resolve-RepoPath -RepoName $repo
    if (-not $path) {
        Write-Host "Not found locally." -ForegroundColor Yellow
        $do = Read-Host "Clone GBOGEB/$repo now? [Y/n]"
        if ($do -match '^[Nn]') { Write-Host "Skipped $repo."; continue }
        $path = Clone-Repo -RepoName $repo
    } else {
        Write-Host "Found at $path" -ForegroundColor Green
    }

    Push-Location $path
    try {
        git fetch --all --prune
        if ($branch) {
            Write-Host "Checking out $branch" -ForegroundColor Green
            git checkout $branch 2>$null
            if ($LASTEXITCODE -ne 0) { git checkout -b $branch "origin/$branch" }
            git pull --ff-only origin $branch
        } else {
            git checkout main 2>$null; git pull --ff-only origin main
        }
    } finally { Pop-Location }

    Invoke-SmokeTests  -RepoPath $path -RepoName $repo
    Activate-Workflows -RepoPath $path -RepoName $repo
}

Write-Section "DONE"
Write-Host "Integration PRs to review:"
Write-Host "  ABACUS            #2433  https://github.com/GBOGEB/ABACUS/pull/2433"
Write-Host "  CODEX             #1189  https://github.com/GBOGEB/CODEX/pull/1189"
Write-Host "  cryoplant-project #2085  https://github.com/GBOGEB/cryoplant-project/pull/2085"
