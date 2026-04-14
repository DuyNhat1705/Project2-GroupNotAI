import os
import time
import streamlit as st
import streamlit.components.v1 as components

from GUI import constants, helpers, visualRender, webStyle

from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
from utils.logger import step_logger, SolverTimeoutError

def run_solver_with_steps(algo_key, puzzle, time_out, heuristic_option=None):
    step_logger.reset(puzzle, time_out=time_out)
    algo = get_algorithm(algo_key)
    if algo_key == "astar" and heuristic_option is not None:
        solution  = algo.solve(puzzle, option=heuristic_option)
    else:
        solution = algo.solve(puzzle)
    steps = list(step_logger.steps)
    return solution, steps, step_logger.execution_time
def reset_puzzle_state():
    st.session_state.current_step = 0
    st.session_state.solved = False
    st.session_state.auto_playing = False

def get_available_inputs():
    return sorted([f.replace('.txt', '') for f in os.listdir(constants.INPUTS_DIR)
                   if f.startswith('input-') and f.endswith('.txt')])
def render_visual_nav():
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
    selected_heuristic = 2
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
            st.markdown(webStyle.render_badge("SOLVED", "badge-green"), unsafe_allow_html=True)
        else:
            st.markdown(webStyle.render_badge("NO SOLUTION", "badge-magenta"), unsafe_allow_html=True)

    return selected_input, selected_algo_name, solve_btn, step_delay, selected_heuristic
