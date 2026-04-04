from algorithms.base_algorithm import BaseAlgorithm

class BruteForce(BaseAlgorithm):
    def __init__(self, params = None):
        super().__init__("Brute Force", params)
    def isValid(self, solution, problem, n):
        # Same num check
        for i in range(n):
            rowCheck = [False] * (n+1)
            colCheck = [False] * (n+1)
            for j in range(n):
                if rowCheck[solution[i][j]]:
                    return False
                rowCheck[solution[i][j]] = True
                if colCheck[solution[j][i]]:
                    return False
                colCheck[solution[j][i]] = True
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
                if (i == n - 1) and (j == n - 1):
                    return self.isValid(solution, problem, n)
                if self.recursion(solution, problem, indexRow, indexCol, n):
                    return True
                solution[i][j] = 0
            return False
        else:
            if (i == n - 1) and (j == n - 1):
                return self.isValid(solution, problem, n)
            return self.recursion(solution, problem, indexRow, indexCol, n)
    def solve(self, problem):
        n = problem.size
        solution = problem.grid
        self.recursion(solution, problem, 0, 0, n)
        return solution