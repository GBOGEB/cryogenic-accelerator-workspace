"""Fail-closed dimensional guard for the legacy workspace mass-balance helper.

The legacy ``verify_mass_balance`` implementation remains useful as archaeology,
but its current input contract is not admissible as QPS engineering evidence:
``cryomodule_static_loss`` is W/m while ``dynamic_rf_load`` is W, and the
enthalpy delta is J/g while the returned field is labelled kg/s.

This guard intentionally does not invent a cryomodule length or silently apply a
1000x unit conversion. It proves that the ambiguity is detected and blocks
promotion until the missing geometry/units and an accepted property source are
bound.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml


def inspect_contract(config: dict) -> dict[str, object]:
    heat_loads = config["engineering_metrics"]["heat_loads"]
    static = heat_loads["cryomodule_static_loss"]
    dynamic = heat_loads["dynamic_rf_load"]

    findings: list[dict[str, str]] = []
    if static.get("unit") == "W/m" and dynamic.get("unit") == "W":
        findings.append(
            {
                "id": "CW-W111-03",
                "finding": "mixed_extensive_and_per_length_heat_loads",
                "effect": "static_W_per_m_cannot_be_added_to_dynamic_W_without_bound_length",
            }
        )

    findings.append(
        {
            "id": "CW-W111-04",
            "finding": "legacy_mass_flow_output_unit_mismatch",
            "effect": "W_divided_by_J_per_g_yields_g_per_s_not_kg_per_s",
        }
    )

    blocked = {item["id"] for item in findings} >= {"CW-W111-03", "CW-W111-04"}
    assert blocked, "known dimensional ambiguities must remain fail-closed until repaired from source"

    return {
        "status": "PASS_GUARD_BLOCKS_PROMOTION",
        "authority_scope": "DIMENSIONAL_AUDIT_ONLY",
        "engineering_promotion_forbidden": True,
        "findings": findings,
        "required_returns": [
            "cryomodule_length_or_total_static_heat_load_with_source",
            "explicit_mass_flow_output_unit_contract",
            "accepted_helium_property_source_and_state_pair",
        ],
        "prohibited_repairs": [
            "assume_cryomodule_length_equals_1m",
            "silently_relabel_or_rescale_without_contract",
            "promote_legacy_PASS_to_QPS_engineering_acceptance",
        ],
    }


def self_check() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "config" / "engineering_data.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    return inspect_contract(config)


if __name__ == "__main__":
    print(json.dumps(self_check(), indent=2, sort_keys=True))
