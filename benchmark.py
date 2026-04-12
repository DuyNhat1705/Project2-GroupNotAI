import os
import copy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import multiprocessing
from problem.futoshiki import Futoshiki

from algorithms.forwardChaining import ForwardChaining
from algorithms.backwardChaining import BackwardChaining
from algorithms.SAT_solver import SATSolver
from algorithms.aStar import AStar
from algorithms.backTracking import Backtracking
from algorithms.bruteForce import BruteForce

from utils.logger import step_logger

TIMEOUT = 300  # 5 minutes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'Outputs')

def run_solver_worker(solver_class, problem, queue, astar_option=None):
    """
    Runs the solver and puts the logger results into the queue.
    """
    solver = solver_class()

    # Run the solver — pass heuristic option for AStar
    if astar_option is not None:
        grid = solver.solve(problem, option=astar_option)
    else:
        grid = solver.solve(problem)

    total_steps = len(step_logger.steps) if hasattr(step_logger, 'steps') else 0
    exec_time = step_logger.execution_time if hasattr(step_logger, 'execution_time') else 0

    queue.put({
        'time_ms': exec_time,
        'space_steps': total_steps,
        'solved': grid is not None
    })


def benchmark_puzzle(solvers, puzzle_file, puzzle_name):
    """Runs all solvers on a single puzzle with a strict timeout."""
    results = []

    problem = Futoshiki(puzzle_file)

    for solver_name, solver_info in solvers.items():
        print(f"Testing {solver_name} on {puzzle_name}...")

        solver_class = solver_info['class']
        astar_option = solver_info.get('option', None)

        problem_copy = copy.deepcopy(problem)

        queue = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=run_solver_worker,
            args=(solver_class, problem_copy, queue, astar_option)
        )

        p.start()
        p.join(TIMEOUT)

        if p.is_alive():
            print(f"  [!] {solver_name} TIMED OUT (> 5 mins). Terminating...")
            p.terminate()
            p.join()
            results.append({
                'Puzzle size': puzzle_name,
                'Solver': solver_name,
                'Time (ms)': TIMEOUT * 1000,
                'Space (Steps)': 0,
                'Status': 'Timeout'
            })
        else:
            if not queue.empty():
                data = queue.get()
                print(f"  [+] Finished in {data['time_ms']:.2f} ms with {data['space_steps']} steps.")
                results.append({
                    'Puzzle size': puzzle_name,
                    'Solver': solver_name,
                    'Time (ms)': data['time_ms'],
                    'Space (Steps)': data['space_steps'],
                    'Status': 'Solved' if data['solved'] else 'Failed'
                })
            else:
                results.append({
                    'Puzzle size': puzzle_name,
                    'Solver': solver_name,
                    'Time (ms)': TIMEOUT * 1000,
                    'Space (Steps)': 0,
                    'Status': 'Crash/Error'
                })

    return results


def export_json(df, output_filename="raw_result.json"):
    """Exports the benchmark dataframe to a JSON file."""
    full_path = os.path.join(OUTPUT_DIR, output_filename)
    print(f"Exporting raw data to JSON: {full_path}")
    df.to_json(full_path, orient='records', indent=4)


def _gen_charts(df):
    """Generates two separate chart images for Time and Space."""
    print("\nGenerating Charts: Benchmark_Time.pdf and Benchmark_Space.pdf")

    sns.set_theme(style="whitegrid")

    # Đã xóa màu của A* H3 để khớp với số lượng solver
    solver_names = df['Solver'].unique().tolist()
    distinct_colors = [
        '#E63946',  # red        — Backward Chaining
        '#F4A261',  # orange      — Forward Chaining
        '#2A9D8F',  # teal        — SAT
        '#457B9D',  # steel blue  — A* H1
        '#1D3557',  # dark navy   — A* H2
        '#6A0572',  # purple      — Backtracking
        '#8B8000',  # dark yellow — Brute Force
    ]
    palette = {name: distinct_colors[i % len(distinct_colors)] for i, name in enumerate(solver_names)}

    # --- Bảng 1: Execution Time ---
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df, x='Puzzle size', y='Time (ms)', hue='Solver', ax=ax1, palette=palette)
    ax1.set_title('Solver Execution Time', fontsize=14)
    ax1.set_ylabel('Execution Time (ms)')
    ax1.axhline(TIMEOUT * 1000, color='red', linestyle='--', label='5 Min Timeout')
    ax1.set_yscale('log')
    ax1.legend(title='Solver', bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
    plt.tight_layout()
    time_benchmark_path = os.path.join(OUTPUT_DIR, "Benchmark_Time.pdf")
    fig1.savefig(time_benchmark_path, dpi=300)
    plt.close(fig1)
    print(f" -> Saved at {time_benchmark_path}")

    # --- Bảng 2: Complexity (Total Steps) ---
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    df_solved = df[df['Status'] == 'Solved']
    sns.barplot(data=df_solved, x='Puzzle size', y='Space (Steps)', hue='Solver', ax=ax2, palette=palette)
    ax2.set_title('Search Space Complexity', fontsize=14)
    ax2.set_ylabel('Total Logged Steps (Given + Try + Backtrack + Deduced)')
    ax2.set_yscale('log')
    ax2.legend(title='Solver', bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
    plt.tight_layout()
    space_benchmark_path = os.path.join(OUTPUT_DIR, "Benchmark_Space.pdf")
    fig2.savefig(space_benchmark_path, dpi=300)
    plt.close(fig2)
    print(f" -> Saved at {space_benchmark_path}")


if __name__ == '__main__':

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    solvers = {
        'Backward Chaining':  {'class': BackwardChaining},
        'Forward Chaining':   {'class': ForwardChaining},
        'SAT':                {'class': SATSolver},
        'A* H1':              {'class': AStar, 'option': 1},
        'A* H2':              {'class': AStar, 'option': 2},
        'Backtracking':       {'class': Backtracking},
        'Brute Force':        {'class': BruteForce},
    }

    # Puzzle sizes to test
    puzzles = {
        '4x4_1': 'input-01',  # Rất dễ
        '4x4_2': 'input-02',  # Dễ
        '5x5_1': 'input-03',  # Trung bình
        '5x5_2': 'input-04',  # Trung bình - Khó
        '6x6_1': 'input-05',  # Khó
        '6x6_2': 'input-06',  # Khó - Ít gợi ý
        '7x7_1': 'input-07',  # Rất khó
        '7x7_2': 'input-08',  # Chuyên gia
        '8x8': 'input-09',    # Cực khó
        '9x9': 'input-10',    # Bậc thầy
    }

    all_results = []

    # Run Benchmarks
    for name, file_path in puzzles.items():
        results = benchmark_puzzle(solvers, file_path, name)
        all_results.extend(results)

    # Generate JSON & 2 separated charts
    df = pd.DataFrame(all_results)
    export_json(df)
    _gen_charts(df)
    print("Done!")