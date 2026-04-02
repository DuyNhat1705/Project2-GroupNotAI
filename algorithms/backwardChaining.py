from algorithms.base_algorithm import BaseAlgorithm

class BackwardChaining(BaseAlgorithm):

    def __init__(self, params = None):
        super().__init__("Backward Chaining", params)

    def solve(self, problem):
        # Implement the backward chaining algorithm here
        print("Implementing Backward Chaining algorithm...")