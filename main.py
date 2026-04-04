from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
def main():
    algorithm = get_algorithm('astar')
    problem = Futoshiki('input-03')
    # problem.printFutoshiki()
    solution = algorithm.solve(problem)
    problem.setSolution(solution)
    problem.printFutoshikiResult()
    problem.writeFile()
if __name__ == "__main__":
    main()