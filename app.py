import os
import streamlit as st
from GUI import webStyle, constants, visualPage



# ─── Session State Init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "Solver",
        "steps": [],
        "solution": None,
        "current_step": 0,
        "auto_playing": False,
        "solved": False,
        "elapsed": 0.0, # thời gian giải
        "memory": 0.0,
        "solve_error": None,
        "last_input": None,
        "last_algo": None,
        "solve_count": 0,   # tăng mỗi lần Solve để force slider re-create
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_puzzle_state():
    st.session_state.current_step = 0
    st.session_state.solved = False
    st.session_state.auto_playing = False

def get_available_inputs():
    return sorted([f.replace('.txt', '') for f in os.listdir(constants.INPUTS_DIR)
                   if f.startswith('input-') and f.endswith('.txt')])



def main():
    # ─── UI ──────────────────────────────────────────────────────────────────────
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
            st.markdown("### ⚙️ CONFIGURE")

            available = get_available_inputs()
            selected_input = st.selectbox(
                "Puzzle", options=available,
                format_func=lambda x: x.upper().replace('-', ' '),
                on_change=reset_puzzle_state,
                label_visibility="collapsed",
            )
            st.markdown('<div class="section-title" style="margin-top:0.8rem">ALGORITHM</div>', unsafe_allow_html=True)
            selected_algo_name = st.radio(
                "Algorithm", options=list(constants.ALGO_MAP.keys()),on_change = reset_puzzle_state, label_visibility="collapsed",
            )

            st.markdown("---")
            solve_btn = st.button("▶ SOLVE & CAPTURE STEPS", use_container_width=True)

            st.markdown('<div class="section-title" style="margin-top:0.5rem">ANIMATION SPEED</div>', unsafe_allow_html=True)
            speed_label = st.select_slider(
                "Speed", options=list(constants.STEP_DELAY_OPTIONS.keys()),
                value="Normal (0.5s)", label_visibility="collapsed",
            )
            step_delay = constants.STEP_DELAY_OPTIONS[speed_label]

            if st.session_state.solved:
                st.markdown("---")
                st.markdown(f"**{len(st.session_state.steps)}** steps · **{st.session_state.elapsed:.1f} ms**")
                if st.session_state.solution:
                    st.markdown('<span class="stat-badge badge-green"> SOLVED</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="stat-badge badge-magenta"> NO SOLUTION</span>', unsafe_allow_html=True)
    if st.session_state.page == "Solver":
        visualPage.render_visual_page(selected_input, selected_algo_name, solve_btn, step_delay, slider_key)
    elif st.session_state.page == "Analytics":
        st.info("Analytics page is under construction. Stay tuned!")
    webStyle.loadPageFooter()
main()