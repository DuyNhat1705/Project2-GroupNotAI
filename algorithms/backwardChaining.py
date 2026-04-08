import time
import re
from utils.logger import step_logger
from algorithms.base_algorithm import BaseAlgorithm
from algorithms.logic import Var, Const, Atom, Bot, Top, And, Imply, Unify, Substitute, KnowledgeBase

class BackwardChaining(BaseAlgorithm):

    def __init__(self, params = None):
        self.kb = None
        self.cnt = 0 # later assigned idx
        self.domains = None
        super().__init__("Backward Chaining", params)

    def solve(self, problem):
        self.kb = KnowledgeBase(problem)
        self.domains = self.init_domain(problem)  # Store as instance variable

        step_logger.reset(problem)
        start_time = time.perf_counter()
        print(f"Backward chaining for {problem.size}x{problem.size}...\n")

        # initial scratchpad
        domains = self.init_domain(problem)

        # Log the starting clues
        for r in range(problem.size):
            for c in range(problem.size):
                if problem.grid[r][c] != 0:
                    step_logger.log_step(r + 1, c + 1, problem.grid[r][c], tag='given',
                                         domains=dict(domains),
                                         facts_count=len(self.kb.obs_facts))

        step_logger.execution_time = (time.perf_counter() - start_time) * 1000

        # recursive search
        if self.backtrack_solve(problem, domains):
            print(f"\nPuzzle Solved!\n")
            print(step_logger.execution_time)
            problem.printFutoshiki()
            return problem.grid
        else:
            print("\nFAILED: The engine could not find a valid solution.")
            return problem.grid

    def backtrack_solve(self, problem, domains):
        # get the MRV cell
        cell = self.get_mrv_cell(domains)

        if cell is None:
            return True  # Board solved

        row, col = cell

        # Ask FOL Engine for candidates
        query = Atom('Val', row + 1, col + 1, Var('$v'))
        ans = list(self.fol_bc_ask(query))

        unique_vals = set()

        for theta in ans:
            # Safely unpack the value through the variable chain
            raw_val_expr = Substitute(theta, Var('$v'))
            val = self.unpack_val(raw_val_expr)

            # Only try value if it is in valid domain
            if val in domains[(row, col)] and val not in unique_vals:
                unique_vals.add(val)  # Mark as seen

                if self.is_safe(problem, row, col, val):
                    # Try placing and Forward Check
                    valid_flag, pruned_list = self.forward_check_kb(problem, domains, row, col, val)

                    if valid_flag:
                        # if safe, commit to the board
                        problem.grid[row][col] = val
                        fact = Atom('Given', row + 1, col + 1, val)
                        self.kb.obs_facts.append(fact)

                        # Log attempt
                        step_logger.log_step(row + 1, col + 1, val, tag='try',
                                             domains=dict(domains),
                                             facts_count=len(self.kb.obs_facts))

                        # Temporarily remove this cell from the domains
                        saved_domain = domains.pop((row, col))

                        # Move forward
                        if self.backtrack_solve(problem, domains):
                            return True

                        # Restore to the domains dict
                        domains[(row, col)] = saved_domain
                        problem.grid[row][col] = 0
                        self.kb.obs_facts.remove(fact)

                        # Log the backtrack 
                        step_logger.log_step(row + 1, col + 1, 0, tag='backtrack',
                                             domains=dict(domains),
                                             facts_count=len(self.kb.obs_facts))

                    # Put back num removed from domains
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

    def forward_check_kb(self, problem, domains, start_row, start_col, start_val):
        pruned = []
        queue = [(start_row, start_col, start_val)]

        def prune_set(r, c, condition):
            if (r, c) not in domains:
                return True

            original_len = len(domains[(r, c)])
            invalid_vals = {x for x in domains[(r, c)] if not condition(x)}

            for v in invalid_vals:
                domains[(r, c)].remove(v)
                pruned.append((r, c, v))
            new_len = len(domains[(r, c)])

            if new_len == 0:
                return False
            if original_len > 1 and new_len == 1:
                queue.append((r, c, next(iter(domains[(r, c)]))))

            return True

        while queue:
            # Pop 0-idx coordinates
            row, col, val = queue.pop(0)

            # Row & Column checks
            for x in range(problem.size):
                if x != col:
                    if not prune_set(row, x, lambda x_val: x_val != val): return False, pruned
                if x != row:
                    if not prune_set(x, col, lambda x_val: x_val != val): return False, pruned

            # KB Constraint Checks
            for fact in self.kb.obs_facts:
                if not hasattr(fact, 'name'):
                    continue

                if fact.name in ['LessH', 'GreaterH', 'LessV', 'GreaterV']:
                    # Extract KB coordinates and convert to 0-idx
                    # handle both integer literals and Const
                    raw_r = fact.args[0].value if hasattr(fact.args[0], 'value') else fact.args[0]
                    raw_c = fact.args[1].value if hasattr(fact.args[1], 'value') else fact.args[1]

                    fact_r = int(raw_r) - 1
                    fact_c = int(raw_c) - 1

                    # --- Horizontal Constraints ---
                    if fact.name == 'LessH':
                        if fact_r == row and fact_c == col:  # Current is Left
                            if not prune_set(row, col + 1, lambda v_next: v_next > val): return False, pruned
                        elif fact_r == row and fact_c == col - 1:  # Current is Right
                            if not prune_set(row, col - 1, lambda v_prev: v_prev < val): return False, pruned

                    elif fact.name == 'GreaterH':
                        if fact_r == row and fact_c == col:  # Current is Left
                            if not prune_set(row, col + 1, lambda v_next: v_next < val): return False, pruned
                        elif fact_r == row and fact_c == col - 1:  # Current is Right
                            if not prune_set(row, col - 1, lambda v_prev: v_prev > val): return False, pruned

                    # --- Vertical Constraints ---
                    elif fact.name == 'LessV':
                        if fact_r == row and fact_c == col:  # Current is Top
                            if not prune_set(row + 1, col, lambda v_bot: v_bot > val): return False, pruned
                        elif fact_r == row - 1 and fact_c == col:  # Current is Bottom
                            if not prune_set(row - 1, col, lambda v_top: v_top < val): return False, pruned

                    elif fact.name == 'GreaterV':
                        if fact_r == row and fact_c == col:  # Current is Top
                            if not prune_set(row + 1, col, lambda v_bot: v_bot < val): return False, pruned
                        elif fact_r == row - 1 and fact_c == col:  # Current is Bottom
                            if not prune_set(row - 1, col, lambda v_top: v_top > val): return False, pruned

        return True, pruned

    def is_safe(self, problem, row, col, val):
        """
        Safety check with Ground KB.
        """
        R = row + 1
        C = col + 1
        V = int(val)

        # Hypothetical state: (r, c, v)
        hypo_state = set()

        # Add the new guess to be tested
        hypo_state.add((R, C, V))

        # Add all existing values in KB
        for fact in self.kb.obs_facts:
            if hasattr(fact, 'name') and fact.name in ['Given', 'Val']:
                # Safely extract raw int whether they are Const objects or ints
                fact_r = int(fact.args[0].value if hasattr(fact.args[0], 'value') else fact.args[0])
                fact_c = int(fact.args[1].value if hasattr(fact.args[1], 'value') else fact.args[1])
                fact_v = int(fact.args[2].value if hasattr(fact.args[2], 'value') else fact.args[2])

                hypo_state.add((fact_r, fact_c, fact_v))

        # Check the Ground Rules for a contradiction
        for rule in self.kb.ground_rules:
            # focus Implication rules that lead to Contradiction
            if not isinstance(rule, Imply) or not isinstance(rule.right, Bot):
                continue

            premise = rule.left

            # Collect the atoms from the premise
            if isinstance(premise, And):
                atoms = premise.args
            else:
                atoms = [premise]

            # Check if every atom in the premise exists in our hypothetical state
            rule_triggers = True
            for a in atoms:
                # If the rule checks other than a Val, skip
                if a.name != 'Val':
                    rule_triggers = False
                    break

                # Extract raw values from the rule's atom
                a_r = int(a.args[0].value if hasattr(a.args[0], 'value') else a.args[0])
                a_c = int(a.args[1].value if hasattr(a.args[1], 'value') else a.args[1])
                a_v = int(a.args[2].value if hasattr(a.args[2], 'value') else a.args[2])

                # If this (r, c, v) is not on the board, contradiction rule doesn't trigger
                if (a_r, a_c, a_v) not in hypo_state:
                    rule_triggers = False
                    break

            # If all premises matched hypothetical state, the rule triggers
            if rule_triggers:
                return False  # Contradiction found => NOT safe

        # Survived alL rule checks
        return True


    # --- Prolog-style Query ---

    def _extract_vars(self, expr):
        """Recursively finds all Var in a logic expression."""
        if isinstance(expr, Var):
            return {expr.name}
        elif isinstance(expr, Atom):
            vars_set = set()
            for arg in expr.args:
                vars_set.update(self._extract_vars(arg))
            return vars_set
        return set()

    def ask_prolog(self, query_atom):
        """Executes a logical query and formats the output with Domain awareness."""
        print(f"\n?- {query_atom}")

        query_vars = self._extract_vars(query_atom)
        answers = list(self.fol_bc_ask(query_atom))

        if not answers:
            print("false.")
            return

        for theta in answers:
            if not query_vars:
                print("true ;")
                continue

            bindings = []
            for var_name in query_vars:
                raw_val = Substitute(theta, Var(var_name))
                clean_val = self.unpack_val(raw_val)

                # ---  Domain Reporting ---
                if isinstance(clean_val, Var):
                    # Check if the query was Val(Row, Col, Var)
                    if query_atom.name == 'Val' and len(query_atom.args) == 3:
                        try:
                            # Extract coordinates from the original query atom
                            r = self.unpack_val(Substitute(theta, query_atom.args[0]))
                            c = self.unpack_val(Substitute(theta, query_atom.args[1]))

                            # Look up the pruned domain from the solver's state
                            # (r-1, c-1) to 0-idx
                            current_domain = self.domains.get((r - 1, c - 1))

                            if current_domain:
                                # Format as a Prolog set: {1, 2, 5}
                                clean_val = f"{{{', '.join(map(str, sorted(current_domain)))}}}"
                            else:
                                clean_val = "_"
                        except:
                            clean_val = "_"
                    else:
                        clean_val = "_"

                bindings.append(f"{var_name} = {clean_val}")

            print(", ".join(bindings) + " ;")

        print("false.")

    def _start_query_console(self):
        """interactive console tied to Knowledge Base."""
        if self.kb is None:
            print("Error: Knowledge Base is empty")
            return

        # print brief tutorial
        print("\n" + "=" * 50)
        print("Futoshiki Prolog-style query engine")
        print("Variables must be Uppercase")
        print("Type 'exit' to quit.")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n?- ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break

                # Strip the trailing period
                if user_input.endswith('.'):
                    user_input = user_input[:-1]

                # Simple regex to parse things
                match = re.match(r"^(\w+)\((.*)\)$", user_input)
                if not match:
                    print("Syntax Error. Format: Predicate(arg1, arg2...)")
                    continue

                name = match.group(1)
                args_str = match.group(2).split(',')

                # Parse args
                parsed_args = []
                for arg in args_str:
                    arg = arg.strip()
                    if arg.isdigit():
                        parsed_args.append(int(arg))  # integer constant
                    elif arg[0].isupper() or arg.startswith('$'):
                        parsed_args.append(Var(arg))  # a Variable
                    else:
                        parsed_args.append(arg)  # string constant

                # Create the query Atom and run
                query = Atom(name, *parsed_args)
                self.ask_prolog(query)

            except Exception as e:
                print(f"Error executing query: {e}")