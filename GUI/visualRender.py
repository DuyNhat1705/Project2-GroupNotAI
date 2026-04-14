from GUI.helpers import h_symbol, v_symbol
from GUI.constants import TAG_STYLE_MAP
import streamlit as st

def render_grid_html(puzzle, step=None, active_cell=None):
    n = puzzle.size
    original = puzzle.grid
    given_cells = {(i, j) for i in range(n) for j in range(n) if original[i][j] != 0}

    val_map = {}
    if step is not None:
        for (ri, cj), dom in step['domains_snapshot'].items():
            if len(dom) == 1:
                val_map[(ri-1, cj-1)] = next(iter(dom))

    html = '<table class="futoshiki-table" cellspacing="0">'
    for i in range(n):
        html += '<tr>'
        for j in range(n):
            is_given = (i, j) in given_cells
            is_active = active_cell == (i+1, j+1)
            has_val = (i, j) in val_map

            if is_active:
                css = 'cell active'
                val = str(val_map.get((i, j), ''))
            elif is_given:
                css = 'cell given'
                val = str(original[i][j])
            elif has_val and step is not None:
                css = 'cell solved'
                val = str(val_map[(i, j)])
            else:
                css = 'cell'
                val = ''

            html += f'<td class="{css}">{val}</td>'
            if j < n - 1:
                sym = h_symbol(puzzle.HorizontalConstraints[i][j])
                html += f'<td class="constraint-h">{sym}</td>'
        html += '</tr>'
        if i < n - 1:
            html += '<tr>'
            for j in range(n):
                sym = v_symbol(puzzle.VerticalConstraints[i][j])
                html += f'<td class="constraint-v">{sym}</td>'
                if j < n - 1:
                    html += '<td class="constraint-gap"></td>'
            html += '</tr>'
    html += '</table>'
    return html

