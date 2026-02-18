# cycles/rankine_basic.py
import numpy as np
import pandas as pd
from iapws import IAPWS97

def _safe_quality(st):
    # iapws sets x for two-phase; for superheated/compressed it may be None
    try:
        x = st.x
        if x is None:
            return None
        if np.isnan(x):
            return None
        return float(x)
    except Exception:
        return None

def rankine_ideal(
    Pc_kPa=10.0,          # condenser pressure
    Pb_kPa=8000.0,        # boiler pressure
    T3_C=None             # if None => saturated vapor at Pb, else superheated at T3_C
):
    """
    Ideal Rankine cycle (isentropic pump + isentropic turbine).
    Units:
      - inputs Pc_kPa, Pb_kPa
      - T3_C optional
    Returns:
      states_df, metrics, dome_df (for T-s saturation dome plotting)
    """
    if Pc_kPa <= 0 or Pb_kPa <= 0:
        raise ValueError("Pressures must be > 0")
    if Pb_kPa <= Pc_kPa:
        raise ValueError("Boiler pressure must be > condenser pressure")

    Pc = Pc_kPa / 1000.0  # MPa
    Pb = Pb_kPa / 1000.0  # MPa

    # --- State 1: saturated liquid at condenser pressure ---
    st1 = IAPWS97(P=Pc, x=0)  # sat liquid
    h1, s1, T1, v1 = st1.h, st1.s, st1.T, st1.v  # h(kJ/kg), s(kJ/kgK), T(K), v(m3/kg)

    # --- State 2: pump to boiler pressure (ideal pump) ---
    # Pump work approx: wp = v1 * (P2-P1); but P in kPa -> convert to kJ/kg via kPa*m3/kg = kJ/kg
    dP_kPa = Pb_kPa - Pc_kPa
    wp = v1 * dP_kPa
    h2 = h1 + wp

    # Find state2 using P & h (compressed liquid)
    st2 = IAPWS97(P=Pb, h=h2)
    T2, s2, v2 = st2.T, st2.s, st2.v

    # --- State 3: boiler outlet ---
    if T3_C is None:
        st3 = IAPWS97(P=Pb, x=1)  # saturated vapor
    else:
        st3 = IAPWS97(P=Pb, T=(T3_C + 273.15))  # superheated
    h3, s3, T3, v3 = st3.h, st3.s, st3.T, st3.v

    # --- State 4: turbine to condenser pressure (ideal isentropic expansion) ---
    st4 = IAPWS97(P=Pc, s=s3)
    h4, s4, T4, v4 = st4.h, st4.s, st4.T, st4.v

    # --- Performance ---
    wt = h3 - h4
    wnet = wt - wp
    qin = h3 - h2
    qout = h4 - h1
    eta = wnet / qin

    states = pd.DataFrame({
        "State": [1, 2, 3, 4],
        "P_kPa": [Pc_kPa, Pb_kPa, Pb_kPa, Pc_kPa],
        "T_K":   [T1, T2, T3, T4],
        "h_kJ_per_kg": [h1, h2, h3, h4],
        "s_kJ_per_kgK": [s1, s2, s3, s4],
        "v_m3_per_kg": [v1, v2, v3, v4],
        "x_quality": [_safe_quality(st1), _safe_quality(st2), _safe_quality(st3), _safe_quality(st4)],
    })

    metrics = {
        "wp_kJ_per_kg": wp,
        "wt_kJ_per_kg": wt,
        "Wnet_kJ_per_kg": wnet,
        "Qin_kJ_per_kg": qin,
        "eta_th": eta,
        "turbine_exit_quality_x": _safe_quality(st4),
    }

    # --- Saturation dome for T-s plot ---
    # Build dome between Pc and Pb (log-spaced for nicer coverage)
    Ps = np.geomspace(Pc, Pb, 80)
    Ts = []
    sf = []
    sg = []
    for P in Ps:
        f = IAPWS97(P=P, x=0)
        g = IAPWS97(P=P, x=1)
        Ts.append(f.T)      # same T at sat
        sf.append(f.s)
        sg.append(g.s)

    dome_df = pd.DataFrame({
        "T_K": Ts,
        "s_f": sf,
        "s_g": sg
    })

    return states, metrics, dome_df
