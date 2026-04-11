import streamlit as st
import streamlit.components.v1 as components
def loadPageLayout():
    st.set_page_config(page_title="Futoshiki Solver", page_icon="🧩", layout="wide")
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=JetBrains+Mono:wght@400;600&display=swap');
    
    * { box-sizing: border-box; }
                
    div[data-testid="stToolbarActions"],
    div[data-testid="stDecoration"],
    #MainMenu { display: none !important; }

    html, body, [class*="css"] { 
        font-family: 'JetBrains Mono', monospace;
    }
                
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
        display: none;
    }
    .stApp {
        background: #0a0e27;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Scanline effect overlay */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            0deg,
            rgba(0, 0, 0, 0.15),
            rgba(0, 0, 0, 0.15) 2px,
            transparent 2px,
            transparent 4px
        );
        pointer-events: none;
        z-index: 999;
    }
    
    /* Hero Title - Neon Cyan Glow */
    .hero-title {
        font-family: 'Press Start 2P', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #00f5ff;
        text-align: center;
        margin-bottom: 0.2rem;
        text-shadow: 
            0 0 10px #00f5ff,
            0 0 20px #00f5ff,
            0 0 30px #0099cc,
            0 0 40px #0066ff;
        letter-spacing: 3px;
        animation: neon-flicker 3s infinite;
    }
    
    @keyframes neon-flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
            text-shadow: 
                0 0 10px #00f5ff,
                0 0 20px #00f5ff,
                0 0 30px #0099cc,
                0 0 40px #0066ff;
        }
        20%, 24%, 55% {
            text-shadow: 
                0 0 5px #00f5ff,
                0 0 10px #0099cc;
        }
    }
    
    /* Hero Subtitle - Vibrant Magenta */
    .hero-sub {
        text-align: center;
        color: #ff006e;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        text-shadow: 
            0 0 8px #ff006e,
            0 0 15px #ec0076,
            0 0 20px #c41e3a;
        letter-spacing: 2px;
    }
    
    :root {
    --cell-size: 52px;
    --h-constraint-width: calc(var(--cell-size) / 2);
    --v-constraint-height: calc(var(--cell-size) / 2.3);
    }  
    /* ── Futoshiki Grid - Neon Purple & Magenta ── */
    .futoshiki-table { 
        table-layout: fixed;
        border-collapse: separate; 
        border-spacing: 4px;
        margin: 0 auto;
        width: max-content;
        font-family: 'JetBrains Mono', monospace;
        overflow: visible;
    }
    
    .cell {
        width: var(--cell-size); 
        height: var(--cell-size);
        aspect-ratio: 1 / 1;
        box-sizing: border-box;
        display: table-cell;
        background-clip: padding-box;
                
        text-align: center; 
        vertical-align: middle;
        font-size: calc(var(--cell-size) * 0.4); 
        font-weight: 600;
        border: 3px solid #9d4edd;
        border-radius: 0px;
        background: rgba(30, 20, 60, 0.9);
        color: #00f5ff;
        transition: all 0.25s ease;
        box-shadow: 
            0 0 8px rgba(157, 78, 221, 0.4),
            inset 0 0 10px rgba(157, 78, 221, 0.2);
        text-shadow: 0 0 5px #00f5ff;
        transform-origin: top left;
    }
    
    .cell.given {
        border: 3px solid #c77dff;
        background: rgba(157, 78, 221, 0.3);
        color: #c77dff;
        box-shadow: 
            0 0 12px rgba(199, 125, 255, 0.5),
            inset 0 0 10px rgba(199, 125, 255, 0.2);
        text-shadow: 0 0 8px #c77dff;
    }
    
    .cell.solved {
        border: 3px solid #00ffff;
        background: rgba(0, 245, 255, 0.15);
        color: #00ffff;
        box-shadow: 
            0 0 15px rgba(0, 255, 255, 0.6),
            inset 0 0 10px rgba(0, 255, 255, 0.2);
        text-shadow: 0 0 10px #00ffff;
        animation: popIn 0.35s ease;
    }
    
    .cell.active {
        border: 3px solid #ff006e;
        background: rgba(255, 0, 110, 0.25);
        color: #ff006e;
        box-shadow: 
            0 0 20px rgba(255, 0, 110, 0.8),
            inset 0 0 10px rgba(255, 0, 110, 0.3);
        text-shadow: 0 0 10px #ff006e;
        animation: pulse 1s infinite;
    }
    
    @keyframes popIn { 
        0% { transform: scale(0.75); opacity: 0; } 
        100% { transform: scale(1); opacity: 1; } 
    }
    
    @keyframes pulse { 
        0%, 100% { box-shadow: 0 0 10px rgba(255, 0, 110, 0.6), inset 0 0 10px rgba(255, 0, 110, 0.3); } 
        50% { box-shadow: 0 0 25px rgba(255, 0, 110, 1), inset 0 0 10px rgba(255, 0, 110, 0.3); } 
    }
    
    .constraint-h { 
        width: var(--h-constraint-width);
        height: var(--cell-size);
        aspect-ratio: 1 / 2;
        box-sizing: border-box;
        display: table-cell;
        border: none;
        text-align: center; 
        vertical-align: middle; 
        font-size: 1rem; 
        font-weight: 700; 
        color: #00f5ff;
        text-shadow: 0 0 5px #00f5ff;
    }
    
    .constraint-v { 
        width: var(--cell-size); 
        height: var(--v-constraint-height);
        box-sizing: border-box;
        display: table-cell;
        border: none;
        text-align: center; 
        vertical-align: middle; 
        font-size: 1rem; 
        font-weight: 700; 
        color: #00f5ff;
        text-shadow: 0 0 5px #00f5ff;
    }
    
    .constraint-gap { width: var(--h-constraint-width); height: var(--v-constraint-height); padding: 0; }
    
    /* ── Stat Badges - Neon Style ── */
    .stat-badge { 
        display: inline-block; 
        padding: 0.35rem 0.8rem; 
        border-radius: 0px;
        font-size: 0.75rem; 
        font-weight: 700;
        margin: 0.25rem;
        border: 2px solid;
        letter-spacing: 1px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .badge-cyan { 
        background: rgba(0, 245, 255, 0.15);
        color: #00f5ff;
        border-color: #00f5ff;
        box-shadow: 0 0 8px rgba(0, 245, 255, 0.4);
        text-shadow: 0 0 5px #00f5ff;
    }
    
    .badge-magenta { 
        background: rgba(255, 0, 110, 0.15);
        color: #ff006e;
        border-color: #ff006e;
        box-shadow: 0 0 8px rgba(255, 0, 110, 0.4);
        text-shadow: 0 0 5px #ff006e;
    }
    
    .badge-purple { 
        background: rgba(157, 78, 221, 0.2);
        color: #c77dff;
        border-color: #9d4edd;
        box-shadow: 0 0 8px rgba(157, 78, 221, 0.4);
        text-shadow: 0 0 5px #9d4edd;
    }
    
    .badge-green { 
        background: rgba(0, 200, 100, 0.2);
        color: #00ff88;
        border-color: #00cc66;
        box-shadow: 0 0 8px rgba(0, 255, 136, 0.4);
        text-shadow: 0 0 5px #00ff88;
    }
    
    .badge-blue { 
        background: rgba(0, 153, 255, 0.2);
        color: #0099ff;
        border-color: #0066ff;
        box-shadow: 0 0 8px rgba(0, 153, 255, 0.4);
        text-shadow: 0 0 5px #0099ff;
    }
    
    .badge-orange { 
        background: rgba(255, 150, 0, 0.2);
        color: #ffaa00;
        border-color: #ff9900;
        box-shadow: 0 0 8px rgba(255, 150, 0, 0.4);
        text-shadow: 0 0 5px #ffaa00;
    }
    
    .badge-yellow { 
        background: rgba(255, 200, 0, 0.2);
        color: #ffdd00;
        border-color: #ffcc00;
        box-shadow: 0 0 8px rgba(255, 200, 0, 0.4);
        text-shadow: 0 0 5px #ffdd00;
    }
    
    /* ── Buttons - Neon Red/Blue ── */
    .stButton > button {
        background: linear-gradient(135deg, #ff006e, #d4006e);
        color: #00f5ff;
        border: 2px solid #ff006e;
        border-radius: 0px;
        
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0.5rem 0.1rem !important;
        
        font-size: 0.7rem !important;
        font-weight: 700;
        letter-spacing: 0px !important;
        white-space: nowrap !important;
        
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        min-width: 0px !important;
        font-family: 'JetBrains Mono', monospace;
        transition: all 0.2s;
        box-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
        text-shadow: 0 0 5px rgba(0, 245, 255, 0.5);
        cursor: pointer;
        
    }
    
    .stButton > button:hover {
        box-shadow: 
            0 0 20px rgba(255, 0, 110, 0.8),
            inset 0 0 15px rgba(0, 245, 255, 0.2);
        transform: translateY(-2px);
    }
    div[data-testid="column"] {
        padding-left: 1px !important;
        padding-right: 1px !important;
    }
    /* ── Sidebar ── */
    div[data-testid="stSidebar"] { 
        background: rgba(10, 14, 39, 0.95);
        border-right: 3px solid #9d4edd;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.3);
    }
    
    /* ── Labels ── */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stRadio"] label { 
        color: #00f5ff !important;
        font-weight: 700;
        text-shadow: 0 0 5px #00f5ff;
        letter-spacing: 1px;
    }
    
    /* ── Section Titles ── */
    .section-title { 
        color: #00f5ff;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 8px #00f5ff;
    }
    
    /* ── Step Log ── */
    .step-log-container {
        max-height: 320px;
        overflow-y: auto;
        padding-right: 4px;
        scrollbar-width: thin;
        scrollbar-color: rgba(0, 245, 255, 0.4) transparent;
    }
    
    .step-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 8px 10px;
        border-radius: 0px;
        margin-bottom: 6px;
        background: rgba(30, 20, 60, 0.6);
        border: 1px solid rgba(157, 78, 221, 0.3);
        transition: all 0.2s;
    }
    
    .step-item.current {
        background: rgba(0, 245, 255, 0.1);
        border-color: #00f5ff;
        box-shadow: 
            0 0 15px rgba(0, 245, 255, 0.4),
            inset 0 0 10px rgba(0, 245, 255, 0.1);
    }
    
    .step-num {
        min-width: 28px;
        height: 28px;
        border-radius: 0px;
        background: rgba(157, 78, 221, 0.3);
        color: #c77dff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid #9d4edd;
        box-shadow: 0 0 5px rgba(157, 78, 221, 0.4);
    }
    
    .step-num.current { 
        background: #9d4edd;
        color: #00f5ff;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.6);
    }
    
    .step-content { flex: 1; }
    
    .step-action { 
        font-size: 0.85rem;
        color: #00f5ff;
        font-weight: 700;
        margin-bottom: 2px;
        text-shadow: 0 0 5px #00f5ff;
    }
    
    .step-detail { 
        font-size: 0.75rem;
        color: #c77dff;
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 3px #9d4edd;
    }
    
    .tag { 
        display: inline-block;
        padding: 2px 6px;
        border-radius: 0px;
        font-size: 0.65rem;
        font-weight: 700;
        margin-right: 4px;
        border: 1px solid;
        letter-spacing: 0.5px;
    }
    
    .tag-given { 
        background: rgba(157, 78, 221, 0.3);
        color: #c77dff;
        border-color: #9d4edd;
        box-shadow: 0 0 5px rgba(157, 78, 221, 0.3);
    }
    
    .tag-deduced { 
        background: rgba(0, 200, 100, 0.2);
        color: #00ff88;
        border-color: #00cc66;
        box-shadow: 0 0 5px rgba(0, 200, 100, 0.3);
    }
    
    .tag-backtrack { 
        background: rgba(255, 200, 0, 0.2);
        color: #ffdd00;
        border-color: #ffcc00;
        box-shadow: 0 0 5px rgba(255, 200, 0, 0.3);
    }
    
    /* ── KB Domains Table ── */
    .kb-table { 
        border-collapse: collapse;
        margin: 0 auto;
        width: 100%;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .kb-cell {
        padding: 6px 4px;
        text-align: center;
        font-size: 0.72rem;
        border: 1px solid rgba(157, 78, 221, 0.4);
        border-radius: 0px;
        vertical-align: middle;
        line-height: 1.4;
        transition: all 0.2s;
        font-weight: 600;
    }
    
    .kb-cell.kb-given {
        background: rgba(157, 78, 221, 0.25);
        color: #c77dff;
        box-shadow: inset 0 0 5px rgba(157, 78, 221, 0.2);
    }
    
    .kb-cell.kb-solved {
        background: rgba(0, 200, 100, 0.2);
        color: #00ff88;
        box-shadow: inset 0 0 5px rgba(0, 200, 100, 0.2);
    }
    
    .kb-cell.kb-active {
        background: rgba(255, 0, 110, 0.25);
        color: #ff006e;
        border-color: #ff006e;
        box-shadow: 0 0 8px rgba(255, 0, 110, 0.4);
    }
    
    .kb-cell.kb-narrowed {
        background: rgba(255, 150, 0, 0.15);
        color: #ffaa00;
        box-shadow: inset 0 0 5px rgba(255, 150, 0, 0.2);
    }
    
    .kb-cell.kb-full {
        background: rgba(100, 80, 150, 0.1);
        color: #9d9dff;
        box-shadow: inset 0 0 5px rgba(157, 78, 221, 0.1);
    }
    
    .kb-cell.kb-empty {
        background: transparent;
        color: transparent;
        box-shadow: none;
        border: none;
    }
    
    /* ── Headings ── */
    h1, h2, h3, h4, h5, h6 {
        color: #00f5ff !important;
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.5) !important;
        letter-spacing: 2px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* ── Text ── */
    p, div, span {
        color: #e0e0ff;
    }
    
    /* Signature */
    .pixel-signature {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-family: 'Press Start 2P', monospace;
        font-size: 0.6rem;
        color: #c77dff;
        text-shadow: 0 0 5px #9d4edd;
        opacity: 0.6;
        pointer-events: none;
        z-index: 1000;
    }
                
    header[data-testid="stHeader"] {
    background: #0a0e27 !important;
    box-shadow: none !important;
    border-bottom: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    components.html("""
    <script>
    (function hide() {
        var btns = window.parent.document.querySelectorAll('header button');
        var found = false;
        btns.forEach(function(btn) {
            if (btn.innerText && btn.innerText.trim() === 'Deploy') {
                btn.style.display = 'none';
                found = true;
            }
        });
        if (!found) setTimeout(hide, 300);
    })();
    </script>
    """, height=0)
    
def loadPageFooter():
    st.markdown(
        '<hr style="border-color:#0a0e27;margin:0;">'
        '<p style="text-align:center;color:#0a0e27;font-size:0.7rem;">FUTOSHIKI SOLVER</p>',
        unsafe_allow_html=True,
    )

def render_badge(text, badge_class):
    """Helper to render a stat badge."""
    return f'<span class="stat-badge {badge_class}">{text}</span>'

def glass_card_open():
    """Open a glass card container."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

def glass_card_close():
    """Close a glass card container."""
    st.markdown('</div>', unsafe_allow_html=True)

def renderGridLegend():
    """Render Grid Legend with colored blocks"""
    return '''**Grid Legend:**
<div style="display:flex;flex-direction:column;gap:0.5rem;margin-bottom:1rem;">
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#c77dff;border:2px solid #9d4edd;"></span>Given (provided in the puzzle)</div>
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#00ff88;border:2px solid #00cc66;"></span>Solved (found solutions)</div>
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#ff006e;border:2px solid #ff006e;"></span>Active (currently being processed)</div>
</div>'''

def renderKBLegend():
    """Render KB Legend with colored blocks"""
    return '''**KB Legend:**
<div style="display:flex;flex-direction:column;gap:0.5rem;">
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#c77dff;border:2px solid #9d4edd;"></span>Given – fixed domain</div>
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#00ff88;border:2px solid #00cc66;"></span>Solved – confirmed solution</div>
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#ff006e;border:2px solid #ff006e;"></span>Active – processed in this step</div>
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:#ffaa00;border:2px solid #ff9900;"></span>Narrowed – domain narrowed down</div>
<div style="display:flex;align-items:center;gap:1rem;"><span style="display:inline-block;width:24px;height:24px;background:rgba(100,80,150,0.2);border:2px solid #9d9dff;"></span>Full domain (1...N)</div>
</div>'''

def renderKBTabLegend():
    """Render KB Tab legend - compact horizontal version"""
    return (
        '<div style="font-size:0.72rem;color:#c77dff;margin-bottom:0.5rem;font-family:JetBrains Mono,monospace;text-shadow:0 0 5px #9d4edd;display:flex;gap:1rem;flex-wrap:wrap;align-items:center;">'
        '<div style="display:flex;align-items:center;gap:0.5rem;"><span style="display:inline-block;width:16px;height:16px;background:#c77dff;border:1px solid #9d4edd;"></span>GIVEN</div>'
        '<div style="display:flex;align-items:center;gap:0.5rem;"><span style="display:inline-block;width:16px;height:16px;background:#00ff88;border:1px solid #00cc66;"></span>SOLVED</div>'
        '<div style="display:flex;align-items:center;gap:0.5rem;"><span style="display:inline-block;width:16px;height:16px;background:#ff006e;border:1px solid #ff006e;"></span>ACTIVE</div>'
        '<div style="display:flex;align-items:center;gap:0.5rem;"><span style="display:inline-block;width:16px;height:16px;background:#ffaa00;border:1px solid #ff9900;"></span>NARROWED</div>'
        '<div style="display:flex;align-items:center;gap:0.5rem;"><span style="display:inline-block;width:16px;height:16px;background:rgba(100,80,150,0.2);border:1px solid #9d9dff;"></span>FULL</div>'
        '</div>'
    )