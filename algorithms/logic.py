import problem.futoshiki

class Expression:
    def __repr__(self):
        return str(self)

# Formula <-> truth value.
class Formula(Expression): pass

# Term <-> object.
class Term(Expression): pass

class Top(Expression): # tautology
    def __str__(self): return "TRUE"
    def __eq__(self, other): return isinstance(other, Top)
    def __hash__(self): return hash("TRUE")

class Bot(Expression): # contradiction
    def __str__(self): return "FALSE"
    def __eq__(self, other): return isinstance(other, Bot)
    def __hash__(self): return hash("FALSE")

class Var(Term):
    def __init__(self, name):
        self.name = name # syntax: $var_name
    def __str__(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name
    def __hash__(self):
        return hash(self.name) # required due to __eq__

class Const(Term):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, Const) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

class Atom(Formula):
    def __init__(self, name, *args):
        self.name = name
        self.args = [Var(p) if isinstance(p, str) and p.startswith('$')
                     else Const(p) if isinstance(p, (int, str)) and not isinstance(p, Expression)
                     else p for p in args]

    def __str__(self):
        args_str = ", ".join(str(p) for p in self.args)
        return f"{self.name}({args_str})"
    
    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name and self.args == other.args

    def __hash__(self):
        return hash((self.name, tuple(self.args)))

def toExpr(x):
    if isinstance(x, str):
        if x.startswith('$'): return Var(x)
        return Const(x)
    return x

class Not(Expression):
    def __init__(self, arg):
        self.arg = arg
    def __str__(self):
        return f"NOT({self.arg})"

class And(Expression):
    def __init__(self, *args):
        self.args = list(args)
    def __str__(self):
        return "AND(" + " , ".join(str(arg) for arg in self.args) + ")"

class Or(Expression):
    def __init__(self, *args):
        self.args = list(args)
    def __str__(self):
        return "OR(" + " v ".join(str(arg) for arg in self.args) + ")"

class Imply(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return f"({self.left} => {self.right})"

class Exist(Formula):
    def __init__(self, var, clause):
        self.var = Var(var) if isinstance(var, str) else str(var)
        self.body = clause
    def __str__(self):
        return 'EXISTS(' + str(self.var) + ',' + str(self.body) + ')'

class Forall(Formula):
    def __init__(self, var, clause):
        self.var = Var(var) if isinstance(var, str) else str(var)
        self.body = clause
    def __str__(self):
        return 'FORALL(' + str(self.var) + ',' + str(self.body) + ')'

def Substitute(theta, expr):
    if isinstance(expr, Var):
        if expr.name in theta:
            # recursively call substitute in case it points to another var
            return Substitute(theta, theta[expr.name])
        return expr
    elif isinstance(expr, Const):
        return expr
    elif isinstance(expr, Atom):
        return Atom(expr.name, *[Substitute(theta, arg) for arg in expr.args])
    elif isinstance(expr, And):
        return And(*[Substitute(theta, arg) for arg in expr.args])
    elif isinstance(expr, Or):
        return Or(*[Substitute(theta, arg) for arg in expr.args])
    elif isinstance(expr, Imply):
        return Imply(Substitute(theta, expr.left), Substitute(theta, expr.right))
    elif isinstance(expr, Not):
        return Not(Substitute(theta, expr.arg))
    return expr

def Unify(x, y, theta):
    if theta is None:
        return None
    elif x == y:
        return theta
    
    # if x or y is a var: unify the var with other term
    elif isinstance(x, Var):
        return Unify_var(x, y, theta)
    elif isinstance(y, Var):
        return Unify_var(y, x, theta)
    
    elif isinstance(x, Atom) and isinstance(y, Atom):
        # match predicate names 
        # recursively match args
        return Unify(x.args, y.args, Unify(x.name, y.name, theta))
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): return None
        if not x: return theta
        return Unify(x[1:], y[1:], Unify(x[0], y[0], theta))
    else:
        return None

