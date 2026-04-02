from problem.futoshiki import Futoshiki
from algorithms.algorithm_factory import get_algorithm
def main():
    algorithm = get_algorithm('astar')
    problem = Futoshiki('input-04')
    problem.printFutoshiki()
    solution = algorithm.solve(problem)

    # Kiểm tra xem thuật toán có trả về kết quả không
    if not solution:
        print("Không tìm thấy giải pháp!")
    else:
        print("\n=== KẾT QUẢ FUTOSHIKI ===")
        rows = len(solution)
        cols = len(solution[0])

        for r in range(rows):
            for c in range(cols):
                print(f"{solution[r][c]} ", end="")
            
            print()

if __name__ == "__main__":
    main()