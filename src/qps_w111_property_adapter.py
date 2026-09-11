"""QPS W111 admission guard for the legacy local helium polynomial.

This module does not claim REFPROP/HEPAK equivalence. It prevents the existing
project-local polynomial from being used outside the narrow low-temperature,
near-1-bar envelope until independent cross-validation is available.
"""
from __future__ import annotations

from dataclasses import dataclass

from physics_validator import HeliumPropertyEngine


@dataclass(frozen=True)
class AdmissionEnvelope:
    temperature_min_K: float = 4.0
    temperature_max_K: float = 10.0
    pressure_min_bar: float = 0.95
    pressure_max_bar: float = 1.05

    def contains(self, temperature_K: float, pressure_bar: float) -> bool:
        return (
            self.temperature_min_K <= temperature_K <= self.temperature_max_K
            and self.pressure_min_bar <= pressure_bar <= self.pressure_max_bar
        )


class QuarantinedHeliumPropertyAdapter:
    authority_scope = "COMPATIBILITY_REFERENCE"
    engineering_promotion_forbidden = True
    source_identity_status = "UNVERIFIED_PROVENANCE_LOCAL_POLYNOMIAL"

    def __init__(self, envelope: AdmissionEnvelope | None = None) -> None:
        self.envelope = envelope or AdmissionEnvelope()
        self._legacy = HeliumPropertyEngine()

    def get_enthalpy_j_g(self, temperature_K: float, pressure_bar: float) -> float:
        if not self.envelope.contains(temperature_K, pressure_bar):
            raise ValueError(
                "QPS_W111_PROPERTY_ADMISSION_REJECT: legacy polynomial is admitted only "
                f"for {self.envelope.temperature_min_K}-{self.envelope.temperature_max_K} K "
                f"and {self.envelope.pressure_min_bar}-{self.envelope.pressure_max_bar} bar; "
                "general P-T helium property use requires an independently validated engine."
            )
        return self._legacy.get_enthalpy(temperature_K, pressure_bar)


def self_check() -> dict[str, object]:
    adapter = QuarantinedHeliumPropertyAdapter()
    h42 = adapter.get_enthalpy_j_g(4.2, 1.0)
    h45 = adapter.get_enthalpy_j_g(4.5, 1.0)
    warm_rejected = False
    try:
        adapter.get_enthalpy_j_g(298.0, 1.05)
    except ValueError:
        warm_rejected = True
    assert warm_rejected, "warm HP state must be rejected by the legacy approximation adapter"
    return {
        "status": "PASS",
        "authority_scope": adapter.authority_scope,
        "engineering_promotion_forbidden": adapter.engineering_promotion_forbidden,
        "source_identity_status": adapter.source_identity_status,
        "h_4p2K_1bar_j_g_legacy": h42,
        "h_4p5K_1bar_j_g_legacy": h45,
        "warm_HP_298K_rejected": warm_rejected,
        "interpretation": "execution/provenance guard only; values are not QPS property acceptance evidence",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_check(), indent=2, sort_keys=True))
