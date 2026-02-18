import numpy as np
import pandas as pd

def brayton_ideal(P1_kPa=100.0, T1_K=300.0, rp=10.0, T3_K=1400.0,
                 gamma=1.4, cp_kJkgK=1.004, R_kJkgK=0.287):
    """
    Ideal Brayton cycle (air-standard).
    Adds v and relative entropy s_rel so we can plot P–v and T–s.
    """
    if rp <= 1:
        raise ValueError("Pressure ratio rp must be > 1")

    P2 = P1_kPa * rp
    P3 = P2
    P4 = P1_kPa

    exp = (gamma - 1.0) / gamma
    T2 = T1_K * (rp ** exp)
    T4 = T3_K * ((1.0 / rp) ** exp)

    # v = RT/P (ideal gas)
    v1 = (R_kJkgK * T1_K) / P1_kPa
    v2 = (R_kJkgK * T2) / P2
    v3 = (R_kJkgK * T3_K) / P3
    v4 = (R_kJkgK * T4) / P4

    # Relative entropy (set s1 = 0)
    # ds = cp ln(T2/T1) - R ln(P2/P1)
    s1 = 0.0
    s2 = s1 + cp_kJkgK * np.log(T2 / T1_K) - R_kJkgK * np.log(P2 / P1_kPa)
    s3 = s2 + cp_kJkgK * np.log(T3_K / T2)  # constant pressure (P3=P2)
    s4 = s3 + cp_kJkgK * np.log(T4 / T3_K) - R_kJkgK * np.log(P4 / P3)

    Wc = cp_kJkgK * (T2 - T1_K)
    Wt = cp_kJkgK * (T3_K - T4)
    Wnet = Wt - Wc

    Qin = cp_kJkgK * (T3_K - T2)
    Qout = cp_kJkgK * (T4 - T1_K)
    eta = 1.0 - (Qout / Qin)

    states = pd.DataFrame({
        "State": [1, 2, 3, 4],
        "P_kPa": [P1_kPa, P2, P3, P4],
        "T_K":   [T1_K, T2, T3_K, T4],
        "v_m3_per_kg": [v1, v2, v3, v4],
        "s_rel_kJ_per_kgK": [s1, s2, s3, s4],
    })

    metrics = {
        "Wc_kJ_per_kg": Wc,
        "Wt_kJ_per_kg": Wt,
        "Wnet_kJ_per_kg": Wnet,
        "Qin_kJ_per_kg": Qin,
        "eta_th": eta,
        "back_work_ratio": Wc / Wt
    }

    return states, metrics
