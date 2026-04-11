import os
import time
import streamlit as st
import streamlit.components.v1 as components

from GUI import constants, visualPageStyle, helpers, visualRender

from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
from utils.logger import step_logger, SolverTimeoutError

visualPageStyle.loadPageLayout()

INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Inputs')

def init_state():
    defaults = {
        "steps": [],
        "solution": None,
        "current_step": -1,
        "auto_playing": False,
        "solved": False,
        "elapsed": 0.0,
        "solve_error": None,
        "solve_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

slider_key = f"step_slider_{st.session_state.solve_count}"

def reset_puzzle_state():
    st.session_state.current_step = -1
    st.session_state.solved = False
    st.session_state.auto_playing = False

def stop_autoplay():
    st.session_state.auto_playing = False

def get_available_inputs():
    return sorted([f.replace('.txt', '') for f in os.listdir(INPUTS_DIR)
                   if f.startswith('input-') and f.endswith('.txt')])

def run_solver_with_steps(algo_key, puzzle, time_out, heuristic_option=None):
    step_logger.reset(puzzle, time_out=time_out)
    algo = get_algorithm(algo_key)
    if algo_key == "astar" and heuristic_option is not None:
        solution = algo.solve(puzzle, option=heuristic_option)
    else:
        solution = algo.solve(puzzle)
    steps = list(step_logger.steps)
    return solution, steps, step_logger.execution_time

st.markdown('<div class="hero-title">🧩 FUTOSHIKI SOLVER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">FUTOSHIKI SOLVER · GROUP 02 · GROUP NON-AI</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### CONFIGURE")

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
    
    selected_heuristic = 3
    if selected_algo_name == "A* Search":
        st.markdown('<div class="section-title" style="margin-top:0.5rem">A* HEURISTIC</div>', unsafe_allow_html=True)
        selected_heuristic_name = st.radio(
            "Heuristic", options=list(constants.HEURISTIC_MAP.keys()), label_visibility="collapsed",
        )
        selected_heuristic = constants.HEURISTIC_MAP[selected_heuristic_name]

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
            st.markdown(visualPageStyle.render_badge("SOLVED", "badge-green"), unsafe_allow_html=True)
        else:
            st.markdown(visualPageStyle.render_badge("NO SOLUTION", "badge-magenta"), unsafe_allow_html=True)

try:
    puzzle = Futoshiki(selected_input)
    load_ok = True
except Exception as e:
    load_ok = False
    st.error(f" Failed to load puzzle: {e}")

if solve_btn and load_ok:
    st.session_state.auto_playing = False
    st.session_state.current_step = -1
    st.session_state.solve_count += 1   # force slider key change
    with st.spinner(f"⏳ Running **{selected_algo_name}** and capturing steps..."):
        try:
            solution, steps, elapsed = run_solver_with_steps(
                constants.ALGO_MAP[selected_algo_name], 
                puzzle, 
                time_out=constants.TIME_OUT,
                heuristic_option=selected_heuristic if selected_algo_name == "A* Search" else None
            )
            st.session_state.steps    = steps
            st.session_state.solution = solution
            st.session_state.elapsed  = elapsed
            st.session_state.solved   = True
            st.session_state.solve_error = None
        except SolverTimeoutError as e:
            st.session_state.solved = False
            st.error(f"{str(e)}")
        except Exception as e:
            st.session_state.solve_error = str(e)
            st.session_state.solved = False

if st.session_state.get('solve_error'):
    st.error(f" Error: {st.session_state.solve_error}")

_trigger_rerun = False
if st.session_state.auto_playing and st.session_state.solved:
    _play_steps = st.session_state.steps
    if st.session_state.current_step < len(_play_steps) - 1:
        time.sleep(step_delay)
        st.session_state.current_step += 1
        _trigger_rerun = True
    else:
        st.session_state.auto_playing = False

st.session_state[slider_key] = st.session_state.current_step

if load_ok:
    visualRender.apply_grid_size(puzzle.size)
    col_grid, col_right = st.columns([1.5, 1], gap="large")

    steps = st.session_state.steps
    cur_idx = st.session_state.current_step
    cur_step = steps[cur_idx] if (steps and 0 <= cur_idx < len(steps)) else None
    active_cell = cur_step['cell'] if cur_step else None

    with col_grid:
        visualPageStyle.glass_card_open()
        n_given  = helpers.count_given(puzzle)
        n_constr = helpers.count_constraints(puzzle)
        title = f" {selected_input.upper()}"
        if st.session_state.solved and cur_step:
            title = f" STEP {cur_step['step_num']} / {len(steps)}"
        elif st.session_state.solved and cur_idx == -1:
            title = f" {selected_input.upper()} — INITIAL"
        st.markdown(f"#### {title}")
        st.markdown(
            visualPageStyle.render_badge(f"{puzzle.size}×{puzzle.size}", "badge-cyan") +
            visualPageStyle.render_badge(f"Given: {n_given}", "badge-cyan") +
            visualPageStyle.render_badge(f"{n_constr} constraints", "badge-cyan"),
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(visualRender.render_grid_html(puzzle, step=cur_step, active_cell=active_cell), unsafe_allow_html=True)
        visualPageStyle.glass_card_close()

    with col_right:
        if st.session_state.solved and steps:
            visualPageStyle.glass_card_open()
            st.markdown("#### ANIMATION CONTROLS")

            def _on_slider_change():
                st.session_state.current_step = st.session_state[slider_key]
                stop_autoplay()

            st.slider(
                "Step", min_value=-1, max_value=len(steps)-1,
                value=st.session_state.current_step,
                format="Step %d",
                label_visibility="collapsed",
                key=slider_key,
                on_change=_on_slider_change,
            )

            if cur_step:
                tc = constants.TAG_BADGE_MAP.get(cur_step['tag'], 'badge-blue')
                st.markdown(
                    visualPageStyle.render_badge(cur_step["tag"].upper(), tc) +
                    visualPageStyle.render_badge(f"CELL ({cur_step['cell'][0]},{cur_step['cell'][1]})", "badge-cyan") +
                    visualPageStyle.render_badge(f"VALUE {cur_step['value']}", "badge-cyan") +
                    visualPageStyle.render_badge(f"{cur_step['facts_count']} FACTS", "badge-purple"),
                    unsafe_allow_html=True
                )
            elif cur_idx == -1:
                st.markdown(visualPageStyle.render_badge("INITIAL STATE", "badge-cyan"), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            btn_cols = st.columns(5)
            def _set_step(val):
                st.session_state.current_step = val
                stop_autoplay()

            with btn_cols[0]:
                if st.button("⏮", use_container_width=True, key="btn_first"):
                    _set_step(-1)
                    st.rerun()
            with btn_cols[1]:
                if st.button("◀", use_container_width=True, key="btn_prev"):
                    _set_step(max(-1, cur_idx - 1))
                    st.rerun()
            with btn_cols[2]:
                play_label = "⏸" if st.session_state.auto_playing else "▶"
                if st.button(play_label, use_container_width=True, key="btn_play"):
                    st.session_state.auto_playing = not st.session_state.auto_playing
                    st.rerun()
            with btn_cols[3]:
                if st.button("▶", use_container_width=True, key="btn_next"):
                    _set_step(min(len(steps)-1, cur_idx + 1))
                    st.rerun()
            with btn_cols[4]:
                if st.button("⏭", use_container_width=True, key="btn_last"):
                    _set_step(len(steps) - 1)
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            tab_log, tab_kb = st.tabs([" STEP LOG", " KB DOMAINS"])

            with tab_log:
                visualPageStyle.glass_card_open()
                total = len(steps)
                n_given_steps    = len(step_logger._given_cells)
                n_deduced_steps  = sum(1 for s in steps if s['tag'] == 'deduced')
                n_backtrack_steps= sum(1 for s in steps if s['tag'] == 'backtrack')
                st.markdown(
                    visualPageStyle.render_badge(f"{total} steps", "badge-cyan") +
                    visualPageStyle.render_badge(f"{n_given_steps} given", "badge-magenta") +
                    visualPageStyle.render_badge(f"{n_deduced_steps} deduced", "badge-green") +
                    (visualPageStyle.render_badge(f"{n_backtrack_steps} backtrack", "badge-yellow") if n_backtrack_steps else ''),
                    unsafe_allow_html=True
                )
                components.html(
                    visualRender.render_step_log_html(steps, cur_idx),
                    height=330,
                    scrolling=False,
                )
                visualPageStyle.glass_card_close()

            with tab_kb:
                visualPageStyle.glass_card_open()
                st.markdown(visualPageStyle.renderKBTabLegend(), unsafe_allow_html=True)
                if cur_step:
                    snap = cur_step['domains_snapshot']
                    n_determined = sum(1 for d in snap.values() if len(d) == 1)
                    n_total_cells = puzzle.size * puzzle.size
                    st.markdown(
                        visualPageStyle.render_badge(f"{n_determined}/{n_total_cells} cells determined", "badge-green") +
                        visualPageStyle.render_badge(f"{cur_step['facts_count']} facts in KB", "badge-purple"),
                        unsafe_allow_html=True
                    )
                st.markdown(
                    visualRender.render_kb_domains_html(puzzle, cur_step, highlight_cell=active_cell),
                    unsafe_allow_html=True
                )
                visualPageStyle.glass_card_close()

        else:
            visualPageStyle.glass_card_open()
            st.markdown("####  INSTRUCTIONS FOR USE")
            st.markdown(f"""
**Press ▶ Solve & Capture Steps** in the sidebar to start.

**After solving:**
- Use the slider or arrow keys **◀ / ▶** to step through
- Press **▶ Play** for auto-play animation
- Tab ** Step Log** – to view step-by-step solutions
- Tab ** KB Domains** – to view KB domain status at each step

{visualPageStyle.renderGridLegend()}

{visualPageStyle.renderKBLegend()}
""", unsafe_allow_html=True)
            visualPageStyle.glass_card_close()

if _trigger_rerun:
    st.rerun()
