# astt.py

# ---------- Base Node ----------

class ASTNode:
    pass

# ---------- Expression Nodes ----------

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"

class String(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String({repr(self.value)})"

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # Token type: +, -, *, /, >, <, etc.
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"

# ---------- Statement Nodes ----------

class LetStatement(ASTNode):
    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr

    def __repr__(self):
        return f"Let({self.variable} = {self.expr})"

class PrintStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"

class InputStatement(ASTNode):
    def __init__(self, variable):
        self.variable = variable

    def __repr__(self):
        return f"Input({self.variable})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"If({self.condition}, Then={self.then_branch}, Else={self.else_branch})"

class ForStatement(ASTNode):
    def __init__(self, var, start, end, step, body=None):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body or []

    def __repr__(self):
        return f"For({self.var} = {self.start} TO {self.end} STEP {self.step}, Body={self.body})"

class NextStatement(ASTNode):
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        return f"Next({self.var})"

class GotoStatement(ASTNode):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return f"Goto({self.target})"

class GosubStatement(ASTNode):
    def __init__(self, target):
        self.target = target

    def __repr__(self):
        return f"Gosub({self.target})"

class ReturnStatement(ASTNode):
    def __repr__(self):
        return "Return()"

class EndStatement(ASTNode):
    def __repr__(self):
        return "End()"

class RemStatement(ASTNode):
    def __init__(self, comment):
        self.comment = comment

    def __repr__(self):
        return f"REM({self.comment})"

# ---------- Program and Line ----------

class LabeledStatement(ASTNode):
    def __init__(self, number, statement):
        self.number = number  # line number like 10, 20, etc.
        self.statement = statement

    def __repr__(self):
        return f"{self.number}: {self.statement}"

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return "\n".join(str(stmt) for stmt in self.statements)

# ---------- TEST CASE (AST generation manually) ----------

# if __name__ == "__main__":
#     prog = Program([
#         LabeledStatement(10, LetStatement(Variable("A"), Number(5))),
#         LabeledStatement(20, LetStatement(Variable("B"), Number(10))),
#         LabeledStatement(30, LetStatement(Variable("C"), BinaryOp(Variable("A"), "+", Variable("B")))),
#         LabeledStatement(40, IfStatement(
#             BinaryOp(Variable("C"), ">", Number(10)),
#             PrintStatement(String("Bigger")),
#             PrintStatement(String("Smaller"))
#         )),
#         LabeledStatement(50, ForStatement(Variable("I"), Number(1), Number(10), Number(1))),
#         LabeledStatement(60, NextStatement(Variable("I"))),
#         LabeledStatement(70, RemStatement("This is a comment")),
#         LabeledStatement(80, EndStatement())
#     ])
#     print(prog)
