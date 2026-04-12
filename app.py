
import streamlit as st
from GUI import webStyle, visualPage, analyticsPage
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
            filtered_df = analyticsPage.render_analytics_nav()
                    
    if st.session_state.page == "Solver":
        visualPage.render_visual_page(selected_input, selected_algo_name, solve_btn, step_delay, slider_key, selected_heuristic)
    elif st.session_state.page == "Analytics":
        analyticsPage.render_analytics_page(filtered_df)
    webStyle.loadPageFooter()

main()