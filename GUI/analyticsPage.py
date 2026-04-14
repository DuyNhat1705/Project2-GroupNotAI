import streamlit as st
import pandas as pd
import json
import plotly.express as px
from GUI import constants
def load_analytics_data():
    try:
        with open('Outputs/raw_result.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        return None
def render_analytics_nav():
    st.markdown("### ANALYTICS")
    df = load_analytics_data()
    if df is None: return
    df['Space (Steps)'] = pd.to_numeric(df['Space (Steps)'], errors='coerce')
    df['Space (Steps)'] = df['Space (Steps)'].fillna(0).astype(float)
    unique_solvers = df["Solver"].unique()
    solvers = []

    for solver in unique_solvers:
        default_val = (solver != "Brute Force")
        
        if st.sidebar.checkbox(solver, value=default_val, key=f"cb_{solver}"):
            solvers.append(solver)
    
    filtered_df = df[df["Solver"].isin(solvers)]
    return filtered_df


def render_analytics_page(filtered_df):

    st.subheader("Execution Time by Puzzle Size")
    fig_time = px.bar(
        filtered_df, 
        x="Puzzle size", 
        y="Time (ms)", 
        color="Solver",
        barmode="group",
        color_discrete_map=constants.COLOR_MAP,
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
        color_discrete_map=constants.COLOR_MAP,
        labels={"Space (Steps)": "Total Steps", "Puzzle size": "Grid Size"}
    )
    fig_steps.update_yaxes(
        type="log",
        range=[1, 5],  # log10(10)=1 và log10(100000)=5
        tickvals=[10, 100, 1000, 10000, 100000],
        ticktext=["10", "100", "1k", "10k", "100k"],
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(255, 255, 255, 0.1)',
        minor_showgrid=False,
        zeroline=False
    )
    fig_steps.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono, monospace", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_steps, use_container_width=True)

    with st.expander("See Raw Data Table"):
        st.dataframe(filtered_df, use_container_width=True)