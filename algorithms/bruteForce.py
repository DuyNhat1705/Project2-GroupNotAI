from algorithms.base_algorithm import BaseAlgorithm
from utils.logger import step_logger
import time
import sys

class BruteForce(BaseAlgorithm):
    def __init__(self, params = None):
        super().__init__("Brute Force", params)

    def isValid(self, solution, problem, n):
        # Same num check
        row_masks = [0] * n
        col_masks = [0] * n
        
        for i in range(n):
            for j in range(n):
                num = solution[i][j]
                if (row_masks[i] & (1 << num)) or (col_masks[j] & (1 << num)):
                    return False
                row_masks[i] |= (1 << num)
                col_masks[j] |= (1 << num)

        # Constraint Check
        for i in range(n):
            for j in range(n):
                if (j < n - 1) and (solution[i][j + 1] != 0):
                    if(problem.HorizontalConstraints[i][j] == 1) and (solution[i][j] > solution[i][j + 1]):
                        return False
                    elif(problem.HorizontalConstraints[i][j] == -1) and (solution[i][j] < solution[i][j + 1]):
                        return False
                if (j > 0) and (solution[i][j - 1] != 0):
                    if (problem.HorizontalConstraints[i][j - 1] == 1) and (solution[i][j] < solution[i][j - 1]):
                        return False
                    elif (problem.HorizontalConstraints[i][j - 1] == -1) and (solution[i][j] > solution[i][j - 1]):
                        return False
                if (i < n - 1) and (solution[i + 1][j] != 0):
                    if (problem.VerticalConstraints[i][j] == 1) and (solution[i][j] > solution[i + 1][j]):
                        return False
                    elif (problem.VerticalConstraints[i][j] == -1) and (solution[i][j] < solution[i + 1][j]):
                        return False
                if (i > 0) and (solution[i - 1][j] != 0):
                    if (problem.VerticalConstraints[i - 1][j] == 1) and (solution[i][j] < solution[i - 1][j]):
                        return False
                    elif (problem.VerticalConstraints[i - 1][j] == -1) and (solution[i][j] > solution[i - 1][j]):
                        return False
        return True
        

    def recursion(self, solution, problem, i, j, n):
        indexCol = (j + 1)%n
        indexRow = i + (j + 1)//n
        if solution[i][j] == 0:
            for num in range(1, n + 1):
                solution[i][j] = num
                step_logger.log_step(i, j, num, tag = "deduced", domains = step_logger.grid_to_domains(solution))
                if (i == n - 1) and (j == n - 1):
                    return self.isValid(solution, problem, n)
                if self.recursion(solution, problem, indexRow, indexCol, n):
                    return True
                solution[i][j] = 0
                step_logger.log_step(i, j, 0, tag = "backtrack", domains = step_logger.grid_to_domains(solution))
            return False
        else:
            if (i == n - 1) and (j == n - 1):
                return self.isValid(solution, problem, n)
            return self.recursion(solution, problem, indexRow, indexCol, n)
        
    def solve(self, problem):
        n = problem.size
        solution = problem.grid
        start_time = time.perf_counter()
        self.recursion(solution, problem, 0, 0, n)
        end_time = time.perf_counter()
        step_logger.execution_time = (end_time - start_time) * 1000
        step_logger.memory_usage = sys.getsizeof(solution)
        return solution