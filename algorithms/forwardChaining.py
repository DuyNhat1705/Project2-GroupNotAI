import time
from algorithms.base_algorithm import BaseAlgorithm
from algorithms.logic import KnowledgeBase, Atom, Imply, And, Bot
from utils.logger import step_logger


class ForwardChaining(BaseAlgorithm):

    def __init__(self, params=None):
        super().__init__("Forward Chaining", params)

    def solve(self, puzzle):
        start_time = time.perf_counter()

        kb = KnowledgeBase(puzzle)
        self._init_domains(kb)

        # A5: Given → Val
        for fact in list(kb.obs_facts):
            if hasattr(fact, 'name') and fact.name == 'Given':
                i, j, v = fact.args[0].value, fact.args[1].value, fact.args[2].value
                self._add_val(kb, i, j, v)

        result_kb = self._backtrack(kb)
        step_logger.execution_time = (time.perf_counter() - start_time) * 1000
        print(f"\nPuzzle Solved in {step_logger.execution_time:.2f}ms!\n")
        if result_kb is None:
            return None
        return self._get_result_grid(result_kb)
    
    def _init_domains(self, kb):
        kb.domains = {}
        for i in range(1, kb.riddle.size + 1):
            for j in range(1, kb.riddle.size + 1):
                v = kb.riddle.grid[i-1][j-1]
                kb.domains[(i, j)] = {v} if v != 0 else set(range(1, kb.riddle.size + 1))

    def _add_val(self, kb, i, j, v):
        fact = Atom('Val', i, j, v)
        if fact not in kb.obs_facts:
            kb.tell(fact)
        kb.domains[(i, j)] = {v}

    def _clone(self, kb):
        new_kb = KnowledgeBase.__new__(KnowledgeBase)
        new_kb.riddle = kb.riddle
        new_kb.obs_facts = list(kb.obs_facts)
        new_kb.domains = {k: set(v) for k, v in kb.domains.items()}
        new_kb.ground_rules = kb.ground_rules  # Share static rules
        return new_kb

    def _get_result_grid(self, kb):
        n = kb.riddle.size
        grid = [[0]*n for _ in range(n)]
        for (i, j), d in kb.domains.items():
            if len(d) == 1:
                grid[i-1][j-1] = next(iter(d))
        return grid

    # ------------------------------------------------------------------
    # Forward Chaining (propagation)
    # ------------------------------------------------------------------

    def _propagate(self, kb):
        changed = True
        while changed:
            changed = False

            # For each Val(i,j,v) — eliminate v from same row and column
            val_facts = [f for f in kb.obs_facts if hasattr(f, 'name') and f.name == 'Val']
            for fact in val_facts:
                i, j, v = fact.args[0].value, fact.args[1].value, fact.args[2].value

                for j2 in range(1, kb.riddle.size + 1):
                    if j2 != j and v in kb.domains[(i, j2)]:
                        kb.domains[(i, j2)].discard(v)
                        changed = True

                for i2 in range(1, kb.riddle.size + 1):
                    if i2 != i and v in kb.domains[(i2, j)]:
                        kb.domains[(i2, j)].discard(v)
                        changed = True

            # Inequality constraints
            for fact in kb.obs_facts:
                if not hasattr(fact, 'name'):
                    continue
                if fact.name == 'LessH':
                    i, j = fact.args[0].value, fact.args[1].value
                    changed |= self._apply_less(kb, (i, j), (i, j + 1))
                elif fact.name == 'GreaterH':
                    i, j = fact.args[0].value, fact.args[1].value
                    changed |= self._apply_less(kb, (i, j + 1), (i, j))
                elif fact.name == 'LessV':
                    i, j = fact.args[0].value, fact.args[1].value
                    changed |= self._apply_less(kb, (i, j), (i + 1, j))
                elif fact.name == 'GreaterV':
                    i, j = fact.args[0].value, fact.args[1].value
                    changed |= self._apply_less(kb, (i + 1, j), (i, j))

            # A1: domain size == 1 → add Val fact
            for i in range(1, kb.riddle.size + 1):
                for j in range(1, kb.riddle.size + 1):
                    d = kb.domains[(i, j)]
                    if len(d) == 1:
                        v = next(iter(d))
                        if Atom('Val', i, j, v) not in kb.obs_facts:
                            self._add_val(kb, i, j, v)
                            changed = True
                            step_logger.log_step(i, j, v, tag='deduced',domains=dict(kb.domains),facts_count=len(kb.obs_facts))

            # Rebuild val_set after A1 before checking ground rules
            val_set = {f for f in kb.obs_facts if hasattr(f, 'name') and f.name == 'Val'}

            # Check ground rules for contradiction
            if self._check_ground_rules(kb, val_set):
                return False

            # Contradiction: empty domain in some cell
            if any(len(d) == 0 for d in kb.domains.values()):
                return False

        return True

    def _apply_less(self, kb, cell_a, cell_b):
        da, db = kb.domains[cell_a], kb.domains[cell_b]
        if not da or not db:
            return False
        new_da = {x for x in da if x < max(db)}
        new_db = {x for x in db if x > min(da)}
        changed = (new_da != da) or (new_db != db)
        kb.domains[cell_a] = new_da
        kb.domains[cell_b] = new_db
        return changed

    def _check_ground_rules(self, kb, val_set):
        for rule in kb.ground_rules:
            if not isinstance(rule, Imply):
                continue

            premise = rule.left
            conclusion = rule.right

            # Collect atoms in premise
            if isinstance(premise, And):
                atoms = premise.args
            else:
                atoms = [premise]

            # Check if all atoms in premise are proven Val facts
            if all(a in val_set for a in atoms):
                if isinstance(conclusion, Bot):
                    return True  # Contradiction found

        return False

    # ------------------------------------------------------------------
    # Backtracking
    # ------------------------------------------------------------------

    def _backtrack(self, kb):
        if not self._propagate(kb):
            return None

        # Check if solved
        if all(len(d) == 1 for d in kb.domains.values()):
            return kb

        # Select unassigned cell with MRV (Minimum Remaining Values)
        cell = None
        min_domain_size = float('inf')
        for i in range(1, kb.riddle.size + 1):
            for j in range(1, kb.riddle.size + 1):
                domain_size = len(kb.domains[(i, j)])
                if 1 < domain_size < min_domain_size:
                    cell = (i, j)
                    min_domain_size = domain_size

        if cell is None:
            return None

        i, j = cell
        for v in sorted(kb.domains[(i, j)]):
            kb_copy = self._clone(kb)
            self._add_val(kb_copy, i, j, v)
            step_logger.log_step(i, j, v, tag='try',domains=dict(kb_copy.domains),facts_count=len(kb_copy.obs_facts))

            result = self._backtrack(kb_copy)
            if result is not None:
                return result

            step_logger.log_step(i, j, 0, tag='backtrack',domains=dict(kb.domains),facts_count=len(kb.obs_facts))

        return None