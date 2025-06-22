# parser.py

from tokens import TOKEN_TYPES
from astt import *
from lexer import Lexer  # Only for test case at bottom

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]

    def expect(self, token_type):
        if self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")
        self.advance()
    
    def skip_newlines(self):
        while self.current_token.type == TOKEN_TYPES['NEWLINE']:
            self.advance()

    def parse(self):
        statements = []
        while self.current_token.type != TOKEN_TYPES['EOF']:
            self.skip_newlines()  
            if self.current_token.type == TOKEN_TYPES['EOF']:
                break
            if self.current_token.type == TOKEN_TYPES['NUMBER']:
                line_number = int(self.current_token.value)
                self.advance()
                stmt = self.parse_statement()
                statements.append(LabeledStatement(line_number, stmt))
            else:
                raise SyntaxError(f"Expected line number, got: {self.current_token}")
        return Program(statements)

    def parse_statement(self):
        token = self.current_token
        if token.type == TOKEN_TYPES['LET']:
            return self.parse_let()
        elif token.type == TOKEN_TYPES['PRINT']:
            return self.parse_print()
        elif token.type == TOKEN_TYPES['IF']:
            return self.parse_if()
        elif token.type == TOKEN_TYPES['FOR']:
            return self.parse_for()
        elif token.type == TOKEN_TYPES['NEXT']:
            return self.parse_next()
        elif token.type == TOKEN_TYPES['INPUT']:
            return self.parse_input()
        elif token.type == TOKEN_TYPES['GOTO']:
            return self.parse_goto()
        elif token.type == TOKEN_TYPES['GOSUB']:
            return self.parse_gosub()
        elif token.type == TOKEN_TYPES['RETURN']:
            self.advance()
            return ReturnStatement()
        elif token.type == TOKEN_TYPES['REM']:
            comment = token.value
            self.advance()
            return RemStatement(comment)
        elif token.type == TOKEN_TYPES['END']:
            self.advance()
            return EndStatement()
        else:
            raise SyntaxError(f"Unknown statement starting with: {token}")

    def parse_let(self):
        self.expect(TOKEN_TYPES['LET'])
        var = Variable(self.current_token.value)
        self.expect(TOKEN_TYPES['IDENTIFIER'])
        self.expect(TOKEN_TYPES['EQ'])
        expr = self.parse_expression()
        return LetStatement(var, expr)

    def parse_print(self):
        self.expect(TOKEN_TYPES['PRINT'])
        if self.current_token.type == TOKEN_TYPES['STRING']:
            string = String(self.current_token.value)
            self.advance()
            return PrintStatement(string)
        else:
            expr = self.parse_expression()
            return PrintStatement(expr)

    def parse_input(self):
        self.expect(TOKEN_TYPES['INPUT'])
        var = Variable(self.current_token.value)
        self.expect(TOKEN_TYPES['IDENTIFIER'])
        return InputStatement(var)

    def parse_if(self):
        self.expect(TOKEN_TYPES['IF'])
        condition = self.parse_expression()
        self.expect(TOKEN_TYPES['THEN'])
        then_branch = self.parse_statement()
        else_branch = None
        if self.current_token.type == TOKEN_TYPES['ELSE']:
            self.advance()
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch)

    def parse_for(self):
        self.expect(TOKEN_TYPES['FOR'])
        var = Variable(self.current_token.value)
        self.expect(TOKEN_TYPES['IDENTIFIER'])
        self.expect(TOKEN_TYPES['EQ'])
        start = self.parse_expression()
        self.expect(TOKEN_TYPES['TO'])
        end = self.parse_expression()
        step = Number(1)
        if self.current_token.type == TOKEN_TYPES['STEP']:
            self.advance()
            step = self.parse_expression()

        body = []
        while True:
            self.skip_newlines()
            if self.current_token.type == TOKEN_TYPES['EOF']:
                raise SyntaxError("Unexpected end of input inside FOR loop")

            if self.current_token.type == TOKEN_TYPES['NUMBER']:
                line_number = int(self.current_token.value)
                self.advance()
                stmt = self.parse_statement()

                if isinstance(stmt, NextStatement) and stmt.var.name == var.name:
                    break
                else:
                    body.append(stmt)
            else:
                raise SyntaxError("Expected line number inside FOR loop")

        return ForStatement(var, start, end, step, body)

    def parse_next(self):
        self.expect(TOKEN_TYPES['NEXT'])
        var = Variable(self.current_token.value)
        self.expect(TOKEN_TYPES['IDENTIFIER'])
        return NextStatement(var)

    def parse_goto(self):
        self.expect(TOKEN_TYPES['GOTO'])
        line = int(self.current_token.value)
        self.expect(TOKEN_TYPES['NUMBER'])
        return GotoStatement(line)

    def parse_gosub(self):
        self.expect(TOKEN_TYPES['GOSUB'])
        line = int(self.current_token.value)
        self.expect(TOKEN_TYPES['NUMBER'])
        return GosubStatement(line)

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_term()
        while self.current_token.type in (TOKEN_TYPES['EQ'], TOKEN_TYPES['NEQ'],
                                          TOKEN_TYPES['LT'], TOKEN_TYPES['LE'],
                                          TOKEN_TYPES['GT'], TOKEN_TYPES['GE']):
            op = self.current_token.type
            self.advance()
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token.type in (TOKEN_TYPES['PLUS'], TOKEN_TYPES['MINUS']):
            op = self.current_token.type
            self.advance()
            right = self.parse_factor()
            left = BinaryOp(left, op, right)
        return left

    def parse_factor(self):
        left = self.parse_atom()
        while self.current_token.type in (TOKEN_TYPES['MUL'], TOKEN_TYPES['DIV']):
            op = self.current_token.type
            self.advance()
            right = self.parse_atom()
            left = BinaryOp(left, op, right)
        return left

    def parse_atom(self):
        token = self.current_token
        if token.type == TOKEN_TYPES['NUMBER']:
            self.advance()
            return Number(int(token.value))
        elif token.type == TOKEN_TYPES['STRING']:
            self.advance()
            return String(token.value)
        elif token.type == TOKEN_TYPES['IDENTIFIER']:
            self.advance()
            return Variable(token.value)
        elif token.type == TOKEN_TYPES['LPAREN']:
            self.advance()
            expr = self.parse_expression()
            self.expect(TOKEN_TYPES['RPAREN'])
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")

# ✅ TEST CASE
# if __name__ == "__main__":
#     code = '''10 LET A = 5
# 20 LET B = 10
# 30 LET C = A + B
# 40 IF C > 10 THEN PRINT "Bigger" ELSE PRINT "Smaller"
# 50 FOR I = 1 TO 10 STEP 1
# 60 NEXT I
# 70 REM This is a comment
# 80 END'''
#     lexer = Lexer(code)
#     tokens = lexer.tokenize()
#     parser = Parser(tokens)
#     program = parser.parse()
#     print(program)
