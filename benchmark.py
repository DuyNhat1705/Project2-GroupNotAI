import time
import copy
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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


def run_solver_worker(solver_class, problem, queue):
    """
    runs the solver and puts the logger results into the queue.
    """
    solver = solver_class()

    # Run the solver
    grid = solver.solve(problem)

    # Extract metrics from the logger
    total_steps = len(step_logger.steps) if hasattr(step_logger, 'steps') else 0
    exec_time = step_logger.execution_time if hasattr(step_logger, 'execution_time') else 0

    # Pass data back to the main process
    queue.put({
        'time_ms': exec_time,
        'space_steps': total_steps,
        'solved': grid is not None
    })


def benchmark_puzzle(solvers, puzzle_file, puzzle_name):
    """Runs all solvers on a single puzzle with a strict timeout."""
    results = []

    # Load your puzzle once
    problem = Futoshiki(puzzle_file)

    for solver_name, solver_class in solvers.items():
        print(f"Testing {solver_name} on {puzzle_name}...")

        problem_copy = copy.deepcopy(problem)

        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_solver_worker, args=(solver_class, problem_copy, queue))
        p = multiprocessing.Process(target=run_solver_worker,
                                    args=(solver_class, problem_copy, queue))  # Replace None with problem_copy

        p.start()
        p.join(TIMEOUT)

        if p.is_alive():
            print(f"  [!] {solver_name} TIMED OUT (> 5 mins). Terminating...")
            p.terminate()
            p.join()
            results.append({
                'Puzzle size': puzzle_name,
                'Solver': solver_name,
                'Time (ms)': TIMEOUT * 1000,  # Max out the graph
                'Space (Steps)': 0,  # Or set to None/NaN
                'Status': 'Timeout'
            })
        else:
            # Solved in allowed time
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
                # Process crashed
                results.append({
                    'Puzzle size': puzzle_name,
                    'Solver': solver_name,
                    'Time (ms)': TIMEOUT * 1000,
                    'Space (Steps)': 0,
                    'Status': 'Crash/Error'
                })
    return results

def export_json(df, output_filename="raw_result.json"):
    """
    Exports the benchmark dataframe to a JSON file.
    """
    print(f"Exporting raw data to JSON: {output_filename}")
    df.to_json(output_filename, orient='records', indent=4)


def _gen_pdf(df, output_filename="Benchmark_graph.pdf"):
    """Generates a PDF containing bar charts for Time and Space."""
    print(f"\nGenerating PDF Report: {output_filename}")

    sns.set_theme(style="whitegrid")

    with PdfPages(output_filename) as pdf:
        # --- Execution Time ---
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df, x='Puzzle', y='Time (ms)', hue='Solver', ax=ax, palette='viridis')
        ax.set_title('Solver Execution Time', fontsize=14)
        ax.set_ylabel('Execution Time (ms)')
        ax.axhline(TIMEOUT * 1000, color='red', linestyle='--', label='5 Min Timeout')
        ax.set_yscale('log')
        plt.legend(title='Solver')
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

        # --- Complexity (Total Steps) ---
        fig, ax = plt.subplots(figsize=(10, 6))

        # Filter out timeouts
        df_solved = df[df['Status'] == 'Solved']

        sns.barplot(data=df_solved, x='Puzzle', y='Space (Steps)', hue='Solver', ax=ax, palette='mako')
        ax.set_title('Search Space Complexity', fontsize=14)
        ax.set_ylabel('Total Logged Steps (Given + Try + Backtrack + Deduced)')
        # Log scale is good here too, Backtracking steps explode on hard puzzles
        ax.set_yscale('log')
        plt.legend(title='Solver')
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()

if __name__ == '__main__':
    # Define the solvers to test
    solvers = {
         'Backward Chaining': BackwardChaining,
         'Forward Chaining': ForwardChaining,
         'SAT': SATSolver,
         'A* Search': AStar,
         'Backtracking': Backtracking,
         'Brute Force': BruteForce,
    }

    # puzzle size to test (e.g., 5x5, 7x7, 9x9)
    puzzles = {
        '4x4': 'input-02',
        '5x5': 'input-04',
        '6x6': 'input-06',
        '7x7': 'input-08',
        '9x9': 'input-09'
    }

    all_results = []

    #Run Benchmarks
    for name, file_path in puzzles.items():
        results = benchmark_puzzle(solvers, file_path, name)
        all_results.extend(results)

    # Generate PDF & JSON
    df = pd.DataFrame(all_results)
    export_json(df)
    _gen_pdf(df)
    print("Done!")