def h_symbol(c):
    return '<' if c == 1 else ('>' if c == -1 else '&nbsp;')

def v_symbol(c):
    return '∧' if c == 1 else ('∨' if c == -1 else '&nbsp;')  

def count_constraints(puzzle):
    t = sum(1 for row in puzzle.HorizontalConstraints for c in row if c != 0)
    t += sum(1 for row in puzzle.VerticalConstraints for c in row if c != 0)
    return t

def count_given(puzzle):
    return sum(1 for row in puzzle.grid for v in row if v != 0)