def Unify_var(var, x, theta):
    if var.name in theta:
        return Unify(theta[var.name], x, theta)
    elif isinstance(x, Var) and x.name in theta:
        return Unify(var, theta[x.name], theta)
    else:
        new_theta = theta.copy()
        new_theta[var.name] = x
        return new_theta

def Val(i, j, v):
    return Atom('Val', i, j, v)

def Given(i, j, v):
    return Atom('Given', i, j, v)

def LessH(i, j):
    return Atom('LessH', i, j)

def GreaterH(i, j):
    return Atom('GreaterH', i, j)

def LessV(i, j):
    return Atom('LessV', i, j)

def GreaterV(i, j):
    return Atom('GreaterV', i, j)

def Less(i, j):
    return Atom('Less', i, j)

def Eq(a, b): # equal
    return Atom('Equals', a, b)

def Next(idx, next_idx):
    return Atom('Next',idx, next_idx)

class KnowledgeBase:
    def __init__(self, Futo_instance):
        self.riddle = Futo_instance
        self.domain = list(range(1, self.riddle.size + 1)) # cell value domain
        self.axioms = [] # list of universal axioms
        self.obs_facts = [] # list of observed facts: clues and inferred truths
        self.horn_rules = []

        self._gen_axioms()
        self._math_sense()
        self._ground_CNF()
        self._init_facts()
        self.init_horn_rules()
    
    def tell(self, clause):
        self.obs_facts.append(clause)
        
    def _math_sense(self):
        """Define Adjacency and Comparative Relations"""

        for idx in range(1, self.riddle.size):
            self.tell(Atom('NextCol', idx, idx + 1))
            self.tell(Atom('NextRow', idx, idx + 1)) 
            
        for v1 in range(1, self.riddle.size + 1):
            for v2 in range(1, self.riddle.size + 1):
                if v1 < v2:
                    self.tell(Atom('Less', v1, v2))

        for v in range(1, self.riddle.size + 1):
            self.tell(Atom('InDomain', v))
        
    def _gen_axioms(self):
        # A1 (Every cell has at least one valid value):
        atom_domain = [Val('$i', '$j', v) for v in self.domain]
        A1 = Forall('$i', Forall('$j', Or(*atom_domain)))

        # A2 (Every cell has at most one value):
        A2 = Forall('$i', 
                Forall('$j',
                        (Forall('$v1', 
                                Forall('$v2',
                                       Imply(And(Val('$i', '$j', '$v1'), Val('$i', '$j', '$v2')),
                                             Eq('$v1', '$v2')))))))
        
        # A3 (Row uniqueness):
        A3 = Forall('$i',
                    Forall('$j1',
                           Forall('$j2',
                                  Forall('$v',
                                         Imply(And(Val('$i', '$j1', '$v'), Val('$i', '$j2', '$v'), Not(Eq('$j1', '$j2'))),
                                               Bot())))))
        
        # A4 (Horizontal less-than constraints):
        A4 = Forall('$i', 
                        Forall('$j', 
                                Forall('$j_next', 
                                        Forall('$v1', 
                                            Forall('$v2',
                                                   Imply(
                                                        And(
                                                            LessH('$i', '$j'),                  
                                                            Atom('NextCol', '$j', '$j_next'),   
                                                            Val('$i', '$j', '$v1'),             
                                                            Val('$i', '$j_next', '$v2')),        
                                                        Atom('Less', '$v1', '$v2')             
                                                    ))))))
        
        # A5 (Given clues are enforced):
        A5 = Forall('$i', Forall('$j', Forall('$v', Imply(Given('$i', '$j', '$v'), Val('$i', '$j', '$v')))))
        
        # A6 (Column uniqueness):
        A6 = Forall('$j',
                    Forall('$i1',
                           Forall('$i2',
                                  Forall('$v',
                                         Imply(And(Val('$i1', '$j', '$v'), Val('$i2', '$j', '$v'), Not(Eq('$i1', '$i2'))),
                                               Bot())))))
        
        # A7 (Vertical less-than constraints):
        A7 = Forall('$i', 
                        Forall('$j', 
                                Forall('$i_next', 
                                        Forall('$v1', 
                                            Forall('$v2',
                                                   Imply(
                                                        And(
                                                            LessV('$i', '$j'),                
                                                            Atom('NextRow', '$i', '$i_next'),   
                                                            Val('$i', '$j', '$v1'),            
                                                            Val('$i_next', '$j', '$v2')),         
                                                        Atom('Less', '$v1', '$v2')             
                                                    ))))))
        
        # A8 (Horizontal greater-than constraints):
        A8 = Forall('$i', 
                        Forall('$j', 
                                Forall('$j_next', 
                                        Forall('$v1', 
                                            Forall('$v2',
                                                   Imply(
                                                        And(
                                                            GreaterH('$i', '$j'),                  
                                                            Atom('NextCol', '$j', '$j_next'),   
                                                            Val('$i', '$j', '$v1'),            
                                                            Val('$i', '$j_next', '$v2')),       
                                                        Atom('Less', '$v2', '$v1') 
                                                    ))))))
        
        # A9 (Vertical greater-than constraints):
        A9 = Forall('$i', 
                        Forall('$j', 
                                Forall('$i_next', 
                                        Forall('$v1', 
                                            Forall('$v2',
                                                   Imply(
                                                        And(
                                                            GreaterV('$i', '$j'),                  
                                                            Atom('NextRow', '$i', '$i_next'),  
                                                            Val('$i', '$j', '$v1'),            
                                                            Val('$i_next', '$j', '$v2')),         
                                                        Atom('Less', '$v2', '$v1')              
                                                    ))))))
        
        self.axioms = [A1, A2, A3, A4, A5, A6, A7, A8, A9]

    def _ground_CNF(self):
        """
        Apply initial game state to achieve ground truth from axioms
        CNF representation
        Static to each riddles
        """
        self.ground_rules = []
        sz = self.riddle.size

        # Cell Completeness & Uniqueness
        for i in self.domain:
            for j in self.domain:
                fixed_val = self.riddle.grid[i - 1][j - 1]

                if fixed_val != 0: # the given clue
                    self.ground_rules.append(Val(i, j, fixed_val))
                else:
                    # Empty cell -> gen domain rules
                    domain_atoms = [Val(i, j, v) for v in self.domain]
                    self.ground_rules.append(Or(*domain_atoms))

                    for v1 in self.domain:
                        for v2 in self.domain:
                            if v1 < v2:
                                rule = Imply(And(Val(i, j, v1), Val(i, j, v2)), Bot()) # Contradiction if not unique value
                                self.ground_rules.append(rule)

        # Row uniqueness
        for i in self.domain:
            for v in self.domain:
                # Check if this v is already placed in this row
                placed_col = None
                for c in range(sz):
                    if self.riddle.grid[i - 1][c] == v:
                        placed_col = c + 1 # logic idx
                        break

                for j1 in self.domain:
                    for j2 in self.domain:
                        if j1 < j2:
                            # if placed, do not gen collision rule for empty cell
                            if placed_col is None or placed_col in (j1, j2): # if not assigned or placed in col j1 or j2
                                rule = Imply(And(Val(i, j1, v), Val(i, j2, v)), Bot())
                                self.ground_rules.append(rule)

        # Column uniqueness
        # same as Row
        for j in self.domain:
            for v in self.domain:
                placed_row = None
                for r in range(sz):
                    if self.riddle.grid[r][j - 1] == v:
                        placed_row = r + 1
                        break

                for i1 in self.domain:
                    for i2 in self.domain:
                        if i1 < i2:
                            if placed_row is None or placed_row in (i1, i2):
                                rule = Imply(And(Val(i1, j, v), Val(i2, j, v)), Bot())
                                self.ground_rules.append(rule)

        # Horizontal constraints (LessH & GreaterH)
        for i in self.domain:
            for j in range(1, sz):
                sign = self.riddle.HorizontalConstraints[i - 1][j - 1]
                if sign == 0:
                    continue  # No constraint

                # check the actual values
                left_val = self.riddle.grid[i - 1][j - 1]
                right_val = self.riddle.grid[i - 1][j]

                for v1 in self.domain:
                    for v2 in self.domain:
                        # check v1/v2 if they align with known clues
                        if (left_val == 0 or left_val == v1) and (right_val == 0 or right_val == v2):
                            if sign == 1 and v1 >= v2:  # LessH violation
                                rule = Imply(And(Val(i, j, v1), Val(i, j + 1, v2)), Bot())
                                self.ground_rules.append(rule)
                            elif sign == -1 and v1 <= v2:  # GreaterH violation
                                rule = Imply(And(Val(i, j, v1), Val(i, j + 1, v2)), Bot())
                                self.ground_rules.append(rule)

        # Vertical Constraints (LessV & GreaterV)
        # same as Horizontal
        for i in range(1, sz):
            for j in self.domain:
                sign = self.riddle.VerticalConstraints[i - 1][j - 1]
                if sign == 0:
                    continue

                top_val = self.riddle.grid[i - 1][j - 1]
                bot_val = self.riddle.grid[i][j - 1]

                for v1 in self.domain:
                    for v2 in self.domain:
                        #  check v1/v2 if they align with known clues
                        if (top_val == 0 or top_val == v1) and (bot_val == 0 or bot_val == v2):
                            if sign == 1 and v1 >= v2:  # LessV violation
                                rule = Imply(And(Val(i, j, v1), Val(i + 1, j, v2)), Bot())
                                self.ground_rules.append(rule)
                            elif sign == -1 and v1 <= v2:  # GreaterV violation
                                rule = Imply(And(Val(i, j, v1), Val(i + 1, j, v2)), Bot())
                                self.ground_rules.append(rule)
        
    def _init_facts(self):
        """
        Grid and constraints from Futoshiki instance => Observed facts
        Facts will be extended by inference progress
        """
        # Load Given Values
        sz = self.riddle.size
        for i in range(sz):
            for j in range(sz):
                val = self.riddle.grid[i][j]
                if val != 0: # is given
                    self.obs_facts.append(Given(i + 1, j + 1, val))

        # Load Horizontal Constraints
        for i in range(self.riddle.size):
            for j in range(self.riddle.size - 1):
                sign = self.riddle.HorizontalConstraints[i][j]
                if sign == 1:     # '<'
                    self.obs_facts.append(LessH(i + 1, j + 1))
                elif sign == -1:  # '>'
                    self.obs_facts.append(GreaterH(i + 1, j + 1))

        # Load Vertical Constraints
        for i in range(self.riddle.size - 1):
            for j in range(self.riddle.size):
                sign = self.riddle.VerticalConstraints[i][j]
                if sign == 1:     # '^'
                    self.obs_facts.append(LessV(i + 1, j + 1))
                elif sign == -1:  # 'v'
                    self.obs_facts.append(GreaterV(i + 1, j + 1))

    def init_horn_rules(self):
        """
        Defines abstract Horn clauses for Backward Chaining
        Format: Imply(Premise, Conclusion)
        """

        # Force the given value (Base truth)
        self.horn_rules.append(Imply(
            Given('$i', '$j', '$v'),
            Val('$i', '$j', '$v')
        ))

        # cell's value v1: if exist LessH constraint -> check the next column (v2), and v1 < v2.
        self.horn_rules.append(Imply(
            And(
                LessH('$i', '$j'),
                Atom('NextCol', '$j', '$j_next'),
                Given('$i', '$j_next', '$v2'),
                Atom('Less', '$v1', '$v2')
            ),
            Val('$i', '$j', '$v1')
        ))

        # Reverse LessH (Horn rule required)
        # A cell value v2 if there is a LessH constraint on the prev col
        # the previous cell val is v1, and v1 < v2.
        self.horn_rules.append(Imply(
            And(
                Atom('NextCol', '$j_prev', '$j'),  # Find the column to the left
                LessH('$i', '$j_prev'),  # Check if it has a '<'
                Given('$i', '$j_prev', '$v1'),  #
                Atom('Less', '$v1', '$v2')  # Ensure less-than
            ),
            Val('$i', '$j', '$v2')
        ))

        # GreaterH (Left > Right)
        # The left cell v1 if the right cell is v2, and v2 < v1
        self.horn_rules.append(Imply(
            And(
                GreaterH('$i', '$j'),
                Atom('NextCol', '$j', '$j_next'),
                Given('$i', '$j_next', '$v2'),
                Atom('Less', '$v2', '$v1')  # order flipped
            ),
            Val('$i', '$j', '$v1')
        ))

        # Reverse GreaterH (Left > Right)
        # The right cell is v2 if the left cell is v1, and v2 < v1
        self.horn_rules.append(Imply(
            And(
                Atom('NextCol', '$j_prev', '$j'),  # find the left col
                GreaterH('$i', '$j_prev'),  # Check if it has a '>'
                Given('$i', '$j_prev', '$v1'),
                Atom('Less', '$v2', '$v1')  # Ensure constraint
            ),
            Val('$i', '$j', '$v2')
        ))

        # LessV (Top < Bottom)
        # The top cell is v1 if the bottom cell is v2, and v1 < v2
        self.horn_rules.append(Imply(
            And(
                LessV('$i', '$j'),
                Atom('NextRow', '$i', '$i_next'),
                Given('$i_next', '$j', '$v2'),
                Atom('Less', '$v1', '$v2')
            ),
            Val('$i', '$j', '$v1')
        ))

        # Reverse LessV (Top < Bottom)
        # The lower cell is v2 if the upper cell is v1, and v1 < v2
        self.horn_rules.append(Imply(
            And(
                Atom('NextRow', '$i_prev', '$i'),  # Find the row above us
                LessV('$i_prev', '$j'),  # Check if it has a '^'
                Given('$i_prev', '$j', '$v1'),
                Atom('Less', '$v1', '$v2')
            ),
            Val('$i', '$j', '$v2')
        ))

        # GreaterV (Up > Down)
        # upper cell is v1 if the lower cell is v2, and v2 < v1
        self.horn_rules.append(Imply(
            And(
                GreaterV('$i', '$j'),
                Atom('NextRow', '$i', '$i_next'),
                Given('$i_next', '$j', '$v2'),
                Atom('Less', '$v2', '$v1')
            ),
            Val('$i', '$j', '$v1')
        ))

        # Reverse GreaterV (Up > Down)
        # The lower cell is v2 if the upper cell is v1, and v2 < v1
        self.horn_rules.append(Imply(
            And(
                Atom('NextRow', '$i_prev', '$i'),
                GreaterV('$i_prev', '$j'),
                Given('$i_prev', '$j', '$v1'),
                Atom('Less', '$v2', '$v1')
            ),
            Val('$i', '$j', '$v2')
        ))

        # Fall back: guess based on domain
        # cell value can be V if V is a valid num in domain
        self.horn_rules.append(Imply(
            Atom('InDomain', '$v'),
            Val('$i', '$j', '$v')
        ))
   
# -------------- TESTING -----------     
if __name__ == "__main__":
    try:
        riddle = problem.futoshiki.Futoshiki("input-01")
        print(f"Successfully loaded a {riddle.size}x{riddle.size} puzzle.")
    except Exception as e:
        print(f"Failed to load puzzle: {e}")
        exit()

    print("Init Knowledge Base and generating rules...")
    kb = KnowledgeBase(riddle)

    print("\n--- OBSERVED FACTS ---")
    print(f"Total facts loaded: {len(kb.obs_facts)}")
    for fact in kb.obs_facts:
        print(f"  {fact}")

    print("\n--- GROUND KNOWLEDGE BASE ---")
    print(f"Total propositional rules generated: {len(kb.ground_rules)}")
    
    print("first 5 rules:")
    for rule in kb.ground_rules[:5]:
        print(f"  {rule}")
        
    print("\nlast 5 rules:")
    for rule in kb.ground_rules[-5:]:
        print(f"  {rule}")