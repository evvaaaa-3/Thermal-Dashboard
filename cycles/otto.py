import numpy as np
import pandas as pd

def otto_cycle(T1_K=300.0, P1_kPa=100.0, r=8.0, T3_K=1800.0, gamma=1.4, R_kJkgK=0.287):
    """
    Air-standard Otto cycle (ideal gas, constant gamma).
    Processes:
      1-2: isentropic compression
      2-3: heat addition at constant volume
      3-4: isentropic expansion
      4-1: heat rejection at constant volume

    Returns:
      states_df with P,T,v,s (relative)
      metrics dict
    """

    if r <= 1:
        raise ValueError("Compression ratio r must be > 1")
    if T3_K <= T1_K:
        raise ValueError("T3 must be > T1")

    cv = R_kJkgK / (gamma - 1.0)
    cp = gamma * cv

    # Choose a convenient v1 (scale doesn't affect efficiency). Use ideal gas: P v = R T.
    v1 = (R_kJkgK * T1_K) / P1_kPa  # m^3/kg
    v2 = v1 / r

    # 1-2 isentropic: T2 = T1 * r^(gamma-1), P2 = P1 * r^gamma
    T2 = T1_K * (r ** (gamma - 1.0))
    P2 = P1_kPa * (r ** gamma)

    # 2-3 constant volume: v3=v2, T3 given => P3 from ideal gas
    v3 = v2
    P3 = (R_kJkgK * T3_K) / v3

    # 3-4 isentropic expansion back to v4=v1
    v4 = v1
    T4 = T3_K / (r ** (gamma - 1.0))
    P4 = P3 / (r ** gamma)

    # Heat/work (kJ/kg)
    Qin = cv * (T3_K - T2)
    Qout = cv * (T4 - T1_K)
    Wnet = Qin - Qout
    eta = 1.0 - (Qout / Qin)

    # Relative entropy (choose s1=0). For ideal gas:
    # ds = cp ln(T2/T1) - R ln(P2/P1)
    # For isentropic steps, ds=0 (numerically ~0). For constant V:
    # ds = cv ln(T3/T2) (since v constant)
    s1 = 0.0
    s2 = s1  # isentropic
    s3 = s2 + cv * np.log(T3_K / T2)
    s4 = s3  # isentropic
    # Step 4-1 at constant volume: s1 = s4 + cv ln(T1/T4) -> should return to ~0

    states = pd.DataFrame({
        "State": [1, 2, 3, 4],
        "P_kPa": [P1_kPa, P2, P3, P4],
        "T_K":   [T1_K, T2, T3_K, T4],
        "v_m3_per_kg": [v1, v2, v3, v4],
        "s_rel_kJ_per_kgK": [s1, s2, s3, s4]
    })

    metrics = {
        "eta_th": eta,
        "Qin_kJ_per_kg": Qin,
        "Qout_kJ_per_kg": Qout,
        "Wnet_kJ_per_kg": Wnet,
        "compression_ratio_r": r
    }

    return states, metrics
