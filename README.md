# FUTOSHIKI SOLVER - GROUP 03 - GROUP NON-AI

This project is a Futoshiki puzzle solver (an inequality-based Sudoku variant) utilizing 6 different search and logic inference algorithms. The main objective is to solve Constraint Satisfaction Problems (CSP) and visualize the algorithm execution process on a modern user interface.

## 1. Algorithm System
The group has implemented and compared various approaches ranging from basic to advanced:
* **Brute Force & Backtracking:** Exhaustive and basic backtracking search to find solutions.
* **Forward & Backward Chaining:** Logic inference and constraint propagation to minimize search space.
* **A* Search:** Heuristic-based search to optimize branch selection process.
* **SAT Solver:** Converting the problem into Boolean Satisfiability form.

## 2. Project Structure
```text
Project2-GroupNotAI/
├── app.py                  # Entry point for Streamlit web interface
├── main.py                 # Quick CLI script execution
├── benchmark.py            # Tool for running tests and generating performance reports
├── requirements.txt        # List of required libraries
│
├── algorithms/             # Contains solver algorithm implementations
│   ├── base_algorithm.py   # Base class defining common structure
│   ├── bruteForce.py       # Brute force algorithm
│   ├── backTracking.py     # Backtracking algorithm
│   ├── forwardChaining.py  # Forward chaining algorithm
│   ├── backwardChaining.py # Backward chaining algorithm
│   ├── aStar.py            # A* algorithm with heuristic
│   ├── SAT_solver.py       # SAT-based solver
│   ├── algorithm_factory.py# Factory pattern for algorithm management
│   └── logic.py            # Logic utility functions
│
├── problem/                # Problem structure definition
│   └── futoshiki.py        # Grid logic, constraint checking, and file parsing
│
├── GUI/                    # User interface components
│   ├── visualPage.py       # Step-by-step puzzle solving visualization page
│   ├── analyticsPage.py    # Performance comparison chart page
│   ├── visualRender.py     # Grid rendering and visual effects
│   ├── webStyle.py         # Neon Cyberpunk UI styling
│   ├── helpers.py          # UI helper functions
│   └── constants.py        # UI configuration constants
│
├── Inputs/                 # Contains 10 test datasets (input-01 to 10)
├── Outputs/                # Stores results after solving (.json, .txt)
└── utils/                  # Support utilities (Logger, etc.)
```

## 3. Installation & Execution Guide
**Requirements:** Python 3.8 or higher.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Web Interface (Recommended):**
   ```bash
   streamlit run app.py
   ```

3. **Run Performance Benchmarking:**
   ```bash
   python benchmark.py
   ```

4. **Run Solving Futoshiki in Console**
   ```bash
   python main.py
   ```

## 4. Key Features
* **Step-by-step Visualization:** Slider allows detailed observation of number filling process and algorithm backtracking in real-time.
* **Performance Analytics:** Dashboard directly compares execution time, nodes explored, and backtrack count across algorithms.
* **Modern Interface:** Optimized user experience with Neon Cyberpunk style and responsive visual effects.

## 5. Input Data Format
Text files (`.txt`) in the `Inputs/` directory follow this structure:
* Line 1: Grid size (N).
* Next N lines: Initial grid values matrix (0 represents empty cells).
* Next section: Horizontal constraint matrix (N rows, N-1 columns).
* Final section: Vertical constraint matrix (N-1 rows, N columns).
*(Convention: 1 represents `<`, -1 represents `>`, 0 means no constraint)*

## 6. Project Team
**Group 03 - GROUP NON-AI**
| # | Full Name | Student ID |
|---|---|---|
| 1 | Nguyễn Lê Hoàng Khải | 24127408 |
| 2 | Vũ Duy Nhất | 24127095 |
| 3 | Trần Lê Hoàng Gia | 24127028 |
| 4 | Phan Lê Anh Minh | 24127082 |