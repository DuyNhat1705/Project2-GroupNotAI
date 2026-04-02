import os

class Futoshiki():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    def __init__(self, file):
        self.size = 0
        self.grid = []
        self.solution = None
        self.HorizontalConstraints = []
        self.VerticalConstraints = []
        self.problemNumber = file[6:]
        self.input_path = os.path.join(self.project_root, 'Inputs', f'{file}.txt')
        self.output_path = os.path.join(self.project_root, 'Outputs', f'output-{self.problemNumber}.txt')
        self.loadFromFile(self.input_path)
    def loadFromFile(self,file):
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
        if (self.solution == None):
            print("The solution is not existent")
            return
        with open(self.output_path, 'w') as f:
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