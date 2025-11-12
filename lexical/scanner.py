from lexical.token import Token, TokenType

class Scanner:
    KEYWORDS = {
        "main", "var", "int", "real", "if", "then", "else",
        "while", "print", "input", "E", "OU", "NAO"
    }

    def __init__(self, filename: str):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.source_code = list(f.read())
            self.pos = 0
            self.line = 1
            self.column = 1
            self.state = 0
        except FileNotFoundError:
            print(f"Erro: arquivo '{filename}' não encontrado.")
            self.source_code = []
            self.pos = 0
            self.line = 1
            self.column = 1
            self.state = 0

    def next_token(self):
        content = ""
        self.state = 0
        while not self.is_eof():
            current_char = self.source_code[self.pos]
            start_line = self.line
            start_column = self.column
            self.next_char()
            match self.state:
                case 0:
                    if self.is_letter(current_char):
                        content += current_char
                        self.state = 1
                    elif self.is_digit(current_char):
                        content += current_char
                        self.state = 3
                    elif current_char == ".":
                        content += current_char
                        self.state = 4
                    elif current_char == '"':
                        lex = []
                        while not self.is_eof():
                            p = self.next_char()
                            if p == '"':
                                return Token(TokenType.STRING, "".join(lex), start_line, start_column)
                            if p == "\n" or p == "":
                                return Token(TokenType.ERROR, "string não fechada", start_line, start_column)
                            lex.append(p)
                    elif self.is_math_operator(current_char):
                        if current_char == "+" and self.peek() == "+":
                            self.next_char()
                            return Token(TokenType.INCREMENT, "++", start_line, start_column)
                        if current_char == "-" and self.peek() == "-":
                            self.next_char()
                            return Token(TokenType.DECREMENT, "--", start_line, start_column)
                        return Token(TokenType.MATH_OPERATOR, current_char, start_line, start_column)
                    elif current_char == "<":
                        if self.peek() == "-":
                            self.next_char()
                            return Token(TokenType.ASSIGN_LEFT, "<-", start_line, start_column)
                        if self.peek() == "=":
                            self.next_char()
                            return Token(TokenType.REL_OPERATOR, "<=", start_line, start_column)
                        return Token(TokenType.REL_OPERATOR, "<", start_line, start_column)
                    elif current_char == "=":
                        if self.peek() == "=":
                            self.next_char()
                            return Token(TokenType.REL_OPERATOR, "==", start_line, start_column)
                        return Token(TokenType.ASSIGNMENT, "=", start_line, start_column)
                    elif current_char == ">":
                        if self.peek() == "=":
                            self.next_char()
                            return Token(TokenType.REL_OPERATOR, ">=", start_line, start_column)
                        return Token(TokenType.REL_OPERATOR, ">", start_line, start_column)
                    elif current_char == "!":
                        if self.peek() == "=":
                            self.next_char()
                            return Token(TokenType.REL_OPERATOR, "!=", start_line, start_column)
                        return Token(TokenType.ERROR, "!", start_line, start_column)
                    elif current_char == "(":
                        return Token(TokenType.LPAREN, current_char, start_line, start_column)
                    elif current_char == ")":
                        return Token(TokenType.RPAREN, current_char, start_line, start_column)
                    elif current_char == "{":
                        return Token(TokenType.LBRACE, current_char, start_line, start_column)
                    elif current_char == "}":
                        return Token(TokenType.RBRACE, current_char, start_line, start_column)
                    elif current_char == ":":
                        return Token(TokenType.COLON, current_char, start_line, start_column)
                    elif current_char == ";":
                        return Token(TokenType.SEMICOLON, current_char, start_line, start_column)
                    elif current_char == ",":
                        return Token(TokenType.COMMA, current_char, start_line, start_column)
                    elif current_char == "#":
                        self.skip_line_comment()
                        continue
                    elif current_char.isspace():
                        continue
                    else:
                        return Token(TokenType.ERROR, current_char, start_line, start_column)
                case 1:
                    if self.is_letter(current_char) or self.is_digit(current_char):
                        content += current_char
                    else:
                        self.back()
                        self.state = 0
                        if content in self.KEYWORDS:
                            return Token(TokenType.RESERVED, content, start_line, start_column)
                        else:
                            return Token(TokenType.IDENTIFIER, content, start_line, start_column)
                case 3:
                    if self.is_digit(current_char):
                        content += current_char
                    elif current_char == ".":
                        content += current_char
                        self.state = 4
                    else:
                        self.back()
                        self.state = 0
                        return Token(TokenType.NUMINT, content, start_line, start_column)
                case 4:
                    if self.is_digit(current_char):
                        content += current_char
                    else:
                        if content[-1] == ".":
                            return Token(TokenType.ERROR, content, start_line, start_column)
                        self.back()
                        self.state = 0
                        return Token(TokenType.NUMREAL, content, start_line, start_column)
        return None

    def is_letter(self, c: str) -> bool:
        return c.isalpha() or c == "_"

    def is_digit(self, c: str) -> bool:
        return c.isdigit()

    def is_math_operator(self, c: str) -> bool:
        return c in "+-*/"

    def next_char(self) -> str:
        if self.is_eof():
            return ""
        ch = self.source_code[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def peek(self) -> str:
        if self.pos < len(self.source_code):
            return self.source_code[self.pos]
        return ""

    def back(self):
        self.pos -= 1
        self.column -= 1

    def is_eof(self) -> bool:
        return self.pos >= len(self.source_code)

    def skip_line_comment(self):
        while not self.is_eof() and self.source_code[self.pos] != "\n":
            self.next_char()


