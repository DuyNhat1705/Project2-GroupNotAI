from algorithms.base_algorithm import BaseAlgorithm

class Backtracking(BaseAlgorithm):

    def __init__(self, params = None):
        super().__init__("Backtracking", params)
    def isValid(self, num, solution, problem, i, j, n):
        # Same num check
        for x in range(n):
            if (solution[i][x] == num) or (solution[x][j] == num):
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
                    if (i == n - 1) and (j == n - 1):
                        return True
                    if self.recursion(solution, problem, indexRow, indexCol,n):
                        return True
                    solution[i][j] = 0
            return False
        else:
            if (i == n - 1) and (j == n - 1):
                return True
            return self.recursion(solution, problem, indexRow, indexCol, n)
    def solve(self, problem):
        # Implement the backtracking algorithm here
        n = problem.size
        solution = problem.grid
        self.recursion(solution, problem, 0, 0, n)
        return solution