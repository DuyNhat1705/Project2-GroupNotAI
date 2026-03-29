from algorithms.aStar import AStar
from algorithms.backTracking import Backtracking
from algorithms.forwardChaining import ForwardChaining
from algorithms.backwardChaining import BackwardChaining

def get_algorithm(name):
    algoDict = {
        "astar": AStar,
        "a*": AStar,
        
        "forwardchaining": ForwardChaining,
        "fc": ForwardChaining,

        "backwardchaining": BackwardChaining,
        "bc": BackwardChaining,

        "backtracking": Backtracking,
        "bt": Backtracking
    }
    if name not in algoDict:
        raise ValueError(f"Algorithm '{name}' not found. Available: {list(algoDict.keys())}")
    
    AlgoClass = algoDict[name]
    return AlgoClass()