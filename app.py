
import streamlit as st
import pandas as pd
import json
import plotly.express as px
from GUI import webStyle, visualPage
def init_state():
    defaults = {
        "page": "Solver",
        "steps": [],
        "solution": None,
        "current_step": 0,
        "auto_playing": False,
        "solved": False,
        "elapsed": 0.0,
        "solve_error": None,
        "solve_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
def load_analytics_data():
    try:
        with open('raw_result.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        return None
def render_analytics_page():
    
    df = load_analytics_data()
    if df is None: return

    COLOR_MAP = {
        "Backward Chaining": "#7b2ff7", 
        "Forward Chaining": "#00d4ff",  
        "SAT": "#ff006e",               
        "A* Search": "#3a86ff",         
        "Backtracking": "#06d6a0",      
        "Brute Force": "#8d99ae"
    }

    st.sidebar.markdown("#### FILTER")
    solvers = st.sidebar.multiselect(
        "Select Solvers", 
        options=df["Solver"].unique(), 
        default=[s for s in df["Solver"].unique() if s != "Brute Force"]
    )
    
    filtered_df = df[df["Solver"].isin(solvers)]

    st.subheader("Execution Time by Puzzle Size")
    fig_time = px.bar(
        filtered_df, 
        x="Puzzle size", 
        y="Time (ms)", 
        color="Solver",
        barmode="group",
        color_discrete_map=COLOR_MAP,
        title="Lower is better (ms)",
        labels={"Time (ms)": "Time (ms)", "Puzzle size": "Grid Size"}
    )
    
    fig_time.update_yaxes(
        type="log", 
        range=[-1, 5], 
        tickvals=[0.1, 1, 10, 100, 1000, 10000, 100000], 
        ticktext=["0.1", "1", "10", "100", "1k", "10k", "100k"], 
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(255, 255, 255, 0.1)',
        minor_showgrid=False,
        zeroline=False
    )

    fig_time.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono, monospace", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    st.subheader("Solving Steps (Space Complexity)")
    fig_steps = px.bar(
        filtered_df, 
        x="Puzzle size", 
        y="Space (Steps)", 
        color="Solver",
        barmode="group",
        color_discrete_map=COLOR_MAP,
        title="Fewer steps = More efficient search",
        labels={"Space (Steps)": "Total Steps", "Puzzle size": "Grid Size"}
    )
    
    fig_steps.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono, monospace")
    )
    st.plotly_chart(fig_steps, use_container_width=True)

    with st.expander("See Raw Data Table"):
        st.dataframe(filtered_df, use_container_width=True)
def main():
    webStyle.loadPageStyle()
    init_state()
    slider_key = f"step_slider_{st.session_state.solve_count}"
    webStyle.loadPageHeader()
    with st.sidebar:
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("SOLVER", use_container_width = True):
                st.session_state.page = "Solver"
                st.rerun()
        with col_nav2:
            if st.button("ANALYTICS", use_container_width = True):
                st.session_state.page = "Analytics"
                st.rerun()
        st.markdown("---")
        if st.session_state.page == "Solver":
            selected_input, selected_algo_name, solve_btn, step_delay, selected_heuristic = visualPage.render_visual_nav()
        elif st.session_state.page == "Analytics":
            st.markdown("### ANALYTICS")
            st
                    
    if st.session_state.page == "Solver":
        visualPage.render_visual_page(selected_input, selected_algo_name, solve_btn, step_delay, slider_key, selected_heuristic)
    elif st.session_state.page == "Analytics":
        render_analytics_page()
    webStyle.loadPageFooter()

main()