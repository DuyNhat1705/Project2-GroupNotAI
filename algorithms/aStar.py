from algorithms.base_algorithm import BaseAlgorithm
import heapq

class AStar(BaseAlgorithm):
    def __init__(self, params = None):
        super().__init__("A*", params)
    def solve(self,problem):
        # Implement the Astar algorithm here
        print("Implementing A* algorithm...")