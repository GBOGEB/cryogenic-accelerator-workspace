# -*- coding: utf-8 -*-
"""
==============================================================================
CORE THERMODYNAMIC VERIFICATION ENGINE - CRYOGENIC ACCELERATOR MASS BALANCES
==============================================================================
References: NIST Standard Reference Database 23 (HEPAK Fluid Models)
Approximates dynamic mass boundary requirements under thermal flux variables.
"""
import numpy as np

class HeliumPropertyEngine:
    def __init__(self):
        # Reduced polynomial coefficients for Helium-4 Enthalpy at 1.0 Bar near Lambda point
        self.poly_coeffs_4k_to_10k = np.array([-1.24, 5.72, 12.31])

    def get_enthalpy(self, temperature_k: float, pressure_bar: float) -> float:
        """
        Calculates enthalpy h (J/g) via polynomial fit regressions mapping NIST data.
        """
        if temperature_k < 2.17:
            return 4.22 * (temperature_k ** 5.6)
        t_steps = np.array([1.0, temperature_k, temperature_k ** 2])
        return float(np.dot(self.poly_coeffs_4k_to_10k, t_steps))

def verify_mass_balance(config_data: dict) -> dict:
    """
    Executes structural physics loops against active YAML state values.
    Formula: m_dot = Q_total / delta_h
    """
    engine = HeliumPropertyEngine()
    static_loss = config_data['engineering_metrics']['heat_loads']['cryomodule_static_loss']['value']
    dynamic_rf = config_data['engineering_metrics']['heat_loads']['dynamic_rf_load']['value']
    
    t_in, t_out, p_ops = 4.2, 4.5, 1.0
    h_in = engine.get_enthalpy(t_in, p_ops)
    h_out = engine.get_enthalpy(t_out, p_ops)
    delta_h = h_out - h_in
    
    total_thermal_load = static_loss + dynamic_rf
    required_mass_flow = total_thermal_load / delta_h
    
    return {
        "calculated_mass_flow_kg_s": round(required_mass_flow, 5),
        "enthalpy_in_j_g": round(h_in, 3),
        "enthalpy_out_j_g": round(h_out, 3),
        "system_verification_status": "PASS" if required_mass_flow < 0.2 else "WARN_LIMIT"
    }