def render_step_log_html(steps, current_idx):
    items_html = ''
    for idx, s in enumerate(steps):
        is_cur = (idx == current_idx)
        cur_id = 'id="step-active"' if is_cur else ''
        item_bg    = 'rgba(0,245,255,0.1)' if is_cur else 'rgba(30,20,60,0.6)'
        item_border= 'rgba(0,245,255,0.5)'  if is_cur else 'rgba(157,78,221,0.3)'
        num_bg     = '#00f5ff'               if is_cur else 'rgba(157,78,221,0.3)'
        num_color  = '#0a0e27'               if is_cur else '#c77dff'

        label, color, bg = TAG_STYLE_MAP.get(s['tag'], (s['tag'], '#0099ff', 'rgba(0, 153, 255, 0.15)'))
        tag_span = (f'<span style="display:inline-block;padding:2px 6px;border-radius:0px;'
                    f'font-size:0.68rem;font-weight:700;margin-right:5px;'
                    f'background:{bg};color:{color};border:1px solid {color};">{label}</span>')

        items_html += f'''
        <div {cur_id} style="display:flex;align-items:flex-start;gap:10px;
            padding:8px 10px;border-radius:0px;margin-bottom:6px;
            background:{item_bg};border:1px solid {item_border};">
          <div style="min-width:26px;height:26px;border-radius:0px;
              background:{num_bg};color:{num_color};
              display:flex;align-items:center;justify-content:center;
              font-size:0.7rem;font-weight:700;font-family:monospace;flex-shrink:0;border:1px solid {num_bg};">{s["step_num"]}</div>
          <div style="flex:1;">
            <div style="font-size:0.84rem;color:#00f5ff;font-weight:700;margin-bottom:2px;text-shadow:0 0 5px #00f5ff;">
              {tag_span} VALUE: {s["action"]}
            </div>
            <div style="font-size:0.73rem;color:#c77dff;font-family:monospace;text-shadow:0 0 3px #9d4edd;">
              facts: {s["facts_count"]} &nbsp;|&nbsp; cell ({s["cell"][0]},{s["cell"][1]})
            </div>
          </div>
        </div>'''

    scroll_js = '''
    <script>
      (function() {
        var wrapper = document.getElementById('log-wrapper');
        var el = document.getElementById('step-active');

        if (wrapper && el) {
            wrapper.scrollTop = el.offsetTop - wrapper.offsetTop;
        }
        if (wrapper) wrapper.style.visibility = 'visible';
      })();
    </script>'''

    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head><style>
      body {{
        margin: 0; padding: 0;
        background: transparent;
        font-family: 'JetBrains Mono', monospace;
        overflow-x: hidden;
      }}
      ::-webkit-scrollbar {{ width: 5px; }}
      ::-webkit-scrollbar-track {{ background: transparent; }}
      ::-webkit-scrollbar-thumb {{ background: rgba(0, 245, 255, 0.4); border-radius: 99px; }}
    </style></head>
    <body>
      <div id="log-wrapper" style="max-height:215px;overflow-y:auto;padding-right:4px;visibility:hidden;">
        {items_html}
      </div>
      {scroll_js}
    </body>
    </html>'''  
    return full_html

def render_kb_domains_html(puzzle, step, highlight_cell=None):
    n = puzzle.size
    given_cells = {(i+1, j+1) for i in range(n) for j in range(n) if puzzle.grid[i][j] != 0}
    full_size = n

    if step is None:
        # Initial state
        domains = {}
        for i in range(1, n+1):
            for j in range(1, n+1):
                v = puzzle.grid[i-1][j-1]
                domains[(i,j)] = frozenset({v} if v != 0 else set(range(1, n+1)))
    else:
        domains = step['domains_snapshot']

    html = '<table class="kb-table" cellspacing="3">'
    # Header row (col indices)
    html += '<tr><td style="width:22px;color:#c77dff;font-size:0.7rem;text-shadow:0 0 3px #9d4edd;"></td>'
    for j in range(1, n+1):
        html += f'<td style="text-align:center;color:#c77dff;font-size:0.7rem;font-weight:600;text-shadow:0 0 3px #9d4edd;">c{j}</td>'
    html += '</tr>'

    for i in range(1, n+1):
        html += f'<tr><td style="color:#c77dff;font-size:0.7rem;font-weight:600;padding:2px 4px;text-shadow:0 0 3px #9d4edd;">r{i}</td>'
        for j in range(1, n+1):
            dom = domains.get((i, j), frozenset())
            size = len(dom)
            is_given    = (i, j) in given_cells
            is_active   = (highlight_cell == (i, j))
            is_empty    = (size == 0)
            is_solved   = (size == 1)
            is_narrowed = (1 < size < full_size)

            if is_empty:
                css = 'kb-cell kb-empty'
                text = '∅'
            elif is_active:
                css = 'kb-cell kb-active'
                text = str(next(iter(dom)))
            elif is_given:
                css = 'kb-cell kb-given'
                text = str(next(iter(dom)))
            elif is_solved:
                css = 'kb-cell kb-solved'
                text = str(next(iter(dom)))
            elif is_narrowed:
                css = 'kb-cell kb-narrowed'
                text = '{' + ','.join(str(x) for x in sorted(dom)) + '}'
            else:
                css = 'kb-cell kb-full'
                text = '1..'+str(n)

            html += f'<td class="{css}" title="Domain ({i},{j}): {sorted(dom)}">{text}</td>'
        html += '</tr>'
    html += '</table>'
    return html
def apply_grid_size(grid_size):
    if grid_size <= 5:
        base_size = 52
    elif grid_size <= 7:
        base_size = 42
    else:
        base_size = 30  # Size 9x9

    st.markdown(f"""
        <style>
        :root {{
            --cell-size: {base_size}px;
            --h-constraint-width: calc(var(--cell-size) / 2);
            --v-constraint-height: calc(var(--cell-size) / 2.3);
        }}
        </style>
    """, unsafe_allow_html=True)