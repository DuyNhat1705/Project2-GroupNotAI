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
        self.is_solved = False
        super().__init__("Backward Chaining", params)

    def solve(self, problem):
        # Init State
        self.is_solved = False
        self.kb = KnowledgeBase(problem)
        self.domains = self.init_domain(problem)

        start_time = time.perf_counter()
        print(f"Backward chaining for {problem.size}x{problem.size}...\n")

        # Log starting clues and initial pruning
        for r in range(problem.size):
            for c in range(problem.size):
                val = problem.grid[r][c]
                if val != 0:
                    self.forward_check_kb(problem, self.domains, r, c, val)

        # Recursive search
        if self.backtrack_solve(problem, self.domains):
            self.is_solved = True
            step_logger.execution_time = (time.perf_counter() - start_time) * 1000

            # Filter out all 'Val' and 'Given' facts
            clean_facts = []
            for fact in self.kb.obs_facts:
                if hasattr(fact, 'name') and fact.name in ['Val', 'Given']:
                    continue  # Throw it in the trash
                clean_facts.append(fact)

            self.kb.obs_facts = clean_facts

            # Rebuild the KB leaning on solved grid
            for r in range(problem.size):
                for c in range(problem.size):
                    val = problem.grid[r][c]
                    self.kb.obs_facts.append(Atom('Val', r + 1, c + 1, int(val)))

            print(f"\nPuzzle Solved in {step_logger.execution_time:.2f}ms!\n")
            problem.printFutoshiki()
            return problem.grid
        else:
            step_logger.execution_time = (time.perf_counter() - start_time) * 1000
            print("\nFAILED: The engine could not find a valid solution.")
            return problem.grid


    def backtrack_solve(self, problem, domains):
        # Get the MRV cell
        cell = self.get_mrv_cell(domains)

        if cell is None:
            return True  # Board solved

        row, col = cell

        query = Atom('Val', row + 1, col + 1, Var('$v'))
        ans = list(self.fol_bc_ask(query))

        unique_vals = set()

        for theta in ans:
            # Safely unpack the value through the variable chain
            raw_val_expr = Substitute(theta, Var('$v'))
            val = self.unpack_val(raw_val_expr)

            # Logic Generation and Domain Pruning
            # only proceed if the SLD guess survives the Forward Check
            if val in domains[(row, col)] and val not in unique_vals:
                unique_vals.add(val)  # Mark as seen

                valid_flag, pruned_list = self.forward_check_kb(problem, domains, row, col, val)

                if valid_flag:
                    # Commit to the board
                    problem.grid[row][col] = val
                    fact = Atom('Given', row + 1, col + 1, val)
                    self.kb.obs_facts.append(fact)

                    step_logger.log_step(row + 1, col + 1, val, tag='try',
                                         domains=self._sync_GUI(problem, domains),
                                         facts_count=len(self.kb.obs_facts))

                    saved_domain = domains.pop((row, col))

                    # Move forward recursively
                    if self.backtrack_solve(problem, domains):
                        return True

                    # --- BACKTRACK ---
                    domains[(row, col)] = saved_domain
                    problem.grid[row][col] = 0
                    self.kb.obs_facts.remove(fact)

                    step_logger.log_step(row + 1, col + 1, 0, tag='backtrack',
                                         domains=self._sync_GUI(problem, domains),
                                         facts_count=len(self.kb.obs_facts))

                # Put back numbers removed from neighbors' domains
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
                            if not prune_set(row, col + 1, lambda v_next: v_next > val):
                                return False, pruned
                        elif fact_r == row and fact_c == col - 1:  # Current is Right
                            if not prune_set(row, col - 1, lambda v_prev: v_prev < val):
                                return False, pruned

                    elif fact.name == 'GreaterH':
                        if fact_r == row and fact_c == col:  # Current is Left
                            if not prune_set(row, col + 1, lambda v_next: v_next < val):
                                return False, pruned
                        elif fact_r == row and fact_c == col - 1:  # Current is Right
                            if not prune_set(row, col - 1, lambda v_prev: v_prev > val):
                                return False, pruned

                    # --- Vertical Constraints ---
                    elif fact.name == 'LessV':
                        if fact_r == row and fact_c == col:  # Current is Top
                            if not prune_set(row + 1, col, lambda v_bot: v_bot > val):
                                return False, pruned
                        elif fact_r == row - 1 and fact_c == col:  # Current is Bottom
                            if not prune_set(row - 1, col, lambda v_top: v_top < val):
                                return False, pruned

                    elif fact.name == 'GreaterV':
                        if fact_r == row and fact_c == col:  # Current is Top
                            if not prune_set(row + 1, col, lambda v_bot: v_bot < val):
                                return False, pruned
                        elif fact_r == row - 1 and fact_c == col:  # Current is Bottom
                            if not prune_set(row - 1, col, lambda v_top: v_top > val):
                                return False, pruned

        return True, pruned


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

    def _start_query_console(self, problem):
        """Interactive console tied to Knowledge Base with Pre/Post Solve awareness."""

        # --- Initialization & Initial Clue Pruning ---
        if getattr(self, 'kb', None) is None:
            print("Initializing Knowledge Base and parsing initial clues...")
            self.kb = KnowledgeBase(problem)
            self.domains = self.init_domain(problem)  # Store as instance variable

            # Apply initial clues on Pre-Solve scratchpad
            for r in range(problem.size):
                for c in range(problem.size):
                    val = problem.grid[r][c]
                    if val != 0:
                        # 1-idx for the Knowledge Base
                        fact = Atom('Val', r + 1, c + 1, int(val))
                        if fact not in self.kb.obs_facts:
                            self.kb.obs_facts.append(fact)

                        # Trigger forward checker to prune the domains
                        if hasattr(self, 'forward_check_kb'):
                            self.forward_check_kb(problem, self.domains, r, c, val)

            self.is_solved = False

        # Print tutorial and State Awareness
        print("\n" + "=" * 50)
        print("Futoshiki Query Engine")
        state_str = "SOLVED" if getattr(self, 'is_solved', False) else "UNSOLVED (Domains Loaded)"
        print(f" Current State: {state_str}")
        print(" Variables must be Uppercase")
        print(" Type 'exit' to quit.")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n?- ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break

                # Strip trailing period
                if user_input.endswith('.'):
                    user_input = user_input[:-1]

                # Prevent crash on empty input
                if not user_input:
                    continue

                # Regex parser
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
                        parsed_args.append(int(arg))
                    elif arg[0].isupper() or arg.startswith('$'):
                        parsed_args.append(Var(arg))
                    else:
                        parsed_args.append(arg)

                # --- Pre-Solve Short-Circuit ---
                # Query check: Val(int, int, Variable)
                is_domain_query = (
                        name == 'Val' and
                        len(parsed_args) == 3 and
                        isinstance(parsed_args[0], int) and
                        isinstance(parsed_args[1], int) and
                        isinstance(parsed_args[2], Var)
                )

                if is_domain_query and not getattr(self, 'is_solved', False):
                    # PRE-SOLVED: Just look in domain scratchpad
                    r, c = parsed_args[0], parsed_args[1]
                    var_name = parsed_args[2].name

                    domain = getattr(self, 'domains', {}).get((r - 1, c - 1))

                    if domain:
                        print(f"{var_name} = {{{', '.join(map(str, sorted(domain)))}}} ;")
                    else:
                        print("false. (Domain is empty or out of bounds)")

                    print("false.")
                    continue  # Skip the rest of the loop

                # --- Post-Solve ---
                # Create query Atom and run full SLD Resolution
                query = Atom(name, *parsed_args)
                self.ask_prolog(query)

            except Exception as e:
                print(f"Error executing query: {e}")

    def ask_prolog(self, query_atom):
        """Executes a logical query and formats the output with Domain awareness."""
        print(f"\n?- {query_atom}")

        query_vars = self._extract_vars(query_atom)
        answers = list(self.fol_bc_ask(query_atom))

        if not answers:
            print("false.")
            return

        # Track printed bindings to eliminate duplicates
        printed_bindings = set()

        for theta in answers:
            if not query_vars:
                if "true" not in printed_bindings:
                    print("true ;")
                    printed_bindings.add("true")
                continue

            bindings = []
            all_unbound = True  # Track ghost variables

            for var_name in query_vars:
                raw_val = Substitute(theta, Var(var_name))
                clean_val = self.unpack_val(raw_val)

                if isinstance(clean_val, Var):
                    clean_val = "_"
                else:
                    all_unbound = False  # At least one real value exists

                bindings.append(f"{var_name} = {clean_val}")

            # Skip ghost proofs (e.g., C = _, R = _)
            if all_unbound:
                continue

            binding_str = ", ".join(bindings)

            # Only print if not seen this exact answer yet
            if binding_str not in printed_bindings:
                print(binding_str + " ;")
                printed_bindings.add(binding_str)

        print("false.")

    def _sync_GUI(self, problem, domains):
        """
        Combines the physical grid and the domain scratchpad
        """
        snap = {}
        for r in range(problem.size):
            for c in range(problem.size):

                # Convert 0-idx (backend) to 1-idx (UI)
                ui_r = r + 1
                ui_c = c + 1

                if problem.grid[r][c] != 0:
                    # Cell is physically placed on the board
                    snap[(ui_r, ui_c)] = {int(problem.grid[r][c])}
                elif (r, c) in domains:
                    # Cell is empty, grab available options
                    snap[(ui_r, ui_c)] = set(domains[(r, c)])

        return snap