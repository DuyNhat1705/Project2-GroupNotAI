import os         # thao tác file/folder, biến môi trường
import time       # đo thời gian, delay
import streamlit as st                    # build web app bằng Python
import streamlit.components.v1 as components  # nhúng HTML/JS vào streamlit

from GUI import constants, helpers, visualRender

from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
from utils.logger import step_logger, SolverTimeoutError

def run_solver_with_steps(algo_key, puzzle, time_out):
    """
    Chạy solver và thu thập từng bước giải qua step_logger singleton.
    Tất cả algorithm (FC, BT, A*, BC) tự log bằng step_logger.log_step().
    Mỗi step: { step_num, action, tag, cell, value, domains_snapshot, facts_count }
    """
    step_logger.reset(puzzle, time_out=time_out)
    algo = get_algorithm(algo_key)
    solution = algo.solve(puzzle)
    steps = list(step_logger.steps)
    return solution, steps, step_logger.execution_time
def render_visual_page(selected_input,selected_algo_name,solve_btn,step_delay, slider_key):
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
                solution, steps, elapsed = run_solver_with_steps(constants.ALGO_MAP[selected_algo_name], puzzle, time_out=constants.TIME_OUT)
                st.session_state.steps    = steps
                st.session_state.solution = solution
                st.session_state.elapsed  = elapsed
                st.session_state.solved   = True
                st.session_state.solve_error = None
                st.session_state.last_input  = selected_input
                st.session_state.last_algo   = selected_algo_name
            except SolverTimeoutError as e:
                st.session_state.solved = False
                st.error(f"🛑 {str(e)}")
            except Exception as e:
                st.session_state.solve_error = str(e)
                st.session_state.solved = False

    if st.session_state.get('solve_error'):
        st.error(f" Error: {st.session_state.solve_error}")

    # ─── Auto-play: cập nhật current_step trước khi bất kỳ widget nào render ─────────────────
    _trigger_rerun = False
    if st.session_state.auto_playing and st.session_state.solved:
        _play_steps = st.session_state.steps
        if st.session_state.current_step < len(_play_steps):
            time.sleep(step_delay)
            st.session_state.current_step += 1
            _trigger_rerun = True
        else:
            st.session_state.auto_playing = False

    # Sync slider một lần duy nhất, TRƯỚC khi slider widget được tạo ra.
    # Mọi thay đổi current_step (auto-play, nút bấm) đều được xử lý ở đây.
    # Streamlit cho phép ghi session_state[key] trước khi widget có key đó render.
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
                st.markdown("#### 🎬 ANIMATION CONTROLS")

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
                    tag_colors = {'given': 'badge-magenta', 'deduced': 'badge-green', 'backtrack': 'badge-yellow'}
                    tc = tag_colors.get(cur_step['tag'], 'badge-blue')
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

                # Control buttons
                b1, b2, b3, b4, b5 = st.columns(5)
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
                    st.markdown(
                        f'<span class="stat-badge badge-cyan">{total} steps</span>'
                        f'<span class="stat-badge badge-magenta">{n_given_steps} given</span>'
                        f'<span class="stat-badge badge-green">{n_deduced_steps} deduced</span>'
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
                    st.markdown(
                        '<div style="font-size:0.72rem;color:#c77dff;margin-bottom:0.5rem;font-family:JetBrains Mono,monospace;text-shadow:0 0 5px #9d4edd;">'
                        '🟪 GIVEN &nbsp; 🟩 SOLVED &nbsp; 🟨 ACTIVE &nbsp; 🟧 NARROWED &nbsp; ··· FULL</div>',
                        unsafe_allow_html=True
                    )
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
    - Tab ** Step Log** – to view step-by-step solutions
    - Tab ** KB Domains** – to view KB domain status at each step

    **Grid Legend:**
    | | |
    |---|---|
    | 🟪 | Given (provided in the puzzle) |
    | 🟩 | Solved (found solutions) |
    | 🟨 | Active (currently being processed) |

    **KB Legend:**
    | | |
    |---|---|
    | 🟪 | Given – fixed domain |
    | 🟩 | Solved – confirmed solution |
    | 🟨 | Active – processed in this step |
    | 🟧 | Narrowed – domain narrowed down |
    | ··· | Full domain (1...N) |
    """)
                st.markdown('</div>', unsafe_allow_html=True)

    # ─── Trigger rerun cho frame tiếp theo của auto-play ───────────────────────────────
    if _trigger_rerun:
        st.rerun()