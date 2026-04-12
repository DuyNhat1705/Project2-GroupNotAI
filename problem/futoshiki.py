import os

class Futoshiki():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    output_dir = os.path.join(project_root, 'Outputs')
    os.makedirs(output_dir, exist_ok=True)
    def __init__(self, file):
        self.size = 0
        self.grid = []
        self.solution = None
        self.HorizontalConstraints = []
        self.VerticalConstraints = []
        self.problemNumber = file[6:]
        self.input_path = os.path.join(self.project_root, 'Inputs', f'{file}.txt')
        self.output_path = os.path.join(self.output_dir, f'output-{self.problemNumber}.txt')
        self.loadFromFile(self.input_path)
        
    def loadFromFile(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()

            data = []
            for line in lines:
                line = line.strip()
                if line == "" or line.startswith("#"):
                    continue
                data.append(line)

            # Read size of futoshiki grid n
            idx = 0
            self.size = int(data[idx])
            idx += 1

            # Read futoshiki grid (n x n)
            self.grid = []
            for _ in range(self.size):
                row = list(map(int, data[idx].split(',')))
                self.grid.append(row)
                idx += 1

            # Read horizontal constraints (n x (n-1))
            self.HorizontalConstraints = []
            for _ in range(self.size):
                row = list(map(int, data[idx].split(',')))
                self.HorizontalConstraints.append(row)
                idx += 1

            # Read vertical constraints ((n-1) x n)
            self.VerticalConstraints = []
            for _ in range(self.size - 1):
                row = list(map(int, data[idx].split(',')))
                self.VerticalConstraints.append(row)
                idx += 1
                
    def setSolution(self, solution):
        self.solution = solution

    def writeFile(self):
        if not self.solution:
            print("The solution is not existent")
            return
        
        with open(self.output_path, 'w', encoding = "utf-8") as f:
            for i in range(self.size):
                for j in range(self.size):
                    print(self.solution[i][j], end = ' ', file = f)
                    if (j < self.size - 1):
                        if (self.HorizontalConstraints[i][j] == 1):
                            print("<", end = ' ', file = f)
                        elif (self.HorizontalConstraints[i][j] == -1):
                            print(">", end = ' ', file = f)
                        else:
                            print(" ", end = ' ', file = f)
                print(file = f)
                if(i < self.size - 1):
                    for j in range(self.size):
                        if(self.VerticalConstraints[i][j] == 1):
                            print("∧", end = "   ", file = f)
                        elif (self.VerticalConstraints[i][j] == -1):
                            print("V", end = "   ", file = f)
                        else:
                            print(" ", end = "   ", file = f)
                    print(file = f)

        print(f"The solution of input-{self.problemNumber} has been written to {self.output_path}")
        
    def isGoalState(self, grid = None):
        grid_to_check = grid if grid is not None else self.grid

        rows = len(grid_to_check)
        cols = len(grid_to_check[0])
        n = self.size

        for r in range(rows):    
            row_seen = set()
            col_seen = set()
            for c in range(cols):                
                if grid_to_check[r][c] == 0:
                    return False
                
                # Check Row and Colum duplication
                row_seen.add(grid_to_check[r][c])
                col_seen.add(grid_to_check[c][r])

                # Check Horizontal constraints
                if c < n - 1:
                    h_constraint = self.HorizontalConstraints[r][c]
                    left_value = grid_to_check[r][c]
                    right_value = grid_to_check[r][c + 1] 

                    if h_constraint == -1:    # Left > Right
                        if (left_value <= right_value): return False
                    elif h_constraint == 1:   # Left < Right
                        if (left_value >= right_value): return False

                # Check Vertical constraints
                if r < n - 1:
                    v_constraint = self.VerticalConstraints[r][c] 
                    up_value = grid_to_check[r][c]
                    down_value = grid_to_check[r + 1][c] 

                    if v_constraint == -1:    # Up > Down
                        if (up_value <= down_value): return False
                    elif v_constraint == 1:   # Up < Down
                        if (up_value >= down_value): return False

            # If there are not enough n unquie numbers => Duplicate
            if len(row_seen) != n or len(col_seen) != n:
                return False

        return True

    def printFutoshiki(self):
        print(f"Size: {self.size}")
        print("Grid:")

        for i in range(self.size):
            for j in range(self.size):
                print(self.grid[i][j], end = ' ')
                if (j < self.size - 1):
                    if (self.HorizontalConstraints[i][j] == 1):
                        print("<", end = ' ')
                    elif (self.HorizontalConstraints[i][j] == -1):
                        print(">", end = ' ')
                    else:
                        print(" ", end = ' ')

            print()

            if(i < self.size - 1):
                for j in range(self.size):
                    if(self.VerticalConstraints[i][j] == 1):
                        print("∧", end = "   ")
                    elif (self.VerticalConstraints[i][j] == -1):
                        print("V", end = "   ")
                    else:
                        print(" ", end = "   ")
                print()

    def printFutoshikiResult(self):
        if not self.solution:
            print("The solution is not existent")
            return

        for i in range(self.size):
            for j in range(self.size):
                print(self.solution[i][j], end = ' ')
                if (j < self.size - 1):
                    if (self.HorizontalConstraints[i][j] == 1):
                        print("<", end = ' ')
                    elif (self.HorizontalConstraints[i][j] == -1):
                        print(">", end = ' ')
                    else:
                        print(" ", end = ' ')
            print()
            if(i < self.size - 1):
                for j in range(self.size):
                    if(self.VerticalConstraints[i][j] == 1):
                        print("∧", end = "   ")
                    elif (self.VerticalConstraints[i][j] == -1):
                        print("V", end = "   ")
                    else:
                        print(" ", end = "   ")
                print()