# lexer.py

import re
from tokens import TOKEN_TYPES

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.position = 0
        self.length = len(source_code)

    def tokenize(self):
        patterns = [
            # Order matters: multi-char operators first
            ('NEQ',       r'<>'),
            ('LE',        r'<='),
            ('GE',        r'>='),

            # Literals
            ('NUMBER',    r'\d+'),
            ('STRING',    r'"[^"]*"'),

            # Keywords
            ('LET',       r'LET'),
            ('PRINT',     r'PRINT'),
            ('INPUT',     r'INPUT'),
            ('IF',        r'IF'),
            ('THEN',      r'THEN'),
            ('ELSE',      r'ELSE'),
            ('FOR',       r'FOR'),
            ('TO',        r'TO'),
            ('STEP',      r'STEP'),
            ('NEXT',      r'NEXT'),
            ('GOTO',      r'GOTO'),
            ('GOSUB',     r'GOSUB'),
            ('RETURN',    r'RETURN'),
            ('REM',       r'REM.*'),  # Must go before IDENTIFIER
            ('END',       r'END'),

            # Identifiers
            ('IDENTIFIER', r'[A-Z][A-Z0-9]*'),

            # Operators
            ('EQ',        r'='),
            ('PLUS',      r'\+'),
            ('MINUS',     r'-'),
            ('MUL',       r'\*'),
            ('DIV',       r'/'),
            ('GT',        r'>'),
            ('LT',        r'<'),

            # Symbols
            ('LPAREN',    r'\('),
            ('RPAREN',    r'\)'),
            ('COLON',     r':'),
            ('COMMA',     r','),

            # Other
            ('NEWLINE',   r'\n'),
            ('SKIP',      r'[ \t]+'),
            ('MISMATCH',  r'.'),  # Must be last
        ]

        pos = 0
        while pos < self.length:
            match = None
            for token_type, pattern in patterns:
                regex = re.compile(pattern)
                match = regex.match(self.source, pos)
                if match:
                    value = match.group(0)

                    # Skip spaces/tabs
                    if token_type == 'SKIP':
                        pos = match.end()
                        break

                    # Skip comments (REM)
                    if token_type == 'REM':
                        self.tokens.append(Token(TOKEN_TYPES[token_type], value.strip()))
                        newline_pos = self.source.find('\n', pos)
                        if newline_pos == -1:
                            pos = self.length
                        else:
                            pos = newline_pos + 1
                        break

                    # Handle string literals
                    if token_type == 'STRING':
                        value = value[1:-1]  # remove quotes

                    if token_type in TOKEN_TYPES:
                        self.tokens.append(Token(TOKEN_TYPES[token_type], value))
                    else:
                        raise ValueError(f"Unknown token type '{token_type}'")

                    pos = match.end()
                    break

            if not match:
                raise SyntaxError(f"Unexpected character '{self.source[pos]}' at position {pos}")
        
        self.tokens.append(Token(TOKEN_TYPES['EOF'], None))
        return self.tokens

# ✅ Test Run
# if __name__ == "__main__":
#     code = '''
#     10 LET A = 5
#     20 LET B = 10
#     30 LET C = A + B
#     40 IF C > 10 THEN PRINT "Bigger" ELSE PRINT "Smaller"
#     50 FOR I = 1 TO 10 STEP 1
#     60 NEXT I
#     70 REM This is a comment
#     80 END
#     '''
#     lexer = Lexer(code)
#     tokens = lexer.tokenize()
#     for token in tokens:
#         print(token)
