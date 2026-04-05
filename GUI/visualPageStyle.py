import streamlit as st
def loadPageLayout():
    # ─── Page Config ──────────────────────────────────────────────────────────────
    st.set_page_config(page_title="Futoshiki Solver", page_icon="🧩", layout="wide")
    #Cấu hình trang Streamlit — title, icon, layout, sidebar mặc định, v.v.
    # ─── CSS ──────────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }
    .hero-title {
        font-size: 2.6rem; font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; text-align: center; margin-bottom: 0.2rem;
    }
    .hero-sub {
        text-align: center; color: #94a3b8; font-size: 0.95rem;
        margin-bottom: 1.5rem; font-weight: 300;
    }
    .glass-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 1.2rem;
        backdrop-filter: blur(12px); margin-bottom: 1rem;
    }

    /* ── Futoshiki grid ── */
    .futoshiki-table { border-collapse: collapse; margin: 0 auto; font-family: 'JetBrains Mono', monospace; }
    .cell {
        width: 52px; height: 52px; text-align: center; vertical-align: middle;
        font-size: 1.35rem; font-weight: 600;
        border: 2px solid rgba(167,139,250,0.25); border-radius: 10px;
        background: rgba(255,255,255,0.04); color: #94a3b8;
        transition: all 0.25s ease;
    }
    .cell.given    { background: rgba(99,102,241,0.28); color: #a78bfa; border-color: rgba(167,139,250,0.6); }
    .cell.solved   { background: rgba(52,211,153,0.15);  color: #34d399;  border-color: rgba(52,211,153,0.5); animation: popIn 0.35s ease; }
    .cell.active   { background: rgba(251,191,36,0.25);  color: #fbbf24;  border-color: #fbbf24; box-shadow: 0 0 12px rgba(251,191,36,0.5); animation: pulse 1s infinite; }
    @keyframes popIn  { 0%{transform:scale(0.75);opacity:0} 100%{transform:scale(1);opacity:1} }
    @keyframes pulse  { 0%,100%{box-shadow:0 0 8px rgba(251,191,36,0.4)} 50%{box-shadow:0 0 18px rgba(251,191,36,0.8)} }
    .constraint-h { width:26px; height:52px; text-align:center; vertical-align:middle; font-size:1rem; font-weight:700; color:#f59e0b; }
    .constraint-v { width:52px; height:22px; text-align:center; vertical-align:middle; font-size:1rem; font-weight:700; color:#f59e0b; }
    .constraint-gap { width:26px; height:22px; }

    /* ── Stat badges ── */
    .stat-badge { display:inline-block; padding:0.25rem 0.7rem; border-radius:999px; font-size:0.8rem; font-weight:600; margin:0.2rem; }
    .badge-purple { background:rgba(139,92,246,0.25); color:#a78bfa; border:1px solid rgba(139,92,246,0.4); }
    .badge-green  { background:rgba(52,211,153,0.2);  color:#34d399;  border:1px solid rgba(52,211,153,0.4); }
    .badge-blue   { background:rgba(96,165,250,0.2);  color:#60a5fa;  border:1px solid rgba(96,165,250,0.4); }
    .badge-orange { background:rgba(251,146,60,0.2);  color:#fb923c;  border:1px solid rgba(251,146,60,0.4); }
    .badge-red    { background:rgba(248,113,113,0.2); color:#f87171;  border:1px solid rgba(248,113,113,0.4); }
    .badge-yellow { background:rgba(251,191,36,0.2);  color:#fbbf24;  border:1px solid rgba(251,191,36,0.4); }

    /* ── Step log ── */
    .step-log-container {
        max-height: 320px; overflow-y: auto;
        padding-right: 4px;
        scrollbar-width: thin; scrollbar-color: rgba(139,92,246,0.4) transparent;
    }
    .step-item {
        display: flex; align-items: flex-start; gap: 10px;
        padding: 8px 10px; border-radius: 10px; margin-bottom: 6px;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
        transition: all 0.2s;
    }
    .step-item.current {
        background: rgba(139,92,246,0.15); border-color: rgba(139,92,246,0.5);
        box-shadow: 0 0 10px rgba(139,92,246,0.2);
    }
    .step-num {
        min-width: 28px; height: 28px; border-radius: 50%;
        background: rgba(99,102,241,0.3); color: #a78bfa;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.72rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;
    }
    .step-num.current { background: #7c3aed; color: white; }
    .step-content { flex: 1; }
    .step-action { font-size: 0.85rem; color: #e2e8f0; font-weight: 500; margin-bottom: 2px; }
    .step-detail { font-size: 0.75rem; color: #64748b; font-family: 'JetBrains Mono', monospace; }
    .tag { display:inline-block; padding:1px 7px; border-radius:4px; font-size:0.7rem; font-weight:600; margin-right:4px; }
    .tag-given   { background:rgba(99,102,241,0.3); color:#a78bfa; }
    .tag-deduced { background:rgba(52,211,153,0.2); color:#34d399; }
    .tag-backtrack { background:rgba(251,191,36,0.2); color:#fbbf24; }

    /* ── KB Domains table ── */
    .kb-table { border-collapse: collapse; margin: 0 auto; width: 100%; font-family: 'JetBrains Mono', monospace; }
    .kb-cell {
        padding: 6px 4px; text-align: center; font-size: 0.72rem;
        border: 1px solid rgba(255,255,255,0.07); border-radius: 6px;
        vertical-align: middle; line-height: 1.4;
        transition: all 0.2s;
    }
    .kb-cell.kb-given    { background:rgba(99,102,241,0.2); color:#a78bfa; font-weight:700; }
    .kb-cell.kb-solved   { background:rgba(52,211,153,0.15); color:#34d399; font-weight:700; }
    .kb-cell.kb-active   { background:rgba(251,191,36,0.2); color:#fbbf24; font-weight:700; border-color:#fbbf24; }
    .kb-cell.kb-narrowed { background:rgba(251,146,60,0.1); color:#fb923c; }
    .kb-cell.kb-full     { background:rgba(255,255,255,0.02); color:#475569; }
    .kb-cell.kb-empty    { background:rgba(248,113,113,0.2); color:#f87171; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white; border: none; border-radius: 10px;
        padding: 0.5rem 1.2rem; font-size: 0.9rem; font-weight: 600;
        width: 100%; transition: all 0.2s;
        box-shadow: 0 4px 15px rgba(124,58,237,0.4);
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(124,58,237,0.6); }
    div[data-testid="stSidebar"] { background: rgba(15,12,41,0.85); border-right: 1px solid rgba(255,255,255,0.08); }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stRadio"] label { color: #cbd5e1 !important; font-weight: 500; }
    .section-title { color:#94a3b8; font-size:0.72rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.5rem; }
    </style>
    """, unsafe_allow_html=True)
def loadPageFooter():
    st.markdown("---")
    st.markdown(
        '<p style="text-align:center;color:#334155;font-size:0.78rem;">'
        'Futoshiki Solver · Project 2 · Group NotAI</p>',
        unsafe_allow_html=True,
    )