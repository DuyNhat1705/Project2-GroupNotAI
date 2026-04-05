from algorithms.base_algorithm import BaseAlgorithm
from algorithms.logic import Var, Const, Atom, And, Imply, Unify, Substitute, KnowledgeBase
from logger import Logger

class BackwardChaining(BaseAlgorithm):

    def __init__(self, params = None):
        self.kb = None
        self.cnt = 0 # later assigned idx
        self.logger = Logger("Backward Chaining")  # Initialize logger
        super().__init__("Backward Chaining", params)

    def solve(self, problem):
        self.kb = KnowledgeBase(problem)
        self.logger.log("system", "Knowledge Base initialized.")
        print(f"Backward chaining for {problem.size}x{problem.size}...\n")

        # initial scratchpad
        domains = self.init_domain(problem)

        # recursive search
        if self.backtrack_solve(problem, domains):
            print("\nPuzzle Solved!")
            problem.printFutoshiki()
            return True
        else:
            print("\nFAILED: The engine could not find a valid solution.")
            return False

    def backtrack_solve(self, problem, domains):
        # get the MRV cell
        cell = self.get_mrv_cell(domains)

        if cell is None:
            return True  # Board solved

        row, col = cell

        # Ask FOL Engine for candidates
        query = Atom('Val', row + 1, col + 1, Var('$v'))
        answers = list(self.fol_bc_ask(query))

        unique_vals = set()

        for theta in answers:
            raw_val_expr = Substitute(theta, Var('$v'))
            val = self.unpack_val(raw_val_expr)

            # Only try value if it is in valid domain
            if val in domains[(row, col)] and val not in unique_vals:
                unique_vals.add(val)  # Mark as seen!

                if self.is_safe(problem, row, col, val):
                    # Try placing and Forward Check
                    is_valid, pruned_list = self.forward_check(problem, domains, row, col, val)

                    if is_valid:
                        # if safe, commit to the board
                        problem.grid[row][col] = val
                        fact = Atom('Given', row + 1, col + 1, val)
                        self.kb.obs_facts.append(fact)

                        # Temporarily remove this cell from the domains
                        saved_domain = domains.pop((row, col))

                        # Move forward
                        if self.backtrack_solve(problem, domains):
                            return True

                        # Restore to the domains dict
                        domains[(row, col)] = saved_domain
                        problem.grid[row][col] = 0
                        self.kb.obs_facts.remove(fact)

                    # Backtrack clean: Put back num we removed from domains
                    for (pr, pc, pv) in pruned_list:
                        domains[(pr, pc)].add(pv)
        return False

    def init_domain(self, problem):
        """
        Every empty cell gets a set of all possible values
        """
        domains = {}
        for r in range(problem.size):
            for c in range(problem.size):
                if problem.grid[r][c] == 0:
                    domains[(r, c)] = set(range(1, problem.size + 1))
        return domains

    # --- Helper functions ---
    def unpack_val(self, val):
        """Unpack the raw integer from a logical Constant."""
        if isinstance(val, Const):
            return val.value
        elif isinstance(val, str):
            return int(val)
        return val

    def stdize_var(self, rule):
        """
        Assign unique indices to vars
        E.g. Val('$i', '$j', '$v') -> Val('$i_1', '$j_1', '$v_1')
        """
        self.cnt += 1
        suffix = f"_{self.cnt}"

        def rename(expr):
            if isinstance(expr, Var):
                return Var(f"{expr.name}{suffix}")
            elif isinstance(expr, Atom):
                return Atom(expr.name, *[rename(arg) for arg in expr.args])
            elif isinstance(expr, And):
                return And(*[rename(arg) for arg in expr.args])
            elif isinstance(expr, Imply):
                return Imply(rename(expr.left), rename(expr.right))
            return expr

        return rename(rule)

    # --- Inference engine ---

    def fol_bc_ask(self, query):
        return self.fol_bc_or(query, {})

    def fol_bc_or(self, goal, theta, path=None):
        if path is None:
            path = []

        # Ground the goal with current bindings
        ground_goal = Substitute(theta, goal)

        # cycle detection
        for p in path:
            # If current goal unifies with a goal already in path -> Prune the branch
            if Unify(p, ground_goal, {}) is not None:
                return

        # Add the current goal to the path
        new_path = path + [ground_goal]

        # check observed facts
        for fact in self.kb.obs_facts:
            new_theta = Unify(fact, goal, theta)
            if new_theta is not None:
                yield new_theta

        # check rules (Horn clauses)
        for rule in self.kb.horn_rules:
            rule = self.stdize_var(rule)

            # Unify the goal with conclusion
            theta_prime = Unify(rule.right, goal, theta)

            if theta_prime is not None:
                # prepare the premises  as a list
                if isinstance(rule.left, And):
                    premises = rule.left.args
                else:
                    premises = [rule.left]  # single Atom

                # Pass the new_path down to avoid cycles
                for phi in self.fol_bc_and(premises, theta_prime, new_path):
                    yield phi

    def fol_bc_and(self, goals, theta, path):
        if theta is None:
            return
        if not goals:  # Base case: list empty, all premises proven
            yield theta
        else:
            first_goal = goals[0]
            rest_goals = goals[1:]

            # Prove the first goal (pass the path forward)
            for theta_prime in self.fol_bc_or(Substitute(theta, first_goal), theta, path):
                # if successful, recursively prove the rest
                for phi in self.fol_bc_and(rest_goals, theta_prime, path):
                    yield phi

    def is_safe(self, problem, row, col, val):
        """Checks if placing 'val' at (row, col) violates any rules, with strict type casting."""

        # cast grid val to int
        def get_val(r, c):
            return int(problem.grid[r][c]) if problem.grid[r][c] != 0 else 0

        # handle both integer and string constraints
        def get_sign(sign):
            if sign in [1, '<', '^']: return 1
            if sign in [-1, '>', 'v', 'V']: return -1
            return 0

        # Row and Column uniqueness & cast to int
        for x in range(problem.size):
            if get_val(row, x) == val: return False
            if get_val(x, col) == val: return False

        # Horizontal constraints
        # Check left
        if col > 0 and problem.HorizontalConstraints[row][col - 1] != 0:
            left_val = get_val(row, col - 1)
            sign = get_sign(problem.HorizontalConstraints[row][col - 1])
            if left_val != 0:
                if sign == 1 and not (left_val < val): return False
                if sign == -1 and not (left_val > val): return False

        # Check right
        if col < problem.size - 1 and problem.HorizontalConstraints[row][col] != 0:
            right_val = get_val(row, col + 1)
            sign = get_sign(problem.HorizontalConstraints[row][col])
            if right_val != 0:
                if sign == 1 and not (val < right_val): return False
                if sign == -1 and not (val > right_val): return False

        # Vertical constraints
        # Check up
        if row > 0 and problem.VerticalConstraints[row - 1][col] != 0:
            top_val = get_val(row - 1, col)
            sign = get_sign(problem.VerticalConstraints[row - 1][col])

            if top_val != 0:
                if sign == 1 and not (top_val < val):
                    return False
                if sign == -1 and not (top_val > val):
                    return False

        # Check low
        if row < problem.size - 1 and problem.VerticalConstraints[row][col] != 0:
            bottom_val = get_val(row + 1, col)
            sign = get_sign(problem.VerticalConstraints[row][col])
            if bottom_val != 0:
                if sign == 1 and not (val < bottom_val): return False
                if sign == -1 and not (val > bottom_val): return False

        return True  # Survived the strict checks!

    def forward_check(self, problem, domains, row, col, val):
        """
        Applies val at (row, col) and shrink the domains of its peers
        returns bool & list of tuples: (peer_row, peer_col, deleted_val)
        """
        pruned = [] # save the pruned val for later undo

        def get_sign(sign):
            if sign in [1, '<', '^']: return 1
            if sign in [-1, '>', 'v', 'V']: return -1
            return 0

        # remove a value from a peer's domain
        def prune(r, c, v):
            if (r, c) in domains and v in domains[(r, c)]:
                domains[(r, c)].remove(v)
                pruned.append((r, c, v))
                # If domain gets dead end => return False
                if len(domains[(r, c)]) == 0:
                    return False
            return True

        # Row & Column Checking
        for x in range(problem.size):
            if x != col and not prune(row, x, val): # dead end encountered
                return False, pruned
            if x != row and not prune(x, col, val):
                return False, pruned

        # Horizontal constraints
        # Check Right (col + 1)
        if col < problem.size - 1 and problem.HorizontalConstraints[row][col] != 0:
            sign = get_sign(problem.HorizontalConstraints[row][col])

            if sign == 1:  # Left < Right
                for v in range(1, val + 1):
                    if not prune(row, col + 1, v):
                        return False, pruned

            elif sign == -1:  # Left > Right
                for v in range(val, problem.size + 1):
                    if not prune(row, col + 1, v):
                        return False, pruned

        # Check Left (col - 1)
        if col > 0 and problem.HorizontalConstraints[row][col - 1] != 0:
            sign = get_sign(problem.HorizontalConstraints[row][col - 1])

            if sign == 1:  # Left < Right
                for v in range(val, problem.size + 1):
                    if not prune(row, col - 1, v):
                        return False, pruned

            elif sign == -1:  # Left > Right
                for v in range(1, val + 1):
                    if not prune(row, col - 1, v):
                        return False, pruned

        # Vertical constraints
        # Check Lower cell (row + 1)
        if row < problem.size - 1 and problem.VerticalConstraints[row][col] != 0:
            sign = get_sign(problem.VerticalConstraints[row][col])

            if sign == 1:  # up < down
                for v in range(1, val + 1):
                    if not prune(row + 1, col, v):
                        return False, pruned

            elif sign == -1:  # Up > Down
                for v in range(val, problem.size + 1):
                    if not prune(row + 1, col, v):
                        return False, pruned

        # Check Upper (row - 1)
        if row > 0 and problem.VerticalConstraints[row - 1][col] != 0:
            sign = get_sign(problem.VerticalConstraints[row - 1][col])

            if sign == 1:  # Up < Down
                for v in range(val, problem.size + 1):
                    if not prune(row - 1, col, v):
                        return False, pruned

            elif sign == -1:  # Up > Down
                for v in range(1, val + 1):
                    if not prune(row - 1, col, v): return False, pruned

        return True, pruned

    def get_mrv_cell(self, available):
        """
        Minimum Remaining Values (MRV).
        """
        best_cell = None
        min_options = float('inf')

        # scan for min domain
        for (r, c), valid_values in available.items():
            options = len(valid_values)
            if options < min_options:
                min_options = options
                best_cell = (r, c)

                # if it only has 0 or 1 opt, nothing can be improved
                if min_options <= 1:
                    break

        return best_cell