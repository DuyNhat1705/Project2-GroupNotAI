import os
ALGO_MAP = {
    "Forward Chaining": "fc",
    "Backward Chaining": "bc",
    "Backtracking": "bt",
    "Brute Force": "bf",
    "A* Search": "astar",
    "SAT Solver": "sat"
}

HEURISTIC_MAP = {
    "Heuristic 1 - Unassigned Cells": 1,
    "Heuristic 2 - Inequality Chains": 2
}

STEP_DELAY_OPTIONS = {
    "Slow (1.0s)": 1.0, 
    "Normal (0.5s)": 0.5, 
    "Fast (0.2s)": 0.2, 
    "Very Fast (0.05s)": 0.05
}
TIME_OUT = 15.0

TAG_BADGE_MAP = {
    'given': 'badge-magenta',
    'deduced': 'badge-green',
    'backtrack': 'badge-yellow',
}

TAG_STYLE_MAP = {
    'given': ('GIVEN', '#00f5ff', 'rgba(0, 245, 255, 0.15)'),
    'deduced': ('DEDUCED', '#00ff88', 'rgba(0, 255, 136, 0.15)'),
    'backtrack': ('BACKTRACK', '#ffdd00', 'rgba(255, 221, 0, 0.15)'),
}
COLOR_MAP = {
    "Backward Chaining": "#7b2ff7", 
    "Forward Chaining": "#00d4ff",  
    "SAT": "#ff006e",               
    "A* H1": "#fee440",
    "A* H2": "#ff9100",  
    "Backtracking": "#06d6a0",      
    "Brute Force": "#8d99ae"
}
INPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Inputs')