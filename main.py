from problem.futoshiki import Futoshiki
from algorithms.logic import KnowledgeBase

from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm

def main():
    algorithm = get_algorithm('backwardchaining')
    problem = Futoshiki('input-04')
    solution = algorithm.solve(problem)
    problem.setSolution(solution)
    problem.printFutoshikiResult()
    problem.writeFile()

if __name__ == "__main__":
    main()