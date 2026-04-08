import os         # thao tác file/folder, biến môi trường
import time       # đo thời gian, delay
import streamlit as st                    # build web app bằng Python
import streamlit.components.v1 as components  # nhúng HTML/JS vào streamlit

from GUI import constants, visualPageStyle, helpers, visualRender

from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
from utils.logger import step_logger

visualPageStyle.loadPageLayout()  # Load page layout and CSS style
# ─── Constants ────────────────────────────────────────────────────────────────
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Inputs')

# ─── Session State Init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "steps": [],
        "solution": None,
        "current_step": -1,
        "auto_playing": False,
        "solved": False,
        "elapsed": 0.0, # thời gian giải
        "memory": 0.0,
        "solve_error": None,
        "last_input": None,
        "last_algo": None,
        "solve_count": 0,   # tăng mỗi lần Solve để force slider re-create
    }
    #st.session_state được Streamlit tự tạo sẵn, không cần khởi tạo thủ công. Nó hoạt động như một dict, tồn tại suốt session của user (từ lúc mở tab đến lúc đóng).
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# Nên mỗi lần bấm Solve → solve_count tăng → slider_key thay đổi → slider được tạo lại từ đầu, không bị giữ giá trị bước cũ từ lần giải trước.
slider_key = f"step_slider_{st.session_state.solve_count}"
# f-string của Python để tạo chuỗi động thôi. Ví dụ: nếu solve_count = 0, slider_key = "step_slider_0". Nếu solve_count = 1, slider_key = "step_slider_1", v.v. 
def reset_puzzle_state():
    st.session_state.current_step = -1
    st.session_state.solved = False
    st.session_state.auto_playing = False
# ─── Helper Functions ──────────────────────────────────────────────────────────
def get_available_inputs(): # Lấy danh sách các file input có sẵn trong thư mục INPUTS_DIR và sort
    return sorted([f.replace('.txt', '') for f in os.listdir(INPUTS_DIR)
                   if f.startswith('input-') and f.endswith('.txt')])

#Hàm này chạy solver và ghi lại từng bước giải bằng kỹ thuật monkeypatching.
def run_solver_with_steps(algo_key, puzzle):
    """
    Chạy solver và thu thập từng bước giải qua step_logger singleton.
    Tất cả algorithm (FC, BT, A*, BC) tự log bằng step_logger.log_step().
    Mỗi step: { step_num, action, tag, cell, value, domains_snapshot, facts_count }
    """
    step_logger.reset(puzzle)
    algo = get_algorithm(algo_key)
    solution = algo.solve(puzzle)
    steps = list(step_logger.steps)
    return solution, steps, step_logger.execution_time

# ─── UI ────────────────────────────────────────────────────────────────────── ─
st.markdown('<div class="hero-title">🧩 FUTOSHIKI SOLVER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">AI Puzzle Solver · Step-by-step Animation · KB Trace Log</div>', unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
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
        "Algorithm", options=list(constants.ALGO_MAP.keys()), label_visibility="collapsed",
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

# ─── Load Puzzle ───────────────────────────────────────────────────────────────
try:
    puzzle = Futoshiki(selected_input)
    load_ok = True
except Exception as e:
    load_ok = False
    st.error(f" Failed to load puzzle: {e}")

# ─── Run Solver ────────────────────────────────────────────────────────────────
if solve_btn and load_ok:
    st.session_state.auto_playing = False
    st.session_state.current_step = -1
    st.session_state.solve_count += 1   # force slider key change
    with st.spinner(f"⏳ Running **{selected_algo_name}** and capturing steps..."):
        try:
            solution, steps, elapsed = run_solver_with_steps(constants.ALGO_MAP[selected_algo_name], puzzle)
            st.session_state.steps    = steps
            st.session_state.solution = solution
            st.session_state.elapsed  = elapsed
            st.session_state.solved   = True
            st.session_state.solve_error = None
            st.session_state.last_input  = selected_input
            st.session_state.last_algo   = selected_algo_name
        except Exception as e:
            st.session_state.solve_error = str(e)
            st.session_state.solved = False

if st.session_state.get('solve_error'):
    st.error(f" Error: {st.session_state.solve_error}")

# ─── Auto-play: cập nhật current_step trước khi bất kỳ widget nào render ─────────────────
_trigger_rerun = False
if st.session_state.auto_playing and st.session_state.solved:
    _play_steps = st.session_state.steps
    if st.session_state.current_step < len(_play_steps) - 1:
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
    cur_idx = st.session_state.current_step        # -1 = initial
    cur_step = steps[cur_idx] if (steps and 0 <= cur_idx < len(steps)) else None
    active_cell = cur_step['cell'] if cur_step else None

    # ── LEFT: Grid ───────────────────────────────────────────────────────────
    with col_grid:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        n_given  = helpers.count_given(puzzle)
        n_constr = helpers.count_constraints(puzzle)
        title = f" {selected_input.upper()}"
        if st.session_state.solved and cur_step:
            title = f" STEP {cur_step['step_num']} / {len(steps)}"
        elif st.session_state.solved and cur_idx == -1:
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
                "Step", min_value=-1, max_value=len(steps)-1,
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
            elif cur_idx == -1:
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
                    _set_step(-1)
                    st.rerun()
            with row1_cols[1]:
                if st.button("◀ PREV",use_container_width=True):
                    _set_step(max(-1, cur_idx - 1))
                    st.rerun()
            with row1_cols[2]:
                if st.button("NEXT ▶",use_container_width=True):
                    _set_step(min(len(steps)-1, cur_idx + 1))
                    st.rerun()
            with row2_cols[0]:
                play_label = "⏸ PAUSE" if st.session_state.auto_playing else "▶ PLAY"
                if st.button(play_label,use_container_width=True):
                    st.session_state.auto_playing = not st.session_state.auto_playing
                    st.rerun()
            with row2_cols[1]:
                if st.button("LAST ⏭",use_container_width=True):
                    _set_step(len(steps) - 1)
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

# ─── Footer ────────────────────────────────────────────────────────────────────
visualPageStyle.loadPageFooter()
