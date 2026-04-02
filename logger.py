import time

# Usage:
'''
logger = Logger(algo_name)
logger.history["steps"] = []
'''

class Logger:
    def __init__(self, algo_name):
        self.algo_name = algo_name
        
        self.history = {} 

    def log(self, key, value):
        """
        Agrs:
            key (str):  what to log
            value(...): elements of corresponding 'key' list
        """
        if key not in self.history: # Auto-creates if not exist.
            self.history[key] = [] # new empty list at 'key'
        self.history[key].append(value) # Appends 'value' to the list at 'key'