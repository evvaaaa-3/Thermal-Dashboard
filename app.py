import streamlit as st

from core.process_paths import smooth_path_ideal
from core.plotting import (
    plot_pv_smooth, plot_ts_smooth,
    plot_pv, plot_ts_rel, plot_ts,
    plot_rankine_ts, plot_rankine_pv,
    plot_vcr_ph, plot_vcr_ts
)

from cycles.carnot import carnot_cycle
from cycles.brayton import brayton_ideal
from cycles.otto import otto_cycle
from cycles.diesel import diesel_cycle
from cycles.dual import dual_cycle
from cycles.rankine_basic import rankine_ideal
from cycles.rankine_reheat import rankine_reheat_ideal
from cycles.refrigeration_vcr import vcr_ideal


st.set_page_config(page_title="Thermo Cycles Visualizer", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
/* -------------------------
   Layout / Page
-------------------------- */
.block-container{
  max-width: 1400px;
  padding-top: 3.0rem;
  padding-bottom: 1.5rem;
}

/* Prevent big text clipping (fix title cut) */
div[data-testid="stMarkdownContainer"] { overflow: visible !important; }
div[data-testid="stVerticalBlock"] { overflow: visible !important; }
section.main > div { overflow: visible !important; }

/* -------------------------
   Sidebar styling
-------------------------- */
section[data-testid="stSidebar"]{
  background: #0b1220;
}
section[data-testid="stSidebar"] *{
  color: #E6E6E6;
}

/* -------------------------
   Title (centered + not cut)
-------------------------- */
.hero{
  width: 100%;
  text-align: center;
  margin: 0 auto 18px auto;
  padding: 6px 0 10px 0;
}
.hero-title{
  font-weight: 900;
  letter-spacing: 0.6px;
  line-height: 1.06;
  margin: 0;
  font-size: clamp(34px, 4.2vw, 56px);
  white-space: nowrap;
}
@media (max-width: 900px){
  .hero-title{ white-space: normal; }
}
.hero-subtitle{
  margin-top: 6px;
  font-size: 16px;
  opacity: 0.75;
}

/* -------------------------
   Cards / Panels
-------------------------- */
.perf-panel{
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 16px 16px 6px 16px;
  box-shadow: 0 8px 26px rgba(0,0,0,0.25);
}

/* Metric card styling */
div[data-testid="stMetric"]{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.14);
  padding: 16px 18px;
  border-radius: 14px;
  margin-bottom: 14px;
}

/* Metric text */
div[data-testid="stMetricLabel"]{
  opacity: 0.85;
  font-size: 14px !important;
}
div[data-testid="stMetricValue"]{
  font-size: 44px !important;
  line-height: 1.05 !important;
}

/* -------------------------
   Table styling
-------------------------- */
div[data-testid="stDataFrame"]{
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  overflow: hidden;
}

/* Headings spacing */
h1, h2, h3{
  letter-spacing: 0.2px;
}
</style>

<div class="hero">
  <div class="hero-title">Thermo Cycles Visualizer</div>
  <div class="hero-subtitle">Basics → Real Cycles</div>
