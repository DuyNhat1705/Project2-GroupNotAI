from algorithms.base_algorithm import BaseAlgorithm

class ForwardChaining(BaseAlgorithm):

    def __init__(self, params = None):
        super().__init__("Forward Chaining", params)
    
    def solve(self, problem):
        # Implement the forward chaining algorithm here
        print("Implementing Forward Chaining algorithm...")