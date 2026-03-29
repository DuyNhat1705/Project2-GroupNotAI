from abc import ABC, abstractmethod

class BaseAlgorithm(ABC):

    def __init__(self, name, params = None):
        """
        Args:
            name (str): Algorithm name 
            params (dict): Dictionary of hyperparameters
        """
        self.name = name
        self.params = params

    @abstractmethod
    def solve(self, problem):
        pass
    def getAlgorithmName(self):
        return self.name