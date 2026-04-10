from algorithms.backwardChaining import BackwardChaining
from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm

def main():
    algorithm = get_algorithm('bc')
    problem = Futoshiki('input-09')
    problem.printFutoshiki()
    if algorithm.name == "Backward Chaining":
        algorithm._start_query_console(problem)
        solution = algorithm.solve(problem)
        problem.setSolution(solution)
        algorithm._start_query_console(problem)

    else:
        solution = algorithm.solve(problem)
        problem.setSolution(solution)


    problem.writeFile()

if __name__ == "__main__":
    main()

# Val(1, 1, 5).
# Val(1, 1, X).
# Val(1, 2, Y).
# LessH(1, 1, Right).
# Val(R, C, 5).