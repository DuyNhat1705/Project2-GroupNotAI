from problem.futoshiki import Futoshiki
from algorithms.logic import KnowledgeBase

from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
def main():
    # algorithm = get_algorithm('astar')
    problem = Futoshiki('input-02')
    problem.printFutoshiki()
    # solution = algorithm.solve(problem)
if __name__ == "__main__":
    main()