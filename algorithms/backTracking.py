import time
from algorithms.base_algorithm import BaseAlgorithm
from utils.logger import step_logger
import sys
class Backtracking(BaseAlgorithm):

    def __init__(self, params = None):
        super().__init__("Backtracking", params)
        self.row_mask = None
        self.col_mask = None
    def isValid(self, num, solution, problem, i, j, n):
        # Same num check
        if (self.row_mask[i] & (1 << num)) or (self.col_mask[j] & (1 << num)):
            return False
        # Constraint Check
        if (j < n - 1) and (solution[i][j + 1] != 0):
            if(problem.HorizontalConstraints[i][j] == 1) and (num > solution[i][j + 1]):
                return False
            elif(problem.HorizontalConstraints[i][j] == -1) and (num < solution[i][j + 1]):
                return False
        if (j > 0) and (solution[i][j - 1] != 0):
            if (problem.HorizontalConstraints[i][j - 1] == 1) and (num < solution[i][j - 1]):
                return False
            elif (problem.HorizontalConstraints[i][j - 1] == -1) and (num > solution[i][j - 1]):
                return False
        if (i < n - 1) and (solution[i + 1][j] != 0):
            if (problem.VerticalConstraints[i][j] == 1) and (num > solution[i + 1][j]):
                return False
            elif (problem.VerticalConstraints[i][j] == -1) and (num < solution[i + 1][j]):
                return False
        if (i > 0) and (solution[i - 1][j] != 0):
            if (problem.VerticalConstraints[i - 1][j] == 1) and (num < solution[i - 1][j]):
                return False
            elif (problem.VerticalConstraints[i - 1][j] == -1) and (num > solution[i - 1][j]):
                return False
        return True
    def recursion(self, solution, problem, i, j, n):
        indexCol = (j + 1)%n
        indexRow = i + (j + 1)//n
        if solution[i][j] == 0:
            for num in range(1, n + 1):
                if self.isValid(num, solution, problem, i, j, n):
                    solution[i][j] = num
                    self.row_mask[i] |= (1 << num)
                    self.col_mask[j] |= (1 << num)
                    step_logger.log_step(i, j, num, tag = "deduced",domains = step_logger.grid_to_domains(solution))
                    if (i == n - 1) and (j == n - 1):
                        return True
                    if self.recursion(solution, problem, indexRow, indexCol, n):
                        return True
                    self.row_mask[i] &= ~(1 << num)
                    self.col_mask[j] &= ~(1 << num)
                    solution[i][j] = 0
                    step_logger.log_step(i, j, 0, tag = 'backtrack', domains = step_logger.grid_to_domains(solution))
            return False
        else:
            if (i == n - 1) and (j == n - 1):
                return True
            return self.recursion(solution, problem, indexRow, indexCol, n)
        
    def solve(self, problem):
        if hasattr(step_logger, 'reset'):
                    step_logger.reset(problem)

        n = problem.size
        solution = problem.grid
        self.row_mask = [0] * n
        self.col_mask = [0] * n

        for i in range(n):
            for j in range(n):
                if solution[i][j] != 0:
                    num = solution[i][j]
                    self.row_mask[i] |= (1 << num)
                    self.col_mask[j] |= (1 << num)
                    
                    domains = step_logger.grid_to_domains(solution) if hasattr(step_logger, 'grid_to_domains') else None
                    step_logger.log_step(i, j, num, tag = "given", domains = domains)

        start_time = time.perf_counter()
        self.recursion(solution, problem, 0, 0, n)
        end_time = time.perf_counter()
        step_logger.execution_time = (end_time - start_time) * 1000
        step_logger.memory_usage = sys.getsizeof(solution) + sys.getsizeof(self.row_mask) + sys.getsizeof(self.col_mask)
        return solution