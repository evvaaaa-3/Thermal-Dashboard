import numpy as np
import pandas as pd

# ---------------------------
# Ideal-gas process samplers
# ---------------------------

def _cv_from_gamma_R(gamma, R):
    cv = R / (gamma - 1.0)
    cp = gamma * cv
    return cp, cv

def path_isentropic_ideal(Pa, Va, Ta, Pb, Vb, gamma, R, n=80, s_a=0.0):
    # P V^gamma = const, T V^(gamma-1) = const
    V = np.linspace(Va, Vb, n)
    Cpv = Pa * (Va ** gamma)
    P = Cpv / (V ** gamma)
    T = Ta * (Va / V) ** (gamma - 1.0)
    s = np.full_like(T, float(s_a))  # isentropic => constant s
    return pd.DataFrame({"P_kPa": P, "v_m3_per_kg": V, "T_K": T, "s_kJ_per_kgK": s})

def path_const_v_ideal(Vconst, Ta, Tb, R, n=60, s_a=0.0, gamma=1.4):
    cp, cv = _cv_from_gamma_R(gamma, R)
    T = np.linspace(Ta, Tb, n)
    P = (R * T) / Vconst
    s = s_a + cv * np.log(T / Ta)
    V = np.full_like(T, float(Vconst))
    return pd.DataFrame({"P_kPa": P, "v_m3_per_kg": V, "T_K": T, "s_kJ_per_kgK": s})

def path_const_p_ideal(Pconst, Ta, Tb, R, n=60, s_a=0.0, gamma=1.4):
    cp, cv = _cv_from_gamma_R(gamma, R)
    T = np.linspace(Ta, Tb, n)
    V = (R * T) / Pconst
    s = s_a + cp * np.log(T / Ta)
    P = np.full_like(T, float(Pconst))
    return pd.DataFrame({"P_kPa": P, "v_m3_per_kg": V, "T_K": T, "s_kJ_per_kgK": s})

def path_isothermal_ideal(Tconst, Va, Vb, R, n=80, s_a=0.0):
    V = np.linspace(Va, Vb, n)
    P = (R * Tconst) / V
    s = s_a + R * np.log(V / Va)
    T = np.full_like(V, float(Tconst))
    return pd.DataFrame({"P_kPa": P, "v_m3_per_kg": V, "T_K": T, "s_kJ_per_kgK": s})


def smooth_path_ideal(states_df, legs, gamma=1.4, R=0.287):
    """
    legs: list of tuples describing each process.
      ("isen", i, j)
      ("cv",   i, j)
      ("cp",   i, j)
      ("isoth",i, j)  # uses T from state i
    i,j are 1-based state numbers.
    """
    out = []
    # choose entropy column name that exists
    if "s_kJ_per_kgK" in states_df.columns:
        scol = "s_kJ_per_kgK"
    elif "s_rel_kJ_per_kgK" in states_df.columns:
        scol = "s_rel_kJ_per_kgK"
    else:
        scol = None

    def row(k):
        return states_df.loc[states_df["State"] == k].iloc[0]

    for idx, leg in enumerate(legs):
        kind, i, j = leg
        a = row(i); b = row(j)

        # entropy anchor at start of each leg
        s_a = float(a[scol]) if scol else 0.0

        if kind == "isen":
            seg = path_isentropic_ideal(
                Pa=float(a["P_kPa"]), Va=float(a["v_m3_per_kg"]), Ta=float(a["T_K"]),
                Pb=float(b["P_kPa"]), Vb=float(b["v_m3_per_kg"]),
                gamma=gamma, R=R, n=90, s_a=s_a
            )
        elif kind == "cv":
            seg = path_const_v_ideal(
                Vconst=float(a["v_m3_per_kg"]),
                Ta=float(a["T_K"]), Tb=float(b["T_K"]),
                R=R, n=70, s_a=s_a, gamma=gamma
            )
        elif kind == "cp":
            seg = path_const_p_ideal(
                Pconst=float(a["P_kPa"]),
                Ta=float(a["T_K"]), Tb=float(b["T_K"]),
                R=R, n=70, s_a=s_a, gamma=gamma
            )
        elif kind == "isoth":
            seg = path_isothermal_ideal(
                Tconst=float(a["T_K"]),
                Va=float(a["v_m3_per_kg"]), Vb=float(b["v_m3_per_kg"]),
                R=R, n=90, s_a=s_a
            )
        else:
            raise ValueError(f"Unknown leg kind: {kind}")

        # avoid duplicating the first point of every next segment
        if idx > 0:
            seg = seg.iloc[1:].copy()
        out.append(seg)

    df = pd.concat(out, ignore_index=True)

# Make the path entropy column name match the states entropy column name
# (states may use s_rel_kJ_per_kgK, while path is computed as s_kJ_per_kgK)
    if scol and (scol != "s_kJ_per_kgK") and ("s_kJ_per_kgK" in df.columns):
        df = df.rename(columns={"s_kJ_per_kgK": scol})

    return df

