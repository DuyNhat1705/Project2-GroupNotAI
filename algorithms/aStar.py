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
                
                # Down > Up
                if relation == 1:
                    c_grid[r][c].add(max_val)
                    c_grid[r + 1][c].add(1)
                    
                    if val_bottom != 0:
                        for v in range(val_bottom, max_val + 1): 
                            c_grid[r][c].add(v)
                    if val_top != 0:
                        for v in range(1, val_top + 1): 
                            c_grid[r + 1][c].add(v)
                        
                # Down < Up
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

    def heuristic(self, problem, problem_grid, constraint_grid, row, col, value, current_remaining, option = 3):
        rows = len(problem_grid)       
        cols = len(problem_grid[0])    
        n = rows

        # Optimization: use list comprehension instead of deepcopy for speed
        temp_grid = [r[:] for r in problem_grid]
        temp_c_grid = [[set(s) for s in r] for r in constraint_grid]
        h_value = 0

        # =========================================
        # ======        Heuristic 2          ======
        # =========================================
        additional_steps = 0

        temp_grid[row][col] = value
        remaining_cells = current_remaining - 1

        for r in range(rows):
            for c in range(cols):
                # Horizontal constraints
                if c < cols - 1:
                    rel_h = problem.HorizontalConstraints[r][c]
                    if rel_h != 0: 
                        if temp_grid[r][c] == 0 or temp_grid[r][c+1] == 0:
                            additional_steps += 1
                
                # Vertical constraints
                if r < rows - 1:
                    rel_v = problem.VerticalConstraints[r][c]
                    if rel_v != 0: 
                        if temp_grid[r][c] == 0 or temp_grid[r+1][c] == 0:
                            additional_steps += 1

        # =========================================
        # ======      Heuristic 1 & 3        ======
        # =========================================
        ac3 = 0

        # Increase constraint value of the whole row
        for r in range(rows):
            temp_c_grid[r][col].add(value)

            # If after constraint propagation, is empty
            if temp_grid[r][col] == 0 and len(temp_c_grid[r][col]) == n:
                ac3 += 1

        # Increase constraint value of the whole col    
        for c in range(cols):
            temp_c_grid[row][c].add(value)

            # If after constraint propagation, is empty
            if temp_grid[row][c] == 0 and len(temp_c_grid[row][c]) == n:
                ac3 += 1

        # Constraints for left cell
        if col > 0:
            relation = problem.HorizontalConstraints[row][col - 1]
            if relation == 1:
                for v in range(value, n + 1):
                    temp_c_grid[row][col - 1].add(v)
            elif relation == -1:
                for v in range(1, value + 1): 
                    temp_c_grid[row][col - 1].add(v)

            # If after constraint propagation, is empty
            if temp_grid[row][col - 1] == 0 and len(temp_c_grid[row][col - 1]) == n: 
                ac3 += 1

        # Constraints for right cell
        if col < cols - 1:
            relation = problem.HorizontalConstraints[row][col]
            if relation == 1:
                for v in range(1, value + 1): 
                    temp_c_grid[row][col + 1].add(v)
            elif relation == -1:
                for v in range(value, n + 1): 
                    temp_c_grid[row][col + 1].add(v)

            # If after constraint propagation, is empty
            if temp_grid[row][col + 1] == 0 and len(temp_c_grid[row][col + 1]) == n: 
                ac3 += 1

        # Constraints for up cell
        if row > 0:
            relation = problem.VerticalConstraints[row - 1][col]
            if relation == 1:
                for v in range(value, n + 1): 
                    temp_c_grid[row - 1][col].add(v)
            elif relation == -1:
                for v in range(1, value + 1): 
                    temp_c_grid[row - 1][col].add(v)

            # If after constraint propagation, is empty
            if temp_grid[row - 1][col] == 0 and len(temp_c_grid[row - 1][col]) == n: 
                ac3 += 1

        # Constraints for down cell
        if row < rows - 1:
            relation = problem.VerticalConstraints[row][col]
            if relation == 1:
                for v in range(1, value + 1): 
                    temp_c_grid[row + 1][col].add(v)
            elif relation == -1:
                for v in range(value, n + 1): 
                    temp_c_grid[row + 1][col].add(v)

            # If after constraint propagation, is empty
            if temp_grid[row + 1][col] == 0 and len(temp_c_grid[row + 1][col]) == n: 
                ac3 += 1

        if option == 1:
            h_value = remaining_cells
        elif option == 2:
            h_value = additional_steps
        elif option == 3:
            h_value = ac3

        return row, col, value, h_value, temp_grid, temp_c_grid, remaining_cells        

    def getValidMoves(self, row, col, c_grid):
        n = len(c_grid)
        valid = []

        for i in range(1, n + 1):
            if i not in c_grid[row][col]:
                valid.append(i)

        return valid

    def solve(self, problem):
        # Implement the Astar algorithm here
        print("Running A* algorithm...")
        start_time = time.perf_counter()

        # Declared nessesscary variable
        pq = []
        counter = 0 

        row, col, c_grid = self.constraint(problem)
        valid_moves = self.getValidMoves(row, col, c_grid)

        for v in valid_moves:
            _, _, _, h_value, temp_grid, temp_c_grid, rem = self.heuristic(problem, problem.grid, c_grid, row, col, v, self.remaining, 3)
            
            g_value = 1 
            f_value = g_value + h_value 
            
            last_move = ((row, col), v)
            
            heapq.heappush(pq, (f_value, counter, g_value, temp_grid, temp_c_grid, last_move, rem))
            counter += 1

        while pq:
            f_value, _, g_value, curr_grid, curr_c_grid, last_move, curr_rem = heapq.heappop(pq)

            step_logger.log_step(last_move[0][0], last_move[0][1], last_move[1], tag= "deduced", domains = step_logger.grid_to_domains(curr_grid))
            # If there is no more cells
            # Check if is it the goal state
            if curr_rem == 0:
                if problem.isGoalState(curr_grid):
                    end_time = time.perf_counter()
                    step_logger.execution_time = (end_time - start_time) * 1000
                    step_logger.memory_usage = sys.getsizeof(pq) / 1024
                    '''
                    print("execution_time", f"{end_time - start_time:.4f}s")
                    print("nodes_expanded", counter)
                    print("memory_usage", f"{sys.getsizeof(pq) / 1024:.2f} KB")
                    '''
                    
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
                _, _, _, h_value, next_grid, next_c_grid, next_rem = self.heuristic(problem, curr_grid, curr_c_grid, next_row, next_col, v, curr_rem, 3)
                
                new_g = g_value + 1
                new_f = new_g + h_value
                
                new_move = ((next_row, next_col), v)
                
                heapq.heappush(pq, (new_f, counter, new_g, next_grid, next_c_grid, new_move, next_rem))
                counter += 1

        print("Can't solve!")
        return []