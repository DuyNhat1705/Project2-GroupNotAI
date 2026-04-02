from py_compile import main

from problem.futoshiki import Futoshiki

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

class Variable(Term):
    def __init__(self, name):
        self.name = name # syntax: $var_name
    def __str__(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    def __hash__(self):
        return hash(self.name) # required due to __eq__

class Constant(Term):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Atom(Formula):
    def __init__(self, name, *args):
        self.name = name
        self.args = [Variable(p) if isinstance(p, str) and p.startswith('$')
                     else Constant(p) if isinstance(p, (int, str)) and not isinstance(p, Expression)
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
        if x.startswith('$'): return Variable(x)
        return Constant(x)
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

class Implies(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return f"({self.left} => {self.right})"

class Exists(Formula):
    def __init__(self, var, clause):
        self.var = Variable(var) if isinstance(var, str) else str(var)
        self.body = clause
    def __str__(self):
        return 'EXISTS(' + str(self.var) + ',' + str(self.body) + ')'

class Forall(Formula):
    def __init__(self, var, clause):
        self.var = Variable(var) if isinstance(var, str) else str(var)
        self.body = clause
    def __str__(self):
        return 'FORALL(' + str(self.var) + ',' + str(self.body) + ')'

def unify(x, y, theta):
    if theta is None:
        return None
    elif x == y:
        return theta
    
    # if x or y is a var: unify the var with other term
    elif isinstance(x, Variable):
        return unify_var(x, y, theta)
    elif isinstance(y, Variable):
        return unify_var(y, x, theta)
    
    elif isinstance(x, Atom) and isinstance(y, Atom):
        # match predicate names 
        # recursively match args
        return unify(x.args, y.args, unify(x.name, y.name, theta))
    elif isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y): return None
        if not x: return theta
        return unify(x[1:], y[1:], unify(x[0], y[0], theta))
    else:
        return None

def unify_var(var, x, theta):
    if var.name in theta:
        return unify(theta[var.name], x, theta)
    elif isinstance(x, Variable) and x.name in theta:
        return unify(var, theta[x.name], theta)
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
        self._gen_axioms()
        self._math_sense()
        self._ground_CNF()
        self._init_facts()
    
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
        
    def _gen_axioms(self):
        # A1 (Every cell has at least one valid value):
        atom_domain = [Val('$i', '$j', v) for v in self.domain]
        A1 = Forall('$i', Forall('$j', Or(*atom_domain)))

        # A2 (Every cell has at most one value):
        A2 = Forall('$i', 
                Forall('j', 
                        (Forall('$v1', 
                                Forall('$v2', 
                                        Implies(And(Val('$i', '$j', '$v1'), Val('$i', '$j', '$v2')),
                                                Eq('$v1', '$v2')))))))
        
        # A3 (Row uniqueness):
        A3 = Forall('$i',
                    Forall('$j1',
                           Forall('$j2',
                                  Forall('$v',
                                         Implies(And(Val('$i', '$j1', '$v'), Val('$i', '$j2', '$v'), Not(Eq('$j1', '$j2'))),
                                                 Bot())))))
        
        
        # A4 (Horizontal less-than constraints):
        A4 = Forall('$i', 
                        Forall('$j', 
                                Forall('$j_next', 
                                        Forall('$v1', 
                                            Forall('$v2', 
                                                Implies(
                                                        And(
                                                            LessH('$i', '$j'),                  
                                                            Atom('NextCol', '$j', '$j_next'),   
                                                            Val('$i', '$j', '$v1'),             
                                                            Val('$i', '$j_next', '$v2')),        
                                                        Atom('Less', '$v1', '$v2')             
                                                    ))))))
        
        
        # A5 (Given clues are enforced):
        A5 = Forall('$i', Forall('$j', Forall('$v', Implies(Given('$i', '$j', '$v'), Val('$i', '$j', '$v'))))) 
        
        # A6 (Column uniqueness):
        A6 = Forall('$j',
                    Forall('$i1',
                           Forall('$i2',
                                  Forall('$v',
                                         Implies(And(Val('$i1', '$j', '$v'), Val('$i2', '$j', '$v'), Not(Eq('$i1', '$i2'))),
                                                 Bot)))))
        
        
        
        # A7 (Vertical less-than constraints):
        A7 = Forall('$i', 
                        Forall('$j', 
                                Forall('$i_next', 
                                        Forall('$v1', 
                                            Forall('$v2', 
                                                Implies(
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
                                                Implies(
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
                                                Implies(
                                                        And(
                                                            GreaterV('$i', '$j'),                  
                                                            Atom('NextRow', '$i', '$i_next'),  
                                                            Val('$i', '$j', '$v1'),            
                                                            Val('$i_next', '$j', '$v2')),         
                                                        Atom('Less', '$v2', '$v1')              
                                                    ))))))
        
        self.axioms = [A1, A2, A3, A4, A5, A6, A7, A8, A9]
              
    def _ground_CNF(self):
        
        self.ground_rules = []

        # Cell Completeness
        for i in self.domain:
            for j in self.domain:
                domain_atoms = [Val(i, j, v) for v in self.domain]
                self.ground_rules.append(Or(*domain_atoms))

        # Cell Uniqueness
        for i in self.domain:
            for j in self.domain:
                for v1 in self.domain:
                    for v2 in self.domain:
                        if v1 < v2: # prevents checking (2,1) if (1,2) checked
                            rule = Implies(And(Val(i, j, v1), Val(i, j, v2)), Bot())
                            self.ground_rules.append(rule)

        # Row Uniqueness
        for i in self.domain:
            for v in self.domain:
                for j1 in self.domain:
                    for j2 in self.domain:
                        if j1 < j2:
                            # Implies(And(Val(1,1,3), Val(1,2,3)), Bot())
                            rule = Implies(And(Val(i, j1, v), Val(i, j2, v)), Bot())
                            self.ground_rules.append(rule)

        # Column Uniqueness
        for j in self.domain:
            for v in self.domain:
                for i1 in self.domain:
                    for i2 in self.domain:
                        if i1 < i2:
                            # Implies(And(Val(1,1,3), Val(2,1,3)), Bot())
                            rule = Implies(And(Val(i1, j, v), Val(i2, j, v)), Bot())
                            self.ground_rules.append(rule)

        # Horizontal Constraints (LessH)
        for i in self.domain:
            for j in range(1, self.riddle.size): # Stops at N-1
                for v1 in self.domain:
                    for v2 in self.domain:
                        if v1 >= v2: # If v1 is not less than v2
                            rule = Implies(
                                And(
                                    LessH(i, j),
                                    Val(i, j, v1),
                                    Val(i, j + 1, v2) 
                                ),
                                Bot() # contradiction found
                            )
                            self.ground_rules.append(rule)

        # Horizontal Constraints (GreaterH)
        for i in self.domain:
            for j in range(1, self.riddle.size):
                for v1 in self.domain:
                    for v2 in self.domain:
                        if v1 <= v2: # If v1 is not greater than v2
                            rule = Implies(
                                And(GreaterH(i, j), Val(i, j, v1), Val(i, j + 1, v2)),
                                Bot() # contradiction found
                            )
                            self.ground_rules.append(rule)

        # Vertical Constraints (LessV)
        for j in self.domain:
            for i in range(1, self.riddle.size):
                for v1 in self.domain:
                    for v2 in self.domain:
                        if v1 >= v2:
                            rule = Implies(
                                And(LessV(i, j), Val(i, j, v1), Val(i + 1, j, v2)),
                                Bot()
                            )
                            self.ground_rules.append(rule)

        # Vertical Constraints (GreaterV)
        for j in self.domain:
            for i in range(1, self.riddle.size):
                for v1 in self.domain:
                    for v2 in self.domain:
                        if v1 <= v2:
                            rule = Implies(
                                And(GreaterV(i, j), Val(i, j, v1), Val(i + 1, j, v2)),
                                Bot()
                            )
                            self.ground_rules.append(rule)
        
    def _init_facts(self):
        """
        Grid and constraints from Futoshiki instance => Observed facts
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
   
# -------------- TESTING -----------     
if __name__ == "__main__":
    print("Loading puzzle...")
    try:
        riddle = Futoshiki("input-01")
        print(f"Successfully loaded a {riddle.size}x{riddle.size} puzzle.")
    except Exception as e:
        print(f"Failed to load puzzle: {e}")
        exit()

    print("Initializing Knowledge Base and generating rules...")
    kb = KnowledgeBase(riddle)

    print("\n--- OBSERVED FACTS ---")
    print(f"Total facts loaded: {len(kb.obs_facts)}")
    for fact in kb.obs_facts:
        print(f"  {fact}")

    print("\n--- GROUND KNOWLEDGE BASE ---")
    print(f"Total propositional rules generated: {len(kb.ground_rules)}")
    
    print("Sample of the first 5 rules:")
    for rule in kb.ground_rules[:5]:
        print(f"  {rule}")
        
    print("\nSample of the last 5 rules (Inequalities):")
    for rule in kb.ground_rules[-5:]:
        print(f"  {rule}")

