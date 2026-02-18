import numpy as np
import pandas as pd

def carnot_cycle(Th_K=600.0, Tc_K=300.0, delta_s_kJkgK=1.0, mode="engine",
                 gamma=1.4, R_kJkgK=0.287, v1=1.0):
    """
    Carnot cycle.
    - T–s is exact by definition (rectangle).
    - P–v is shown as an *ideal-gas reversible Carnot* (conceptual), using gamma, R and a scale v1.
    """
    if Th_K <= Tc_K:
        raise ValueError("Th must be > Tc for Carnot cycle.")
    if delta_s_kJkgK <= 0:
        raise ValueError("Δs must be > 0")

    # T–s rectangle (exact for Carnot representation)
    s1 = 0.0
    s2 = float(delta_s_kJkgK)

    # Build ideal-gas volumes using:
    # Isothermal: Δs = R ln(v2/v1)  => v2/v1 = exp(Δs/R)
    v2 = v1 * np.exp(delta_s_kJkgK / R_kJkgK)

    # Isentropic: T v^(gamma-1) = const  => v3 = v2*(Th/Tc)^(1/(gamma-1))
    factor = (Th_K / Tc_K) ** (1.0 / (gamma - 1.0))
    v3 = v2 * factor
    v4 = v1 * factor

    # Pressures from ideal gas: P = RT / v
    P1 = (R_kJkgK * Th_K) / v1
    P2 = (R_kJkgK * Th_K) / v2
    P3 = (R_kJkgK * Tc_K) / v3
    P4 = (R_kJkgK * Tc_K) / v4

    states = pd.DataFrame({
        "State": [1, 2, 3, 4],
        "T_K":   [Th_K, Th_K, Tc_K, Tc_K],
        "s_kJ_per_kgK": [s1, s2, s2, s1],
        "v_m3_per_kg":  [v1, v2, v3, v4],
        "P_kPa":        [P1, P2, P3, P4],
    })

    Qh = Th_K * (s2 - s1)
    Qc = Tc_K * (s2 - s1)
    Wnet = Qh - Qc

    if mode == "engine":
        eta = 1.0 - (Tc_K / Th_K)
        metrics = {"mode": "Heat engine", "Q_in_kJ_per_kg": Qh, "Q_out_kJ_per_kg": Qc,
                   "W_net_kJ_per_kg": Wnet, "eta_th": eta}
    elif mode == "refrigerator":
        metrics = {"mode": "Refrigerator", "Q_cold_kJ_per_kg": Qc, "W_in_kJ_per_kg": Wnet,
                   "COP_R": Qc / Wnet}
    elif mode == "heat_pump":
        metrics = {"mode": "Heat pump", "Q_hot_kJ_per_kg": Qh, "W_in_kJ_per_kg": Wnet,
                   "COP_HP": Qh / Wnet}
    else:
        raise ValueError("mode must be one of: engine, refrigerator, heat_pump")

    return states, metrics
