from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm

def main():
    algorithm = get_algorithm('bc')
    problem = Futoshiki('input-01')
    problem.printFutoshiki()

    if algorithm.name == "Backward Chaining":
        algorithm._start_query_console(problem)
        solution = algorithm.solve(problem)
        algorithm._start_query_console(problem)

    elif algorithm.name == "A*" :
        solution = algorithm.solve(problem, 2)
    else:
        solution = algorithm.solve(problem)

    problem.setSolution(solution)
    problem.printFutoshikiResult()
    problem.writeFile()

if __name__ == "__main__":
    main()