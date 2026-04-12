import time
from utils.logger import step_logger
from algorithms.base_algorithm import BaseAlgorithm
from pysat.solvers import Glucose3
# pip install python-sat


class SATSolver(BaseAlgorithm):
    def __init__(self, params=None):
        super().__init__("SAT Solver", params)

    def solve(self, problem):
        step_logger.reset(problem)
        start_time = time.perf_counter()
        print(f"SAT Solver for {problem.size}x{problem.size}...\n")

        sz = problem.size
        domains = self.init_domain(problem)

        # Map (Row, Col, Val) into a single 1-idx boolean int
        def var_id(r, c, v):
            return (r - 1) * sz * sz + (c - 1) * sz + v

        # parse constraint
        def get_sign(sign):
            if sign in [1, '<', '^']: return 1
            if sign in [-1, '>', 'v', 'V']: return -1
            return 0

        solver = Glucose3()

        # add given clues
        for r in range(1, sz + 1):
            for c in range(1, sz + 1):
                val = int(problem.grid[r - 1][c - 1]) if problem.grid[r - 1][c - 1] != 0 else 0
                if val != 0:
                    # Unit Clause: force the value
                    solver.add_clause([var_id(r, c, val)])
                    step_logger.log_step(r, c, val, tag='given',
                                         domains=dict(domains),
                                         facts_count=1)

        # cell uniqueness
        for r in range(1, sz + 1):
            for c in range(1, sz + 1):
                # At least one number per cell
                solver.add_clause([var_id(r, c, v) for v in range(1, sz + 1)])
                # At most one number per cell
                for v1 in range(1, sz + 1):
                    for v2 in range(v1 + 1, sz + 1):
                        solver.add_clause([-var_id(r, c, v1), -var_id(r, c, v2)])

        # Row & Column Uniqueness 
        for v in range(1, sz + 1):
            for i in range(1, sz + 1):
                for j1 in range(1, sz + 1):
                    for j2 in range(j1 + 1, sz + 1):
                        solver.add_clause([-var_id(i, j1, v), -var_id(i, j2, v)])
                        solver.add_clause([-var_id(j1, i, v), -var_id(j2, i, v)])

        # inequalities Constraints
        # Horizontal Constraints
        for r in range(1, sz + 1):
            for c in range(1, sz):
                sign = get_sign(problem.HorizontalConstraints[r - 1][c - 1])
                
                if sign == 1:  # Left < Right
                    for v1 in range(1, sz + 1):
                        for v2 in range(1, v1 + 1):  # If Left >= Right -> Contradiction
                            solver.add_clause([-var_id(r, c, v1), -var_id(r, c + 1, v2)])
                
                elif sign == -1:  # Left > Right
                    for v1 in range(1, sz + 1):
                        for v2 in range(v1, sz + 1):  # If Left <= Right -> Contradiction
                            solver.add_clause([-var_id(r, c, v1), -var_id(r, c + 1, v2)])

        # Vertical Constraints
        for r in range(1, sz):
            for c in range(1, sz + 1):
                sign = get_sign(problem.VerticalConstraints[r - 1][c - 1])
                if sign == 1:  # Top < Bottom
                    for v1 in range(1, sz + 1):
                        for v2 in range(1, v1 + 1):  # If Top >= Bottom -> Contradiction
                            solver.add_clause([-var_id(r, c, v1), -var_id(r + 1, c, v2)])
                elif sign == -1:  # Top > Bottom
                    for v1 in range(1, sz + 1):
                        for v2 in range(v1, sz + 1):  # If Top <= Bottom -> Contradiction
                            solver.add_clause([-var_id(r, c, v1), -var_id(r + 1, c, v2)])

        # C++ Engine
        if solver.solve():
            model = solver.get_model()

            # Reconstruct the grid from the true boolean variables
            for lit in model:
                if lit > 0:  # If True
                    lit -= 1  # get back to 0-idx
                    v = (lit % sz) + 1
                    lit //= sz
                    c = (lit % sz) + 1
                    r = (lit // sz) + 1

                    # Update board state
                    if problem.grid[r - 1][c - 1] == 0:  # log it if it wasn't a starting clue
                        problem.grid[r - 1][c - 1] = v
                        domains[(r, c)] = {v}
                        # Log the final deduced cell
                        step_logger.log_step(r, c, v, tag='deduced',
                                             domains=dict(domains),
                                             facts_count=sz * sz)

            step_logger.execution_time = (time.perf_counter() - start_time) * 1000
            print(f"\nPuzzle Solved by PySAT in {step_logger.execution_time:.2f}ms!")
            problem.printFutoshiki()
            solver.delete()
            return problem.grid
        else:
            step_logger.execution_time = (time.perf_counter() - start_time) * 1000
            print("\nFAILED: The SAT Solver proved no solution exists.")
            solver.delete()
            return problem.grid

    def init_domain(self, problem):
        domains = {}
        for r in range(problem.size):
            for c in range(problem.size):
                if problem.grid[r][c] == 0:
                    domains[(r + 1, c + 1)] = set(range(1, problem.size + 1)) # 1-indexed
                else:
                    domains[(r + 1, c + 1)] = {int(problem.grid[r][c])} # 1-indexed
        return domains