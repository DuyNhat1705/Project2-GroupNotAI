from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
def main():
    algorithm = get_algorithm('astar')
    problem = Futoshiki('input-09')
    problem.printFutoshiki()
    problem.solution = algorithm.solve(problem)
    problem.writeFile()

if __name__ == "__main__":
    main()