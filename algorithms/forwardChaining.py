from algorithms.base_algorithm import BaseAlgorithm
from algorithms.groundKB import KnowledgeBase


class ForwardChaining(BaseAlgorithm):

    def __init__(self, params=None):
        super().__init__("Forward Chaining", params)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def solve(self, puzzle):
        kb = KnowledgeBase(puzzle)

        # Apply A5: Given → Val  (obs_facts already has Given atoms from _init_facts)
        for fact in list(kb.obs_facts):
            if isinstance(fact, object) and hasattr(fact, 'name') and fact.name == 'Given':
                i = fact.args[0].value
                j = fact.args[1].value
                v = fact.args[2].value
                kb.add_val(i, j, v)

        # Run FC + backtracking
        result_kb = self._backtrack(kb)
        if result_kb is None:
            return None  # no solution found

        return result_kb.get_result_grid()

    # ------------------------------------------------------------------
    # Pure Forward Chaining (propagation)
    # ------------------------------------------------------------------

    def _propagate(self, kb):
        changed = True
        while changed:
            changed = False

            # --- Apply known Val facts ---
            for fact in list(kb.obs_facts):
                if not (hasattr(fact, 'name') and fact.name == 'Val'):
                    continue
                i = fact.args[0].value
                j = fact.args[1].value
                v = fact.args[2].value

                # A2: narrow domain (i,j) to {v}
                if kb.domains[(i, j)] != {v}:
                    kb.domains[(i, j)] = {v}
                    changed = True

                # A3: Row uniqueness — exclude v from domain cells in same row
                for j2 in range(1, kb.size + 1):
                    if j2 != j and v in kb.domains[(i, j2)]:
                        kb.domains[(i, j2)].discard(v)
                        changed = True

                # A6: Column uniqueness — exclude v from domain cells in same column
                for i2 in range(1, kb.size + 1):
                    if i2 != i and v in kb.domains[(i2, j)]:
                        kb.domains[(i2, j)].discard(v)
                        changed = True

            # --- Apply inequality constraints ---
            for fact in list(kb.obs_facts):
                if not hasattr(fact, 'name'):
                    continue

                if fact.name == 'LessH':
                    # cell(i,j) < cell(i,j+1)
                    i = fact.args[0].value
                    j = fact.args[1].value
                    changed |= self._apply_less(kb, (i, j), (i, j + 1))

                elif fact.name == 'GreaterH':
                    # cell(i,j) > cell(i,j+1)  ≡  cell(i,j+1) < cell(i,j)
                    i = fact.args[0].value
                    j = fact.args[1].value
                    changed |= self._apply_less(kb, (i, j + 1), (i, j))

                elif fact.name == 'LessV':
                    # cell(i,j) < cell(i+1,j)
                    i = fact.args[0].value
                    j = fact.args[1].value
                    changed |= self._apply_less(kb, (i, j), (i + 1, j))

                elif fact.name == 'GreaterV':
                    # cell(i,j) > cell(i+1,j)  ≡  cell(i+1,j) < cell(i,j)
                    i = fact.args[0].value
                    j = fact.args[1].value
                    changed |= self._apply_less(kb, (i + 1, j), (i, j))

            # --- A1: domain has 1 value → add Val fact ---
            for i in range(1, kb.size + 1):
                for j in range(1, kb.size + 1):
                    d = kb.domains[(i, j)]
                    if len(d) == 1:
                        v = next(iter(d))
                        if not kb.has_val(i, j, v):
                            kb.add_val(i, j, v)
                            changed = True

            # Early contradiction check
            if kb.is_contradiction():
                return False

        return True

    def _apply_less(self, kb, cell_a, cell_b):
        da = kb.domains[cell_a]
        db = kb.domains[cell_b]

        if not da or not db:
            return False

        # cell_a < cell_b: a < max(b), b > min(a)
        new_da = {x for x in da if x < max(db)}
        new_db = {x for x in db if x > min(da)}

        changed = (new_da != da) or (new_db != db)
        kb.domains[cell_a] = new_da
        kb.domains[cell_b] = new_db
        return changed

    # ------------------------------------------------------------------
    # Backtracking (used when FC alone is not sufficient to solve completely)
    # ------------------------------------------------------------------

    def _backtrack(self, kb):
        # Step 1: propagate
        if not self._propagate(kb):
            return None  # contradiction

        # Step 2: check if solved
        if kb.is_solved():
            return kb

        # Step 3: select unassigned cell with smallest domain (MRV)
        cell = self._select_unassigned(kb)
        if cell is None:
            return None

        i, j = cell

        # Step 4: try each value in domain
        for v in sorted(kb.domains[(i, j)]):
            kb_copy = kb.clone()
            kb_copy.add_val(i, j, v)

            result = self._backtrack(kb_copy)
            if result is not None:
                return result

        return None  # no valid value found

    def _select_unassigned(self, kb):
        best = None
        best_size = float('inf')
        for i in range(1, kb.size + 1):
            for j in range(1, kb.size + 1):
                d = kb.domains[(i, j)]
                if len(d) > 1 and len(d) < best_size:
                    best = (i, j)
                    best_size = len(d)
        return best