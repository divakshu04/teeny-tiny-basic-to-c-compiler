# tokens.py

# Token types (strings for easy pattern matching and debugging)
TOKEN_TYPES = {
    # Keywords
    'PRINT': 'PRINT',
    'LET': 'LET',
    'IF': 'IF',
    'THEN': 'THEN',
    'ELSE': 'ELSE',
    'ENDIF': 'ENDIF',
    'GOTO': 'GOTO',
    'GOSUB': 'GOSUB',
    'RETURN': 'RETURN',
    'FOR': 'FOR',
    'TO': 'TO',
    'STEP': 'STEP',
    'NEXT': 'NEXT',
    'INPUT': 'INPUT',
    'REM': 'REM',  # Comment
    'END': 'END',

    # Operators
    'PLUS': '+',
    'MINUS': '-',
    'MUL': '*',
    'DIV': '/',
    'EQ': '=',
    'NEQ': '<>',
    'LT': '<',
    'GT': '>',
    'LE': '<=',
    'GE': '>=',

    # Symbols
    'LPAREN': '(',
    'RPAREN': ')',
    'COLON': ':',
    'COMMA': ',',

    # Other token types
    'NUMBER': 'NUMBER',
    'STRING': 'STRING',
    'IDENTIFIER': 'IDENTIFIER',
    'NEWLINE': 'NEWLINE',
    'EOF': 'EOF',
}