def render_visual_page(selected_input,selected_algo_name,solve_btn,step_delay, slider_key, selected_heuristic):
    try:
        puzzle = Futoshiki(selected_input)
        load_ok = True
    except Exception as e:
        load_ok = False
        st.error(f" Failed to load puzzle: {e}")

    # ─── Run Solver ────────────────────────────────────────────────────────────────
    if solve_btn and load_ok:
        st.session_state.auto_playing = False
        st.session_state.current_step = 0
        st.session_state.solve_count += 1   # force slider key change
        with st.spinner(f"⏳ Running **{selected_algo_name}** and capturing steps..."):
            try:
                solution, steps, elapsed = run_solver_with_steps(constants.ALGO_MAP[selected_algo_name], puzzle, time_out=constants.TIME_OUT, heuristic_option=selected_heuristic)
                st.session_state.steps    = steps
                st.session_state.solution = solution
                st.session_state.elapsed  = elapsed
                st.session_state.solved   = True
                st.session_state.solve_error = None
            except SolverTimeoutError as e:
                st.session_state.solved = False
                st.error(f"🛑 {str(e)}")
            except Exception as e:
                st.session_state.solve_error = str(e)
                st.session_state.solved = False

    if st.session_state.get('solve_error'):
        st.error(f" Error: {st.session_state.solve_error}")

    _trigger_rerun = False
    if st.session_state.auto_playing and st.session_state.solved:
        _play_steps = st.session_state.steps
        if st.session_state.current_step < len(_play_steps):
            time.sleep(step_delay)
            st.session_state.current_step += 1
            _trigger_rerun = True
        else:
            st.session_state.auto_playing = False

    st.session_state[slider_key] = st.session_state.current_step

    # ─── Main Layout ───────────────────────────────────────────────────────────────
    if load_ok:
        visualRender.apply_grid_size(puzzle.size)
        col_grid, col_right = st.columns([2.5, 1], gap="large")

        # ── Current display state ────────────────────────────────────────────────
        steps = st.session_state.steps
        cur_idx = st.session_state.current_step        # 0 = initial
        cur_step = steps[cur_idx-1] if (steps and 0 < cur_idx <= len(steps)) else None
        active_cell = cur_step['cell'] if cur_step else None

        # ── LEFT: Grid ───────────────────────────────────────────────────────────
        with col_grid:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            n_given  = helpers.count_given(puzzle)
            n_constr = helpers.count_constraints(puzzle)
            title = f" {selected_input.upper()}"
            if st.session_state.solved and cur_step:
                title = f" STEP {cur_step['step_num']} / {len(steps)}"
            elif st.session_state.solved and cur_idx == 0:
                title = f" {selected_input.upper()} — INITIAL"
            st.markdown(f"#### {title}")
            st.markdown(
                f'<span class="stat-badge badge-cyan">{puzzle.size}×{puzzle.size}</span>'
                f'<span class="stat-badge badge-cyan">Given: {n_given}</span>'
                f'<span class="stat-badge badge-cyan">{n_constr} constraints</span>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(visualRender.render_grid_html(puzzle, step=cur_step, active_cell=active_cell), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── RIGHT: Controls + Tabs ────────────────────────────────────────────────
        with col_right:
            # ── Animation controls (only when solved) ──
            if st.session_state.solved and steps:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### ANIMATION CONTROLS")

                # on_change chỉ gọi khi USER kéo — không gọi khi auto-play set session_state[key]
                def _on_slider_change():
                    st.session_state.current_step = st.session_state[slider_key]
                    st.session_state.auto_playing = False

                st.slider(
                    "Step", min_value=0, max_value=len(steps),
                    value=st.session_state.current_step,
                    format="Step %d",
                    label_visibility="collapsed",
                    key=slider_key,
                    on_change=_on_slider_change,
                )

                # Step info
                if cur_step:
                    tc = constants.TAG_BADGE_MAP.get(cur_step['tag'], 'badge-blue')
                    st.markdown(
                        f'<span class="stat-badge {tc}">{cur_step["tag"].upper()}</span>'
                        f'<span class="stat-badge badge-cyan">CELL ({cur_step["cell"][0]},{cur_step["cell"][1]})</span>'
                        f'<span class="stat-badge badge-cyan">VALUE {cur_step["value"]}</span>'
                        f'<span class="stat-badge badge-purple">{cur_step["facts_count"]} FACTS</span>',
                        unsafe_allow_html=True
                    )
                elif cur_idx == 0:
                    st.markdown('<span class="stat-badge badge-cyan">INITIAL STATE</span>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                
                row1_cols = st.columns(3)
                row2_cols = st.columns(2)
                def _set_step(val):
                    """Update current_step — slider will sync at next render."""
                    st.session_state.current_step = val
                    st.session_state.auto_playing = False

                with row1_cols[0]:
                    if st.button("⏮ FIRST",use_container_width=True):
                        _set_step(0)
                        st.rerun()
                with row1_cols[1]:
                    if st.button("◀ PREV",use_container_width=True):
                        _set_step(max(0, cur_idx - 1))
                        st.rerun()
                with row1_cols[2]:
                    if st.button("NEXT ▶",use_container_width=True):
                        _set_step(min(len(steps), cur_idx + 1))
                        st.rerun()
                with row2_cols[0]:
                    play_label = "⏸ PAUSE" if st.session_state.auto_playing else "▶ PLAY"
                    if st.button(play_label,use_container_width=True):
                        st.session_state.auto_playing = not st.session_state.auto_playing
                        st.rerun()
                with row2_cols[1]:
                    if st.button("LAST ⏭",use_container_width=True):
                        _set_step(len(steps))
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

                # ── Tabs: Step Log | KB Domains ──────────────────────────────
                tab_log, tab_kb = st.tabs([" STEP LOG", " KB DOMAINS"])

                with tab_log:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    total = len(steps)
                    n_given_steps    = len(step_logger._given_cells)
                    n_deduced_steps  = sum(1 for s in steps if s['tag'] == 'deduced')
                    n_backtrack_steps= sum(1 for s in steps if s['tag'] == 'backtrack')
                    n_try_steps      = sum(1 for s in steps if s['tag'] == 'try')
                    st.markdown(
                        f'<span class="stat-badge badge-orange">{total} steps</span>'
                        f'<span class="stat-badge badge-magenta">{n_given_steps} given</span>'
                        + (f'<span class="stat-badge badge-cyan">{n_try_steps} try</span>' if n_try_steps else '')
                        + (f'<span class="stat-badge badge-green">{n_deduced_steps} deduced</span>' if n_deduced_steps else '')
                        + (f'<span class="stat-badge badge-yellow">{n_backtrack_steps} backtrack</span>' if n_backtrack_steps else ''),
                        unsafe_allow_html=True
                    )
                    # Dùng components.v1.html để JS có thể chạy — scrollIntoView về bước hiện tại
                    components.html(
                        visualRender.render_step_log_html(steps, cur_idx),
                        height=330,
                        scrolling=False,
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                with tab_kb:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown(webStyle.renderKBTabLegend(), unsafe_allow_html=True)
                    if cur_step:
                        # Domain stats
                        snap = cur_step['domains_snapshot']
                        n_determined = sum(1 for d in snap.values() if len(d) == 1)
                        n_total_cells = puzzle.size * puzzle.size
                        st.markdown(
                            f'<span class="stat-badge badge-green">{n_determined}/{n_total_cells} cells determined</span>'
                            f'<span class="stat-badge badge-purple">{cur_step["facts_count"]} facts in KB</span>',
                            unsafe_allow_html=True
                        )
                    st.markdown(
                        visualRender.render_kb_domains_html(puzzle, cur_step, highlight_cell=active_cell),
                        unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

            else:
                # ── Before solving: hint panel ──
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("####  INSTRUCTIONS FOR USE")
                st.markdown("""
    **Press ▶ Solve & Capture Steps** in the sidebar to start.

    **After solving:**
    - Use the slider or arrow keys **◀ / ▶** to step through
    - Press **▶ Play** for auto-play animation
    - Tab **Step Log** – to view step-by-step solutions
    - Tab **KB Domains** – to view KB domain status at each step

    **Grid Legend:**
    <div style="display:flex;flex-direction:column;gap:0.5rem;margin-bottom:1rem;">
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#c77dff;border:2px solid #9d4edd;"></span>Given (provided in the puzzle)</div>
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#00ff88;border:2px solid #00cc66;"></span>Solved (found solutions)</div>
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#ff006e;border:2px solid #ff006e;"></span>Active (currently being processed)</div>
    </div>

    **KB Legend:**
    <div style="display:flex;flex-direction:column;gap:0.5rem;">
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#c77dff;border:2px solid #9d4edd;"></span>Given – fixed domain</div>
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#00ff88;border:2px solid #00cc66;"></span>Solved – confirmed solution</div>
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#ff006e;border:2px solid #ff006e;"></span>Active – processed in this step</div>
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#ffaa00;border:2px solid #ff9900;"></span>Narrowed – domain narrowed down</div>
    <div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:rgba(100,80,150,0.2);border:2px solid #9d9dff;"></span>Full domain (1...N)</div>
    </div>
    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # ─── Trigger rerun cho frame tiếp theo của auto-play ───────────────────────────────
    if _trigger_rerun:
        time.sleep(0.5)
        st.rerun()