from parser import Parser
from lexer import Lexer
from astt import *

class CodeGenerator:
    def __init__(self):
        self.output = []
        self.variables = set()
        self.return_stack_used = False
        self.used_labels = set()
        self.goto_targets = set()
        self.return_targets = set()
        self.label_required = set()

    def emit(self, line):
        self.output.append("    " + line)

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node):
        # Collect all jump targets first
        for labeled in node.statements:
            stmt = labeled.statement
            if isinstance(stmt, GotoStatement):
                self.goto_targets.add(stmt.target)
            elif isinstance(stmt, GosubStatement):
                self.return_stack_used = True
                self.goto_targets.add(stmt.target)
                self.return_targets.add(labeled.number + 10)
            elif isinstance(stmt, ReturnStatement):
                self.return_stack_used = True

        self.label_required = self.goto_targets.union(self.return_targets)

        # Start generating code
        self.output = ["#include <stdio.h>", ""]
        if self.return_stack_used:
            self.output.append("int return_stack[100];")
            self.output.append("int sp = -1;")

        self.output.append("int main() {")

        # Generate statements
        for labeled in node.statements:
            number = labeled.number
            stmt = labeled.statement
            if number in self.label_required:
                self.output.append(f"label_{number}:")
            self.visit(stmt)

        if self.variables:
            decl_line = f"int {', '.join(sorted(self.variables))};"
            insert_index = self.output.index("int main() {") + 1
            self.output.insert(insert_index, decl_line)

        self.emit("return 0;")
        self.output.append("}")
        return "\n".join(self.output)

    def visit_LetStatement(self, node):
        var = node.variable.name
        self.variables.add(var)
        expr = self.visit(node.expr)
        self.emit(f"{var} = {expr};")

    def visit_Number(self, node):
        return str(node.value)

    def visit_String(self, node):
        return f'\"{node.value}\"'

    def visit_Variable(self, node):
        self.variables.add(node.name)
        return node.name

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_map = {
            'PLUS': '+', 'MINUS': '-', 'MUL': '*', 'DIV': '/',
            'EQ': '==', 'NEQ': '!=', 'LT': '<', 'LE': '<=',
            'GT': '>', 'GE': '>='
        }
        op = op_map.get(node.op, node.op)
        return f"({left} {op} {right})"

    def visit_PrintStatement(self, node):
        expr = self.visit(node.expr)
        if isinstance(node.expr, String):
            self.emit(f'printf({expr});')
        else:
            self.emit(f'printf("%d\\n", {expr});')

    def visit_InputStatement(self, node):
        var = node.variable.name
        self.variables.add(var)
        self.emit(f'scanf("%d", &{var});')

    def visit_IfStatement(self, node):
        cond = self.visit(node.condition)
        self.emit(f"if ({cond}) {{")
        self.visit(node.then_branch)
        self.emit("}")
        if node.else_branch:
            self.emit("else {")
            self.visit(node.else_branch)
            self.emit("}")

    def visit_ForStatement(self, node):
        var = node.var.name
        self.variables.add(var)
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step)
        self.emit(f"for ({var} = {start}; {var} <= {end}; {var} += {step}) {{")
        for stmt in node.body:
            self.visit(stmt)
        self.emit("}")

    def visit_NextStatement(self, node):
        pass  

    def visit_GotoStatement(self, node):
        self.emit(f"goto label_{node.target};")

    def visit_GosubStatement(self, node):
        self.emit(f"return_stack[++sp] = {node.target + 10};")
        self.emit(f"goto label_{node.target};")

    def visit_ReturnStatement(self, node):
        self.emit("switch (return_stack[sp--]) {")
        for label in sorted(self.return_targets):
            self.emit(f"  case {label}: goto label_{label};")
        self.emit("}")

    def visit_RemStatement(self, node):
        self.emit(f"// {node.comment}")

    def visit_EndStatement(self, node):
        self.emit("return 0;")

# === Example test code ===
# code = '''10 REM Fibonacci Series in BASIC
# 20 PRINT "Enter number of terms:"
# 21 INPUT N
# 30 LET A = 0
# 40 LET B = 1
# 50 PRINT "Fibonacci Series:"
# 60 FOR I = 1 TO N STEP 1
# 70   PRINT A
# 80   LET TEMP = A + B
# 90   LET A = B
# 100  LET B = TEMP
# 110 NEXT I
# 120 END'''

# lexer = Lexer(code)
# tokens = lexer.tokenize()
# print("\n--- Token stream ---")
# for tok in tokens:
#     print(tok)

# parser = Parser(tokens)
# ast = parser.parse()
# print("\n--- AST ---")
# for stmt in ast.statements:
#     print(stmt)

# print("\nGenerated C Code:\n")
# generator = CodeGenerator()
# c_code = generator.visit(ast)
# print(c_code)