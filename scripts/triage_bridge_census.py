#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
TERMS=['MCP','orchestration','manifest','extraction','QPLANT','RTM','ABACUS','CODEX','cryoplant']
rows=[]
for p in sorted(ROOT.glob('*.md')):
    text=p.read_text(encoding='utf-8',errors='ignore')
    hits={t:len(re.findall(re.escape(t),text,re.I)) for t in TERMS}
    if any(hits.values()):
        rows.append({'path':p.name,'bytes':p.stat().st_size,'hits':hits})
print(json.dumps({'schema':'triage-accelerator-census/v0.1','authority':'DISCOVERY_ONLY','release_credit':False,'documents':rows,'document_count':len(rows)},sort_keys=True,indent=2))
