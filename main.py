from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
def main():
    algorithm = get_algorithm('backtracking')
    problem = Futoshiki('input-07')
    # problem.printFutoshiki()
    solution = algorithm.solve(problem)
    problem.setSolution(solution)
    problem.printFutoshikiResult()
    problem.writeFile()
if __name__ == "__main__":
    main()