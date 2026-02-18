# cycles/refrigeration_vcr.py
import numpy as np
import pandas as pd
from CoolProp.CoolProp import PropsSI

def _try_quality(fluid, P_Pa, H_Jkg):
    # Quality is only meaningful in 2-phase region; CoolProp may throw otherwise.
    try:
        q = PropsSI("Q", "P", P_Pa, "H", H_Jkg, fluid)
        if q is None or np.isnan(q):
            return None
        return float(q)
    except Exception:
        return None

def vcr_ideal(
    fluid="R134a",
    Tevap_C=-10.0,
    Tcond_C=40.0,
    superheat_C=5.0,
    subcool_C=5.0
):
    """
    Ideal vapor-compression refrigeration cycle (basic).
    Uses saturation temps (Tevap, Tcond) to define evaporator/condenser pressures.
    Adds optional superheat at compressor inlet and subcool at condenser outlet.

    Returns: states_df, metrics, sat_df (for dome/lines on T-s and P-h)
    """
    Te = Tevap_C + 273.15
    Tc = Tcond_C + 273.15
    if Tc <= Te:
        raise ValueError("Tcond must be > Tevap")

    # Saturation pressures
    Pe = PropsSI("P", "T", Te, "Q", 1, fluid)  # Pa
    Pc = PropsSI("P", "T", Tc, "Q", 0, fluid)  # Pa

    # ---- State 1: compressor inlet (Pe, Te + superheat) ----
    T1 = Te + superheat_C
    H1 = PropsSI("H", "P", Pe, "T", T1, fluid)   # J/kg
    S1 = PropsSI("S", "P", Pe, "T", T1, fluid)   # J/kg-K
    V1 = PropsSI("V", "P", Pe, "T", T1, fluid)   # m3/kg
    Q1 = _try_quality(fluid, Pe, H1)

    # ---- State 2: compressor outlet (Pc, s = s1) ----
    H2 = PropsSI("H", "P", Pc, "S", S1, fluid)
    T2 = PropsSI("T", "P", Pc, "H", H2, fluid)
    S2 = PropsSI("S", "P", Pc, "H", H2, fluid)
    V2 = PropsSI("V", "P", Pc, "H", H2, fluid)
    Q2 = _try_quality(fluid, Pc, H2)

    # ---- State 3: condenser outlet (Pc, Tc - subcool) ----
    T3 = Tc - subcool_C
    H3 = PropsSI("H", "P", Pc, "T", T3, fluid)
    S3 = PropsSI("S", "P", Pc, "T", T3, fluid)
    V3 = PropsSI("V", "P", Pc, "T", T3, fluid)
    Q3 = _try_quality(fluid, Pc, H3)

    # ---- State 4: expansion valve outlet (Pe, h = h3) ----
    H4 = H3
    T4 = PropsSI("T", "P", Pe, "H", H4, fluid)
    S4 = PropsSI("S", "P", Pe, "H", H4, fluid)
    V4 = PropsSI("V", "P", Pe, "H", H4, fluid)
    Q4 = _try_quality(fluid, Pe, H4)

    # Convert to kPa, kJ/kg, kJ/kg-K
    def kPa(P): return P / 1000.0
    def kJ(H): return H / 1000.0
    def kJk(S): return S / 1000.0

    states = pd.DataFrame({
        "State": [1, 2, 3, 4],
        "P_kPa": [kPa(Pe), kPa(Pc), kPa(Pc), kPa(Pe)],
        "T_K":   [T1, T2, T3, T4],
        "h_kJ_per_kg": [kJ(H1), kJ(H2), kJ(H3), kJ(H4)],
        "s_kJ_per_kgK": [kJk(S1), kJk(S2), kJk(S3), kJk(S4)],
        "v_m3_per_kg": [V1, V2, V3, V4],
        "x_quality": [Q1, Q2, Q3, Q4],
    })

    # Performance (kJ/kg)
    w_comp = kJ(H2 - H1)
    q_in = kJ(H1 - H4)     # evaporator
    q_out = kJ(H2 - H3)    # condenser
    cop_r = q_in / w_comp

    metrics = {
        "fluid": fluid,
        "Pe_kPa": kPa(Pe),
        "Pc_kPa": kPa(Pc),
        "pressure_ratio": (Pc / Pe),
        "w_comp_kJ_per_kg": w_comp,
        "q_in_kJ_per_kg": q_in,
        "q_out_kJ_per_kg": q_out,
        "COP_R": cop_r,
        "x4_quality": Q4
    }

    # Saturation lines for plotting (between Te and Tc)
    Tline = np.linspace(Te, Tc, 80)
    Pline = []
    hf = []
    hg = []
    sf = []
    sg = []
    for T in Tline:
        try:
            P = PropsSI("P", "T", T, "Q", 0, fluid)
            Pline.append(P / 1000.0)               # kPa
            hf.append(PropsSI("H", "T", T, "Q", 0, fluid) / 1000.0)  # kJ/kg
            hg.append(PropsSI("H", "T", T, "Q", 1, fluid) / 1000.0)
            sf.append(PropsSI("S", "T", T, "Q", 0, fluid) / 1000.0)  # kJ/kg-K
            sg.append(PropsSI("S", "T", T, "Q", 1, fluid) / 1000.0)
        except Exception:
            continue

    sat_df = pd.DataFrame({
        "T_K": Tline[:len(Pline)],
        "P_kPa": Pline,
        "h_f": hf,
        "h_g": hg,
        "s_f": sf,
        "s_g": sg
    })

    return states, metrics, sat_df
