from algorithms.base_algorithm import BaseAlgorithm
import heapq
import time
import sys
from utils.logger import step_logger


class AStar(BaseAlgorithm):
    def __init__(self, params = None):
        self.remaining = 0
        super().__init__("A*", params)  
        
    def constraint(self, problem):
        """
        Computes a comprehensive constraint grid for all cells.

        Args:
            problem (tuple): The original horizontal and vertical constraint definitions.

        Returns:
            list[list]: A grid where each cell contains its specific logic or 
                        numerical constraints based on the initial problem.
        """
        
        rows = len(problem.grid)       
        cols = len(problem.grid[0])    
        max_val = rows
        
        # Copy problem.grid size not value
        c_grid = [[set() for _ in range(cols)] for _ in range(rows)]
        highest_constraint = -1
        i, j = -1, -1
        self.remaining = 0 # Reset remaining count

        for row in range(rows):
            for col in range(cols):

                # If there is a number
                value = problem.grid[row][col]

                if value != 0:
                    # Increase constraint value of the whole row 
                    for r in range(rows):
                        c_grid[r][col].add(value)

                    # Increase constraint value of the whole col    
                    for c in range(cols):
                        c_grid[row][c].add(value)

        # Calculate Horizontal constraints
        for r in range(rows):
            for c in range(len(problem.HorizontalConstraints[r])):
                relation = problem.HorizontalConstraints[r][c]
                left_value = problem.grid[r][c]
                right_value = problem.grid[r][c + 1]
                
                # Left < Right
                if relation == 1:
                    c_grid[r][c].add(max_val) 
                    c_grid[r][c + 1].add(1)     
                    
                    if right_value != 0:
                        for v in range(right_value, max_val + 1): 
                            c_grid[r][c].add(v)
                    if left_value != 0:
                        for v in range(1, left_value + 1): 
                            c_grid[r][c + 1].add(v)
                        
                # Left > Right
                elif relation == -1:
                    c_grid[r][c].add(1)       
                    c_grid[r][c + 1].add(max_val) 
                    
                    if right_value != 0:
                        for v in range(1, right_value + 1): 
                            c_grid[r][c].add(v)
                    if left_value != 0:
                        for v in range(left_value, max_val + 1): 
                            c_grid[r][c + 1].add(v)

        # Calculate Vertical constraints
        for r in range(len(problem.VerticalConstraints)):
            for c in range(cols):
                relation = problem.VerticalConstraints[r][c]
                val_top = problem.grid[r][c]
                val_bottom = problem.grid[r + 1][c]
                
                # Top < Bottom
                if relation == 1:
                    c_grid[r][c].add(max_val)
                    c_grid[r + 1][c].add(1)
                    
                    if val_bottom != 0:
                        for v in range(val_bottom, max_val + 1): 
                            c_grid[r][c].add(v)
                    if val_top != 0:
                        for v in range(1, val_top + 1): 
                            c_grid[r + 1][c].add(v)
                        
                # Top > Bottom
                elif relation == -1:
                    c_grid[r][c].add(1)
                    c_grid[r + 1][c].add(max_val)
                    
                    if val_bottom != 0:
                        for v in range(1, val_bottom + 1): 
                            c_grid[r][c].add(v)
                    if val_top != 0:
                        for v in range(val_top, max_val + 1): 
                            c_grid[r + 1][c].add(v)

        # Find the varible with the most constraint cell for starting point
        for r in range(rows):
            for c in range(cols):
                set_size = 0
                if problem.grid[r][c] == 0: 
                    self.remaining += 1
                    set_size = len(c_grid[r][c])

                    # Update when more constraint found
                    if highest_constraint < set_size:
                        highest_constraint = set_size
                        (i, j) = (r, c)

        # Return the constaints grid and the most constraint cell position
        return i, j, c_grid

    def propagate(self, problem, temp_grid, temp_c_grid, row, col, value):
        """
        Lightweight domain refinement after assigning a value to (row, col).

        Updates the constraint sets of all peers in the same row/column and
        of the four direct inequality neighbours. Does NOT force-assign any
        cell (no AC-3 queue).

        Args:
            problem: The problem object carrying HorizontalConstraints and
                     VerticalConstraints.
            temp_grid (list[list]): Grid state with the new value already placed.
            temp_c_grid (list[list]): Constraint (excluded-values) sets to update.
            row (int): Row of the just-assigned cell.
            col (int): Column of the just-assigned cell.
            value (int): Value that was assigned.

        Returns:
            bool: False if any unassigned cell's domain becomes empty (dead end),
                  True otherwise.
        """

        n = len(temp_grid)

        # --- Row & column peers: remove `value` from their available domain ---
        for i in range(n):
            if i != row and temp_grid[i][col] == 0:
                temp_c_grid[i][col].add(value)
                if len(temp_c_grid[i][col]) == n:   # domain is now empty
                    return False

            if i != col and temp_grid[row][i] == 0:
                temp_c_grid[row][i].add(value)
                if len(temp_c_grid[row][i]) == n:
                    return False

        # --- Inequality neighbours ---

        # Left cell  (HorizontalConstraints[row][col-1] describes left OP current)
        if col > 0 and temp_grid[row][col - 1] == 0:
            relation = problem.HorizontalConstraints[row][col - 1]

            if relation == 1:       # left < value  →  left cannot be >= value
                for val in range(value, n + 1):
                    temp_c_grid[row][col - 1].add(val)
            elif relation == -1:    # left > value  →  left cannot be <= value
                for val in range(1, value + 1):
                    temp_c_grid[row][col - 1].add(val)

            if len(temp_c_grid[row][col - 1]) == n:
                return False

        # Right cell  (HorizontalConstraints[row][col] describes current OP right)
        if col < n - 1 and temp_grid[row][col + 1] == 0:
            relation = problem.HorizontalConstraints[row][col]

            if relation == 1:       # value < right  →  right cannot be <= value
                for val in range(1, value + 1):
                    temp_c_grid[row][col + 1].add(val)
            elif relation == -1:    # value > right  →  right cannot be >= value
                for val in range(value, n + 1):
                    temp_c_grid[row][col + 1].add(val)

            if len(temp_c_grid[row][col + 1]) == n:
                return False

        # Up cell  (VerticalConstraints[row-1][col] describes up OP current)
        if row > 0 and hasattr(problem, 'VerticalConstraints') and temp_grid[row - 1][col] == 0:
            relation = problem.VerticalConstraints[row - 1][col]

            if relation == 1:       # up < value  →  up cannot be >= value
                for val in range(value, n + 1):
                    temp_c_grid[row - 1][col].add(val)
            elif relation == -1:    # up > value  →  up cannot be <= value
                for val in range(1, value + 1):
                    temp_c_grid[row - 1][col].add(val)

            if len(temp_c_grid[row - 1][col]) == n:
                return False

        # Down cell  (VerticalConstraints[row][col] describes current OP down)
        if row < n - 1 and hasattr(problem, 'VerticalConstraints') and temp_grid[row + 1][col] == 0:
            relation = problem.VerticalConstraints[row][col]

            if relation == 1:       # value < down  →  down cannot be <= value
                for val in range(1, value + 1):
                    temp_c_grid[row + 1][col].add(val)
            elif relation == -1:    # value > down  →  down cannot be >= value
                for val in range(value, n + 1):
                    temp_c_grid[row + 1][col].add(val)
                    
            if len(temp_c_grid[row + 1][col]) == n:
                return False

        return True

    def heuristic(self, problem, problem_grid, constraint_grid, row, col, value, current_remaining, option = 2):
        """
        Calculates the heuristic value for a specific grid configuration.

        After assigning `value` to (row, col), lightweight domain propagation is
        performed via `propagate`. If any unassigned cell ends up with an empty
        domain the assignment is a dead end and float("inf") is returned so the
        caller can prune it immediately.

        Supported options:
            1 — number of remaining unassigned cells (Remaining Cells).
            2 — number of unsatisfied inequality constraints (Degree-style).

        Args:
            problem: The problem object carrying HorizontalConstraints /
                     VerticalConstraints.
            problem_grid (list[list]): Current grid state (values).
            constraint_grid (list[list]): Current excluded-value sets.
            row (int): Row of the cell being assigned.
            col (int): Column of the cell being assigned.
            value (int): Value being tried.
            current_remaining (int): Number of currently unassigned cells.
            option (int): Heuristic variant — 1 or 2.

        Returns:
            tuple: (row, col, value, h_value, temp_grid, temp_c_grid, remaining_cells)
                   h_value is float("inf") when the assignment leads to a dead end.
        """

        rows = len(problem_grid)
        cols = len(problem_grid[0])

        temp_grid = [r[:] for r in problem_grid]
        temp_c_grid = [[set(s) for s in r] for r in constraint_grid]

        # Assign the value to the cell
        temp_grid[row][col] = value

        remaining_cells = current_remaining - 1

        # Purning branches that violates FOL without using AC-3
        if not self.propagate(problem, temp_grid, temp_c_grid, row, col, value):
            return row, col, value, float("inf"), temp_grid, temp_c_grid, remaining_cells

        if option == 1:
            h_value = remaining_cells

        else:
            additional_steps = 0
            for r in range(rows):
                for c in range(cols):
                    if c < cols - 1 and problem.HorizontalConstraints[r][c] != 0:
                        if temp_grid[r][c] == 0 or temp_grid[r][c + 1] == 0:
                            additional_steps += 1
                    if r < rows - 1 and hasattr(problem, 'VerticalConstraints') and problem.VerticalConstraints[r][c] != 0:
                        if temp_grid[r][c] == 0 or temp_grid[r + 1][c] == 0:
                            additional_steps += 1
            h_value = additional_steps

        return row, col, value, h_value, temp_grid, temp_c_grid, remaining_cells

    def getValidMoves(self, row, col, c_grid):
        """Get all the valid moves from constraints grid"""

        n = len(c_grid)
        valid = []

        for i in range(1, n + 1):
            if i not in c_grid[row][col]:
                valid.append(i)

        return valid

    def solve(self, problem, option = 2):
        if hasattr(step_logger, 'reset'):
            step_logger.reset(problem)

        if option == 1:
            print("Running A* algorithm on Heuristic 1...")
        elif option == 2:
            print("Running A* algorithm on Heuristic 2...")
        else:
            print("Invalid heuristic option. Defaulting to Heuristic 2.")
            option = 2

        start_time = time.perf_counter()

        for r in range(problem.size):
            for c in range(problem.size):
                if problem.grid[r][c] != 0:
                    domains = step_logger.grid_to_domains(problem.grid) if hasattr(step_logger, 'grid_to_domains') else None
                    step_logger.log_step(r, c, problem.grid[r][c], tag = "given", domains = domains)

        # Declared nessesscary variable
        pq = []
        counter = 0
        closed = set()  # Closed set to avoid re-expanding the same state

        row, col, c_grid = self.constraint(problem)
        valid_moves = self.getValidMoves(row, col, c_grid)

        for v in valid_moves:
            _, _, _, h_value, temp_grid, temp_c_grid, rem = self.heuristic(problem, problem.grid, c_grid, row, col, v, self.remaining, option)
            
            # Apply pruning if violate FOL constraints
            if h_value != float("inf"): 
                g_value = 1 
                f_value = g_value + h_value 
                last_move = ((row, col), v)
                heapq.heappush(pq, (f_value, counter, g_value, temp_grid, temp_c_grid, last_move, rem))
                counter += 1

        while pq:
            f_value, _, g_value, curr_grid, curr_c_grid, last_move, curr_rem = heapq.heappop(pq)

            # Skip already-expanded states
            state_key = tuple(tuple(row) for row in curr_grid)
            if state_key in closed:
                continue
            closed.add(state_key)

            step_logger.log_step(last_move[0][0], last_move[0][1], last_move[1], tag= "deduced", domains = step_logger.grid_to_domains(curr_grid))
            
            # If there is no more cells
            # Check if is it the goal state
            if curr_rem <= 0:
                if problem.isGoalState(curr_grid):
                    end_time = time.perf_counter()
                    step_logger.execution_time = (end_time - start_time) * 1000
                    step_logger.memory_usage = sys.getsizeof(pq) / 1024

                    # print("execution_time", f"{end_time - start_time:.4f}s")
                    # print("nodes_expanded", counter)
                    # print("memory_usage", f"{sys.getsizeof(pq) / 1024:.2f} KB")
                    
                    print(f"Goal found!")
                    return curr_grid

            # Finding the next cell using MRV
            next_row, next_col = -1, -1
            highest_constraint = -1

            for r in range(len(curr_grid)):
                for c in range(len(curr_grid[0])):
                    if curr_grid[r][c] == 0: 
                        set_size = len(curr_c_grid[r][c])
                        
                        if highest_constraint < set_size:
                            highest_constraint = set_size
                            next_row, next_col = r, c

            if next_row == -1:
                continue

            valid_moves_for_next_cell = self.getValidMoves(next_row, next_col, curr_c_grid)

            # Getting all the valid moves from the cell
            for v in valid_moves_for_next_cell:
                _, _, _, h_value, next_grid, next_c_grid, next_rem = self.heuristic(problem, curr_grid, curr_c_grid, next_row, next_col, v, curr_rem, option)
                
                # Apply pruning if violate FOL constraints
                if h_value != float("inf"): 
                    new_g = g_value + 1  
                    new_f = new_g + h_value 
                    new_move = ((next_row, next_col), v) 
                    
                    heapq.heappush(pq, (new_f, counter, new_g, next_grid, next_c_grid, new_move, next_rem))
                    counter += 1

        print("Can't solve!")
        return []