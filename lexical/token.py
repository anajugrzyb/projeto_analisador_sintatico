class TokenType:
    IDENTIFIER = "IDENTIFIER"
    NUMINT = "NUMINT"
    NUMREAL = "NUMREAL"
    RESERVED = "RESERVED"
    STRING = "STRING"
    MATH_OPERATOR = "MATH_OPERATOR"
    REL_OPERATOR = "REL_OPERATOR"
    ASSIGNMENT = "ASSIGNMENT"
    ASSIGN_LEFT = "ASSIGN_LEFT"
    INCREMENT = "INCREMENT"
    DECREMENT = "DECREMENT"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    ERROR = "ERROR"

class Token:
    def __init__(self, type_, value, line=None, column=None):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        if self.type == TokenType.ERROR and self.line is not None and self.column is not None:
            return f"<{self.type}, {self.value}, line={self.line}, col={self.column}>"
        else:
            return f"<{self.type}, {self.value}>"



