import numpy as np
import pandas as pd

def dual_cycle(
    T1_K=300.0, P1_kPa=100.0,
    r=14.0, alpha=1.5, rc=1.3,   # alpha = P3/P2 (const-V heat add), rc = v4/v3 (const-P heat add)
    gamma=1.4, R_kJkgK=0.287
):
    """
    Air-standard Dual (mixed) cycle.
    Processes:
      1-2: isentropic compression
      2-3: heat add at constant volume (pressure ratio alpha = P3/P2)
      3-4: heat add at constant pressure (cutoff ratio rc = v4/v3)
      4-5: isentropic expansion to v5 = v1
      5-1: heat rejection at constant volume

    Returns states_df with 5 states and metrics.
    """
    if r <= 1:
        raise ValueError("Compression ratio r must be > 1")
    if alpha <= 1:
        raise ValueError("alpha (P3/P2) must be > 1")
    if rc <= 1:
        raise ValueError("rc (v4/v3) must be > 1")

    cv = R_kJkgK / (gamma - 1.0)
    cp = gamma * cv

    v1 = (R_kJkgK * T1_K) / P1_kPa
    v2 = v1 / r

    # 1-2 isentropic
    T2 = T1_K * (r ** (gamma - 1.0))
    P2 = P1_kPa * (r ** gamma)

    # 2-3 constant volume: P3 = alpha*P2 -> T3 = alpha*T2
    P3 = alpha * P2
    T3 = alpha * T2
    v3 = v2

    # 3-4 constant pressure: v4 = rc*v3 -> T4 = rc*T3, P4 = P3
    v4 = rc * v3
    T4 = rc * T3
    P4 = P3

    # 4-5 isentropic expansion to v5 = v1
    v5 = v1
    T5 = T4 * ((v4 / v5) ** (gamma - 1.0))
    P5 = P4 * ((v4 / v5) ** gamma)

    # heat transfers
    Qin_cv = cv * (T3 - T2)       # 2-3
    Qin_cp = cp * (T4 - T3)       # 3-4
    Qin = Qin_cv + Qin_cp
    Qout = cv * (T5 - T1_K)       # 5-1
    Wnet = Qin - Qout
    eta = 1.0 - (Qout / Qin)

    # relative entropy s (s1=0)
    s1 = 0.0
    s2 = s1
    s3 = s2 + cv * np.log(T3 / T2)    # const V
    s4 = s3 + cp * np.log(T4 / T3)    # const P
    s5 = s4

    states = pd.DataFrame({
        "State": [1, 2, 3, 4, 5],
        "P_kPa": [P1_kPa, P2, P3, P4, P5],
        "T_K":   [T1_K, T2, T3, T4, T5],
        "v_m3_per_kg": [v1, v2, v3, v4, v5],
        "s_rel_kJ_per_kgK": [s1, s2, s3, s4, s5],
    })

    metrics = {
        "eta_th": eta,
        "Qin_kJ_per_kg": Qin,
        "Qout_kJ_per_kg": Qout,
        "Wnet_kJ_per_kg": Wnet,
        "compression_ratio_r": r,
        "alpha_P3_over_P2": alpha,
        "cutoff_ratio_rc": rc,
    }

    return states, metrics
