# cycles/rankine_reheat.py
import numpy as np
import pandas as pd
from iapws import IAPWS97

def _safe_quality(st):
    try:
        x = st.x
        if x is None:
            return None
        if np.isnan(x):
            return None
        return float(x)
    except Exception:
        return None

def rankine_reheat_ideal(
    Pc_kPa=10.0,          # condenser pressure
    Pb_kPa=8000.0,        # boiler pressure
    Pr_kPa=1500.0,        # reheat pressure (between Pb and Pc)
    T3_C=450.0,           # main steam temp at Pb
    T5_C=450.0            # reheat outlet temp at Pr
):
    """
    Ideal Rankine with reheat:
      1: sat liquid at Pc
      2: after pump to Pb (ideal)
      3: superheated at Pb, T3
      4: after HP turbine to Pr (isentropic)
      5: after reheat at Pr, T5
      6: after LP turbine to Pc (isentropic)
      6->1: condensation at Pc (to sat liquid)

    Returns: states_df, metrics, dome_df
    """
    if Pc_kPa <= 0 or Pb_kPa <= 0 or Pr_kPa <= 0:
        raise ValueError("Pressures must be > 0")
    if not (Pb_kPa > Pr_kPa > Pc_kPa):
        raise ValueError("Need Pb > Pr > Pc")

    Pc = Pc_kPa / 1000.0  # MPa
    Pb = Pb_kPa / 1000.0  # MPa
    Pr = Pr_kPa / 1000.0  # MPa

    # --- 1: sat liquid at Pc ---
    st1 = IAPWS97(P=Pc, x=0)
    h1, s1, T1, v1 = st1.h, st1.s, st1.T, st1.v

    # --- 2: pump to Pb (ideal pump work) ---
    wp = v1 * (Pb_kPa - Pc_kPa)  # kJ/kg (since kPa*m3/kg = kJ/kg)
    h2 = h1 + wp
    st2 = IAPWS97(P=Pb, h=h2)
    T2, s2, v2 = st2.T, st2.s, st2.v

    # --- 3: boiler outlet (superheated) ---
    st3 = IAPWS97(P=Pb, T=T3_C + 273.15)
    h3, s3, T3, v3 = st3.h, st3.s, st3.T, st3.v

    # --- 4: HP turbine to Pr (isentropic) ---
    st4 = IAPWS97(P=Pr, s=s3)
    h4, s4, T4, v4 = st4.h, st4.s, st4.T, st4.v

    # --- 5: Reheat at Pr to T5 ---
    st5 = IAPWS97(P=Pr, T=T5_C + 273.15)
    h5, s5, T5, v5 = st5.h, st5.s, st5.T, st5.v

    # --- 6: LP turbine to Pc (isentropic) ---
    st6 = IAPWS97(P=Pc, s=s5)
    h6, s6, T6, v6 = st6.h, st6.s, st6.T, st6.v

    # --- Performance ---
    wt_hp = h3 - h4
    wt_lp = h5 - h6
    wt = wt_hp + wt_lp
    wnet = wt - wp

    qin_boiler = h3 - h2
    qin_reheat = h5 - h4
    qin_total = qin_boiler + qin_reheat

    eta = wnet / qin_total

    states = pd.DataFrame({
        "State": [1, 2, 3, 4, 5, 6],
        "P_kPa": [Pc_kPa, Pb_kPa, Pb_kPa, Pr_kPa, Pr_kPa, Pc_kPa],
        "T_K":   [T1, T2, T3, T4, T5, T6],
        "h_kJ_per_kg": [h1, h2, h3, h4, h5, h6],
        "s_kJ_per_kgK": [s1, s2, s3, s4, s5, s6],
        "v_m3_per_kg": [v1, v2, v3, v4, v5, v6],
        "x_quality": [_safe_quality(st1), _safe_quality(st2), _safe_quality(st3),
                      _safe_quality(st4), _safe_quality(st5), _safe_quality(st6)],
    })

    metrics = {
        "wp_kJ_per_kg": wp,
        "wt_hp_kJ_per_kg": wt_hp,
        "wt_lp_kJ_per_kg": wt_lp,
        "wt_total_kJ_per_kg": wt,
        "Wnet_kJ_per_kg": wnet,
        "Qin_boiler_kJ_per_kg": qin_boiler,
        "Qin_reheat_kJ_per_kg": qin_reheat,
        "Qin_total_kJ_per_kg": qin_total,
        "eta_th": eta,
        "turbine_exit_quality_x6": _safe_quality(st6),
    }

    # saturation dome for T-s plot
    Ps = np.geomspace(Pc, Pb, 90)
    Ts, sf, sg = [], [], []
    for P in Ps:
        f = IAPWS97(P=P, x=0)
        g = IAPWS97(P=P, x=1)
        Ts.append(f.T)
        sf.append(f.s)
        sg.append(g.s)
    dome_df = pd.DataFrame({"T_K": Ts, "s_f": sf, "s_g": sg})

    return states, metrics, dome_df
