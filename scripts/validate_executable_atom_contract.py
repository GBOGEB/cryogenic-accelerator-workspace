#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'triage/EXECUTABLE_ATOM_CONTRACT_W02.yaml'

def fail(msg):
    raise SystemExit('FAIL: '+msg)

def main():
    d=yaml.safe_load(P.read_text(encoding='utf-8'))
    if d.get('schema')!='accelerator-executable-atom-contract/v0.1': fail('schema')
    atom=d.get('selected_atom',{})
    if atom.get('target_owner')!='GBOGEB/ABACUS': fail('target owner')
    if atom.get('authority_effect')!='NONE': fail('authority leakage')
    m=d.get('modernization',{})
    rejected=set(m.get('rejected_legacy_behaviour',[]))
    required_rejections={'embedded_hardcoded_requirement_to_test_mapping','echo_only_success_receipts','missing_or_stub_module_treated_as_success'}
    if not required_rejections.issubset(rejected): fail('legacy behavior not fully rejected')
    contract=m.get('executable_contract',{})
    required=set(contract.get('required_inputs',[]))
    if not {'source_manifest','source_sha256','target_manifest','target_sha','mapping_rows'}.issubset(required): fail('input contract incomplete')
    receipt=contract.get('receipt',{})
    if receipt.get('authority')!='EVIDENCE_ONLY' or receipt.get('release_credit') is not False or receipt.get('compliance_credit') is not False:
        fail('receipt boundary')
    print('PASS: accelerator design atom is now an executable hash-bound contract, not hardcoded live input')
    return 0

if __name__=='__main__':
    sys.exit(main())