</div>
""", unsafe_allow_html=True)


cycle = st.sidebar.selectbox(
    "Choose cycle",
    ["Carnot", "Brayton", "Otto", "Diesel", "Dual", "Rankine Ideal", "Rankine Reheat", "VCR Refrigeration"]
)

# -----------------------------
# Carnot
# -----------------------------
if cycle == "Carnot":
    st.sidebar.subheader("Inputs")
    mode = st.sidebar.selectbox("Mode", ["engine", "refrigerator", "heat_pump"])
    Th = st.sidebar.number_input("Th (K) – hot reservoir", 350.0, 2500.0, 600.0, 10.0)
    Tc = st.sidebar.number_input("Tc (K) – cold reservoir", 200.0, 2000.0, 300.0, 10.0)
    ds = st.sidebar.number_input("Δs (kJ/kg·K) (sets scale)", 0.1, 10.0, 1.0, 0.1)

    states, metrics = carnot_cycle(Th_K=Th, Tc_K=Tc, delta_s_kJkgK=ds, mode=mode)

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table (T–s)")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        #st.markdown('<div class="perf-panel">', unsafe_allow_html=True)

        st.write(f"**Mode:** {metrics['mode']}")

        if mode == "engine":
            st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
            st.metric("W_net (kJ/kg)", f"{metrics['W_net_kJ_per_kg']:.2f}")
            st.metric("Q_in (kJ/kg)", f"{metrics['Q_in_kJ_per_kg']:.2f}")

        elif mode == "refrigerator":
            st.metric("COP_R", f"{metrics['COP_R']:.3f}")
            st.metric("W_in (kJ/kg)", f"{metrics['W_in_kJ_per_kg']:.2f}")
            st.metric("Q_cold (kJ/kg)", f"{metrics['Q_cold_kJ_per_kg']:.2f}")

        else:  # heat_pump
            st.metric("COP_HP", f"{metrics['COP_HP']:.3f}")
            st.metric("W_in (kJ/kg)", f"{metrics['W_in_kJ_per_kg']:.2f}")
            st.metric("Q_hot (kJ/kg)", f"{metrics['Q_hot_kJ_per_kg']:.2f}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Smooth path (ideal-gas conceptual Carnot)
    legs = [("isoth", 1, 2), ("isen", 2, 3), ("isoth", 3, 4), ("isen", 4, 1)]
    path = smooth_path_ideal(states, legs, gamma=1.4, R=0.287)

    st.subheader("Plots (smooth processes)")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(
            plot_ts_smooth(states, path, s_col="s_kJ_per_kgK", title="Carnot (T–s)"),
            use_container_width=True
        )
    with colB:
        st.plotly_chart(
            plot_pv_smooth(states, path, title="Carnot (P–v, ideal-gas conceptual)"),
            use_container_width=True
        )


# -----------------------------
# Brayton
# -----------------------------
elif cycle == "Brayton":
    st.sidebar.subheader("Inputs")
    P1 = st.sidebar.number_input("P1 (kPa)", 50.0, 500.0, 100.0, 10.0)
    T1 = st.sidebar.number_input("T1 (K)", 250.0, 400.0, 300.0, 5.0)
    rp = st.sidebar.number_input("Pressure ratio rp", 1.5, 40.0, 10.0, 0.5)
    T3 = st.sidebar.number_input("T3 (K)", 900.0, 2200.0, 1400.0, 50.0)
    gamma = st.sidebar.number_input("gamma", 1.2, 1.45, 1.4, 0.01)

    states, metrics = brayton_ideal(P1_kPa=P1, T1_K=T1, rp=rp, T3_K=T3, gamma=gamma)

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)
        st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
        st.metric("W_net (kJ/kg)", f"{metrics['Wnet_kJ_per_kg']:.2f}")
        st.metric("Q_in (kJ/kg)", f"{metrics['Qin_kJ_per_kg']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    # plots unchanged
    legs = [("isen", 1, 2), ("cv", 2, 3), ("isen", 3, 4), ("cv", 4, 1)]
    path = smooth_path_ideal(states, legs, gamma=gamma, R=0.287)

    st.subheader("Plots (smooth processes)")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(plot_pv_smooth(states, path, title="Carnot (P–v)"), use_container_width=True)
    with colB:
        st.plotly_chart(plot_ts_smooth(states, path, s_col="s_rel_kJ_per_kgK", title="Carnot (T–s, relative s)"),
                        use_container_width=True)


# -----------------------------
# Otto
# -----------------------------
elif cycle == "Otto":
    st.sidebar.subheader("Inputs")
    P1 = st.sidebar.number_input("P1 (kPa)", 50.0, 500.0, 100.0, 10.0)
    T1 = st.sidebar.number_input("T1 (K)", 250.0, 600.0, 300.0, 10.0)
    r  = st.sidebar.number_input("Compression ratio r", 2.0, 25.0, 8.0, 0.5)
    T3 = st.sidebar.number_input("T3 (K) (max temp after heat add)", 700.0, 3500.0, 1800.0, 50.0)
    gamma = st.sidebar.number_input("gamma", 1.25, 1.45, 1.4, 0.01)

    states, metrics = otto_cycle(T1_K=T1, P1_kPa=P1, r=r, T3_K=T3, gamma=gamma)

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)
        st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
        st.metric("W_net (kJ/kg)", f"{metrics['Wnet_kJ_per_kg']:.2f}")
        st.metric("Q_in (kJ/kg)", f"{metrics['Qin_kJ_per_kg']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    # plots unchanged
    legs = [("isen", 1, 2), ("cv", 2, 3), ("isen", 3, 4), ("cv", 4, 1)]
    path = smooth_path_ideal(states, legs, gamma=gamma, R=0.287)

    st.subheader("Plots (smooth processes)")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(plot_pv_smooth(states, path, title="Otto (P–v)"), use_container_width=True)
    with colB:
        st.plotly_chart(plot_ts_smooth(states, path, s_col="s_rel_kJ_per_kgK", title="Otto (T–s, relative s)"),
                        use_container_width=True)

# -----------------------------
# Diesel
# -----------------------------
elif cycle == "Diesel":
    st.sidebar.subheader("Inputs")
    P1 = st.sidebar.number_input("P1 (kPa)", 50.0, 500.0, 100.0, 10.0)
    T1 = st.sidebar.number_input("T1 (K)", 250.0, 600.0, 300.0, 10.0)
    r  = st.sidebar.number_input("Compression ratio r", 5.0, 30.0, 18.0, 0.5)
    rc = st.sidebar.number_input("Cutoff ratio rc (v3/v2)", 1.05, 4.0, 2.0, 0.05)
    gamma = st.sidebar.number_input("gamma", 1.25, 1.45, 1.4, 0.01)

    states, metrics = diesel_cycle(T1_K=T1, P1_kPa=P1, r=r, rc=rc, gamma=gamma)

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)
        st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
        st.metric("W_net (kJ/kg)", f"{metrics['Wnet_kJ_per_kg']:.2f}")
        st.metric("Q_in (kJ/kg)", f"{metrics['Qin_kJ_per_kg']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    # plots unchanged
    legs = [("isen", 1, 2), ("cv", 2, 3), ("isen", 3, 4), ("cv", 4, 1)]
    path = smooth_path_ideal(states, legs, gamma=gamma, R=0.287)

    st.subheader("Plots (smooth processes)")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(plot_pv_smooth(states, path, title="Diesel (P–v)"), use_container_width=True)
    with colB:
        st.plotly_chart(plot_ts_smooth(states, path, s_col="s_rel_kJ_per_kgK", title="Diesel (T–s, relative s)"),
                        use_container_width=True)

# -----------------------------
# Dual
# -----------------------------
elif cycle == "Dual":
    st.sidebar.subheader("Inputs")
    P1 = st.sidebar.number_input("P1 (kPa)", 50.0, 500.0, 100.0, 10.0)
    T1 = st.sidebar.number_input("T1 (K)", 250.0, 600.0, 300.0, 10.0)
    r  = st.sidebar.number_input("Compression ratio r", 5.0, 30.0, 14.0, 0.5)
    alpha = st.sidebar.number_input("alpha = P3/P2 (const-V heat add)", 1.05, 5.0, 1.5, 0.05)
    rc = st.sidebar.number_input("rc = v4/v3 (const-P heat add)", 1.05, 4.0, 1.3, 0.05)
    gamma = st.sidebar.number_input("gamma", 1.25, 1.45, 1.4, 0.01)

    states, metrics = dual_cycle(T1_K=T1, P1_kPa=P1, r=r, alpha=alpha, rc=rc, gamma=gamma)

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)
        st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
        st.metric("W_net (kJ/kg)", f"{metrics['Wnet_kJ_per_kg']:.2f}")
        st.metric("Q_in (kJ/kg)", f"{metrics['Qin_kJ_per_kg']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    # plots unchanged
    legs = [("isen", 1, 2), ("cv", 2, 3), ("isen", 3, 4), ("cv", 4, 1)]
    path = smooth_path_ideal(states, legs, gamma=gamma, R=0.287)

    st.subheader("Plots (smooth processes)")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(plot_pv_smooth(states, path, title="Dual (P–v)"), use_container_width=True)
    with colB:
        st.plotly_chart(plot_ts_smooth(states, path, s_col="s_rel_kJ_per_kgK", title="Dual(T–s, relative s)"),
                        use_container_width=True)

# -----------------------------
# Rankine Ideal
# -----------------------------
elif cycle == "Rankine Ideal":
    st.sidebar.subheader("Inputs")
    Pc = st.sidebar.number_input("Condenser pressure Pc (kPa)", 2.0, 100.0, 10.0, 1.0)
    Pb = st.sidebar.number_input("Boiler pressure Pb (kPa)", 500.0, 25000.0, 8000.0, 500.0)

    superheat = st.sidebar.checkbox("Superheat at turbine inlet?", value=True)
    if superheat:
        T3C = st.sidebar.number_input("T3 (°C)", 150.0, 800.0, 450.0, 10.0)
    else:
        T3C = None

    states, metrics, dome = rankine_ideal(Pc_kPa=Pc, Pb_kPa=Pb, T3_C=T3C)

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)

        st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
        st.metric("W_net (kJ/kg)", f"{metrics['Wnet_kJ_per_kg']:.2f}")
        st.metric("Q_in (kJ/kg)", f"{metrics['Qin_kJ_per_kg']:.2f}")
        x4 = metrics["turbine_exit_quality_x"]
        st.write(f"**Turbine exit quality x₄:** {x4 if x4 is not None else 'N/A (superheated)'}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Plots")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(plot_rankine_ts(states, dome, title="Rankine (T–s)"), use_container_width=True)
    with colB:
        st.plotly_chart(plot_rankine_pv(states, title="Rankine (P–v)"), use_container_width=True)


# -----------------------------
# Rankine Reheat
# -----------------------------
elif cycle == "Rankine Reheat":
    st.sidebar.subheader("Inputs")
    Pc = st.sidebar.number_input("Condenser pressure Pc (kPa)", 2.0, 100.0, 10.0, 1.0)
    Pb = st.sidebar.number_input("Boiler pressure Pb (kPa)", 500.0, 25000.0, 8000.0, 500.0)
    Pr = st.sidebar.number_input("Reheat pressure Pr (kPa)", 50.0, 20000.0, 1500.0, 100.0)

    T3C = st.sidebar.number_input("Main steam T3 (°C) at Pb", 200.0, 800.0, 450.0, 10.0)
    T5C = st.sidebar.number_input("Reheat outlet T5 (°C) at Pr", 200.0, 800.0, 450.0, 10.0)

    states, metrics, dome = rankine_reheat_ideal(
        Pc_kPa=Pc, Pb_kPa=Pb, Pr_kPa=Pr, T3_C=T3C, T5_C=T5C
    )

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)

        st.metric("η_th", f"{metrics['eta_th']*100:.2f}%")
        st.metric("W_net (kJ/kg)", f"{metrics['Wnet_kJ_per_kg']:.2f}")
        st.metric("Q_in total (kJ/kg)", f"{metrics['Qin_total_kJ_per_kg']:.2f}")
        st.write(
            f"**Turbine exit quality x₆:** "
            f"{metrics['turbine_exit_quality_x6'] if metrics['turbine_exit_quality_x6'] is not None else 'N/A'}"
        )

        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Plots")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(
            plot_rankine_ts(states, dome, title="Rankine with Reheat (T–s)"),
            use_container_width=True
        )
    with colB:
        st.plotly_chart(
            plot_rankine_pv(states, title="Rankine with Reheat (P–v)"),
            use_container_width=True
        )


# -----------------------------
# VCR Refrigeration
# -----------------------------
elif cycle == "VCR Refrigeration":
    st.sidebar.subheader("Inputs")
    fluid = st.sidebar.selectbox("Refrigerant", ["R134a", "R22", "R410A", "R32", "Ammonia", "Propane"])
    Tevap = st.sidebar.number_input("Evaporator saturation temp Tevap (°C)", -40.0, 30.0, -10.0, 1.0)
    Tcond = st.sidebar.number_input("Condenser saturation temp Tcond (°C)", 10.0, 80.0, 40.0, 1.0)
    superheat = st.sidebar.number_input("Superheat at compressor inlet (°C)", 0.0, 30.0, 5.0, 1.0)
    subcool = st.sidebar.number_input("Subcool at condenser outlet (°C)", 0.0, 30.0, 5.0, 1.0)

    states, metrics, sat = vcr_ideal(
        fluid=fluid,
        Tevap_C=Tevap,
        Tcond_C=Tcond,
        superheat_C=superheat,
        subcool_C=subcool
    )

    st.subheader("Overview")
    tab1, tab2 = st.tabs(["📋 State Table", "📌 Performance"])

    with tab1:
        st.subheader("State Table")
        st.dataframe(states, use_container_width=True)

    with tab2:
        st.subheader("Performance")
        # st.markdown('<div class="perf-panel">', unsafe_allow_html=True)

        st.metric("COP_R", f"{metrics['COP_R']:.3f}")
        st.metric("Compressor work (kJ/kg)", f"{metrics['w_comp_kJ_per_kg']:.2f}")
        st.metric("Cooling effect q_in (kJ/kg)", f"{metrics['q_in_kJ_per_kg']:.2f}")
        st.write(f"**Pe:** {metrics['Pe_kPa']:.1f} kPa")
        st.write(f"**Pc:** {metrics['Pc_kPa']:.1f} kPa")
        st.write(f"**x4 (after valve):** {metrics['x4_quality'] if metrics['x4_quality'] is not None else 'N/A'}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Plots")
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(plot_vcr_ph(states, sat, title="VCR (P–h)"), use_container_width=True)
    with colB:
        st.plotly_chart(plot_vcr_ts(states, sat, title="VCR (T–s)"), use_container_width=True)

