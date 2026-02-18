import numpy as np
import pandas as pd

def diesel_cycle(
    T1_K=300.0, P1_kPa=100.0,
    r=18.0, rc=2.0,          # r = compression ratio, rc = cutoff ratio (v3/v2)
    gamma=1.4, R_kJkgK=0.287
):
    """
    Air-standard Diesel cycle (ideal gas, constant gamma).
    Processes:
      1-2: isentropic compression
      2-3: heat addition at constant pressure (cutoff ratio rc = v3/v2)
      3-4: isentropic expansion
      4-1: heat rejection at constant volume

    Returns states_df with P,T,v,s_rel and metrics.
    """
    if r <= 1:
        raise ValueError("Compression ratio r must be > 1")
    if rc <= 1:
        raise ValueError("Cutoff ratio rc must be > 1")

    cv = R_kJkgK / (gamma - 1.0)
    cp = gamma * cv

    # choose v1 scale from ideal gas
    v1 = (R_kJkgK * T1_K) / P1_kPa
    v2 = v1 / r

    # 1-2 isentropic
    T2 = T1_K * (r ** (gamma - 1.0))
    P2 = P1_kPa * (r ** gamma)

    # 2-3 constant pressure, v3 = rc*v2, so T3/T2 = v3/v2 = rc
    v3 = rc * v2
    T3 = T2 * rc
    P3 = P2

    # 3-4 isentropic expansion to v4 = v1
    v4 = v1
    T4 = T3 * ((v3 / v4) ** (gamma - 1.0))
    P4 = P3 * ((v3 / v4) ** gamma)

    # heat/work
    Qin = cp * (T3 - T2)     # constant pressure
    Qout = cv * (T4 - T1_K)  # constant volume
    Wnet = Qin - Qout
    eta = 1.0 - (Qout / Qin)

    # relative entropy (set s1=0)
    s1 = 0.0
    s2 = s1  # isentropic
    # constant pressure: ds = cp ln(T3/T2)
    s3 = s2 + cp * np.log(T3 / T2)
    s4 = s3  # isentropic

    states = pd.DataFrame({
        "State": [1, 2, 3, 4],
        "P_kPa": [P1_kPa, P2, P3, P4],
        "T_K":   [T1_K, T2, T3, T4],
        "v_m3_per_kg": [v1, v2, v3, v4],
        "s_rel_kJ_per_kgK": [s1, s2, s3, s4],
    })

    metrics = {
        "eta_th": eta,
        "Qin_kJ_per_kg": Qin,
        "Qout_kJ_per_kg": Qout,
        "Wnet_kJ_per_kg": Wnet,
        "compression_ratio_r": r,
        "cutoff_ratio_rc": rc,
    }

    return states, metrics
