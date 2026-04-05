import time

# Usage:
'''
logger = Logger(algo_name)
logger.history["steps"] = []
'''

class Logger:
    def __init__(self):
        self.execution_time = 0.0 # in ms (miliseconds)
        self.memory_usage = 0.0 # in MB (MegaBytes)

        self.steps = []
        self._given_cells = set()
        self._n = 0
    def reset(self, puzzle):
        """Gọi trước mỗi lần solve để xóa state cũ."""
        self.steps = []
        self._n = puzzle.size
        self.execution_time = 0.0
        self.memory_usage = 0.0
        self._given_cells = {
            (i + 1, j + 1)
            for i in range(puzzle.size)
            for j in range(puzzle.size)
            if puzzle.grid[i][j] != 0
        }
    def log_step(self, i, j, v, tag = None, domains = None, facts_count = -0):

        if self._n == 0:
            return
        if tag is None:
            already = any(s['cell'] == (i, j) for s in self.steps)
            if (i, j) in self._given_cells and not already:
                tag = 'given'
            elif already:
                tag = 'backtrack'
            else:
                tag = 'deduced'

        self.steps.append({
            'step_num'         : len(self.steps) + 1,
            'action'           : f"({i}, {j})  \u2190  {v}",
            'tag'              : tag,
            'cell'             : (i, j),
            'value'            : v,
            'domains_snapshot' : domains if domains is not None else {},
            'facts_count'      : facts_count,
        })
    def grid_to_domains(self, grid) -> dict:

        n = self._n or len(grid)
        domains = {}
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                v = grid[i - 1][j - 1]
                domains[(i, j)] = frozenset({v}) if v != 0 else frozenset(range(1, n + 1))
        return domains
        
    def finish(self):
        self.execution_time = (time.perf_counter() - self.start_time) * 1000

step_logger = Logger()