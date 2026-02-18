import numpy as np
import plotly.graph_objects as go

def cycle_line_plot(x, y, xlab, ylab, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers"))
    fig.update_layout(title=title, xaxis_title=xlab, yaxis_title=ylab)
    return fig

def plot_ts(states_df, s_col="s_kJ_per_kgK", t_col="T_K", title="T–s Diagram"):
    s = states_df[s_col].astype(float).tolist()
    t = states_df[t_col].astype(float).tolist()

    # close the loop
    s = s + [s[0]]
    t = t + [t[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s, y=t, mode="lines+markers"))
    fig.update_layout(title=title, xaxis_title="s (kJ/kg·K)", yaxis_title="T (K)")
    return fig

def plot_pv(states_df, v_col="v_m3_per_kg", p_col="P_kPa", title="P–v Diagram"):
    v = states_df[v_col].astype(float).tolist()
    p = states_df[p_col].astype(float).tolist()
    v = v + [v[0]]
    p = p + [p[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v, y=p, mode="lines+markers"))
    fig.update_layout(title=title, xaxis_title="v (m³/kg)", yaxis_title="P (kPa)")
    return fig

def plot_ts_rel(states_df, s_col="s_rel_kJ_per_kgK", t_col="T_K", title="T–s Diagram (relative s)"):
    s = states_df[s_col].astype(float).tolist()
    t = states_df[t_col].astype(float).tolist()
    s = s + [s[0]]
    t = t + [t[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s, y=t, mode="lines+markers"))
    fig.update_layout(title=title, xaxis_title="s (relative, kJ/kg·K)", yaxis_title="T (K)")
    return fig


def plot_rankine_ts(states_df, dome_df, title="Rankine (T–s)"):
    s = states_df["s_kJ_per_kgK"].astype(float).tolist()
    t = states_df["T_K"].astype(float).tolist()
    s = s + [s[0]]
    t = t + [t[0]]

    fig = go.Figure()

    # saturation dome
    fig.add_trace(go.Scatter(x=dome_df["s_f"], y=dome_df["T_K"], mode="lines", name="sat liq"))
    fig.add_trace(go.Scatter(x=dome_df["s_g"], y=dome_df["T_K"], mode="lines", name="sat vap"))

    # cycle
    fig.add_trace(go.Scatter(x=s, y=t, mode="lines+markers", name="cycle"))

    fig.update_layout(title=title, xaxis_title="s (kJ/kg·K)", yaxis_title="T (K)")
    return fig

def plot_rankine_pv(states_df, title="Rankine (P–v)"):
    v = states_df["v_m3_per_kg"].astype(float).tolist()
    p = states_df["P_kPa"].astype(float).tolist()
    v = v + [v[0]]
    p = p + [p[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=v, y=p, mode="lines+markers", name="cycle"))
    fig.update_layout(title=title, xaxis_title="v (m³/kg)", yaxis_title="P (kPa)")
    fig.update_yaxes(type="log")  # Rankine spans big pressure range
    return fig


def plot_vcr_ph(states_df, sat_df, title="VCR (P–h)"):
    h = states_df["h_kJ_per_kg"].astype(float).tolist()
    p = states_df["P_kPa"].astype(float).tolist()
    h = h + [h[0]]
    p = p + [p[0]]

    fig = go.Figure()
    # saturation lines (liq + vap)
    fig.add_trace(go.Scatter(x=sat_df["h_f"], y=sat_df["P_kPa"], mode="lines", name="sat liq"))
    fig.add_trace(go.Scatter(x=sat_df["h_g"], y=sat_df["P_kPa"], mode="lines", name="sat vap"))
    # cycle
    fig.add_trace(go.Scatter(x=h, y=p, mode="lines+markers", name="cycle"))

    fig.update_layout(title=title, xaxis_title="h (kJ/kg)", yaxis_title="P (kPa)")
    fig.update_yaxes(type="log")  # refrigeration spans large pressure ratio
    return fig

def plot_vcr_ts(states_df, sat_df, title="VCR (T–s)"):
    s = states_df["s_kJ_per_kgK"].astype(float).tolist()
    t = states_df["T_K"].astype(float).tolist()
    s = s + [s[0]]
    t = t + [t[0]]

    fig = go.Figure()
    # saturation dome
    fig.add_trace(go.Scatter(x=sat_df["s_f"], y=sat_df["T_K"], mode="lines", name="sat liq"))
    fig.add_trace(go.Scatter(x=sat_df["s_g"], y=sat_df["T_K"], mode="lines", name="sat vap"))
    # cycle
    fig.add_trace(go.Scatter(x=s, y=t, mode="lines+markers", name="cycle"))

    fig.update_layout(title=title, xaxis_title="s (kJ/kg·K)", yaxis_title="T (K)")
    return fig

import plotly.graph_objects as go

def plot_pv_smooth(states_df, path_df, title="P–v Diagram"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=path_df["v_m3_per_kg"], y=path_df["P_kPa"],
        mode="lines", name="process path"
    ))
    fig.add_trace(go.Scatter(
        x=states_df["v_m3_per_kg"], y=states_df["P_kPa"],
        mode="markers+text", text=states_df["State"], textposition="top center",
        name="states"
    ))
    fig.update_layout(title=title, xaxis_title="v (m³/kg)", yaxis_title="P (kPa)")
    return fig

def plot_ts_smooth(states_df, path_df, s_col="s_kJ_per_kgK", title="T–s Diagram"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=path_df[s_col], y=path_df["T_K"],
        mode="lines", name="process path"
    ))
    fig.add_trace(go.Scatter(
        x=states_df[s_col], y=states_df["T_K"],
        mode="markers+text", text=states_df["State"], textposition="top center",
        name="states"
    ))
    fig.update_layout(title=title, xaxis_title="s (kJ/kg·K)", yaxis_title="T (K)")
    return fig

