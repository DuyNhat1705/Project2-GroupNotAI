import os

class Futoshiki():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))
    def __init__(self, file):
        self.size = 0
        self.grid = []
        self.HorizontalConstraints = []
        self.VerticalConstraints = []
        self.data_path = os.path.join(self.project_root, 'Inputs', f'{file}.txt')
        self.loadFromFile(self.data_path)
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
        
    def printFutoshiki(self):
        print(f"Size: {self.size}")
        print("Grid:")
        for row in self.grid:
            print(row)
        print("Horizontal Constraints:")
        for row in self.HorizontalConstraints:
            print(row)
        print("Vertical Constraints:")
        for row in self.VerticalConstraints:
            print(row)