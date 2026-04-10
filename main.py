
from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm

def main():
    algorithm = get_algorithm('astar')
    problem = Futoshiki('input-07')
    solution = algorithm.solve(problem)
    problem.setSolution(solution)

    problem.writeFile()
    if algorithm.name == "Backward Chaining":
        algorithm._start_query_console()

if __name__ == "__main__":
    main()