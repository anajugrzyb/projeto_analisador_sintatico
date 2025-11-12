from lexical.scanner import Scanner
from lexical.token import TokenType, Token

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.current = None
        self.errors = []
        self._advance()

    def _advance(self):
        self.current = self.scanner.next_token()

    def _check(self, *types):
        return self.current is not None and self.current.type in types

    def _check_kw(self, *kws):
        return self.current is not None and self.current.type == TokenType.RESERVED and self.current.value in kws

    def _match(self, *types):
        if self._check(*types):
            t = self.current
            self._advance()
            return t
        return None

    def _match_kw(self, *kws):
        if self._check_kw(*kws):
            t = self.current
            self._advance()
            return t
        return None

    def _consume(self, ttype, msg):
        if self._check(ttype):
            t = self.current
            self._advance()
            return t
        self._error_here(msg)
        raise ParseError()

    def _consume_kw(self, kw, msg):
        if self._check_kw(kw):
            t = self.current
            self._advance()
            return t
        self._error_here(msg)
        raise ParseError()

    def _error_here(self, message):
        if self.current is None:
            self.errors.append(f"[EOF] Erro sintático: {message}")
        else:
            self.errors.append(f"[linha {self.current.line}, col {self.current.column}] Erro sintático perto de '{self.current.value}': {message}")

    def _synchronize(self):
        while self.current is not None:
            if self._match(TokenType.SEMICOLON):
                return
            if self._check_kw("if", "while", "print", "input", "var"):
                return
            if self._check(TokenType.RBRACE):
                return
            self._advance()

    def parse(self):
        try:
            self.programa()
            if self.current is not None:
                self._error_here("tokens após o fechamento de 'main'.")
        except ParseError:
            self._synchronize()
        return self.errors

    def programa(self):
        self._consume_kw("main", "esperado 'main' no início do programa")
        self._consume(TokenType.LBRACE, "esperado '{' após 'main'")
        self.corpo()
        self._consume(TokenType.RBRACE, "esperado '}' ao final do programa")

    def corpo(self):
        self.secaoDeclaracoes()
        self.listaComandos()

    def secaoDeclaracoes(self):
        self._consume_kw("var", "esperado 'var' no início da seção de declarações")
        self._consume(TokenType.LBRACE, "esperado '{' após 'var'")
        self.listaDeclaracoes()
        self._consume(TokenType.RBRACE, "esperado '}' ao final da seção 'var'")

    def listaDeclaracoes(self):
        self.declaracao()
        while self._check(TokenType.IDENTIFIER):
            self.declaracao()

    def declaracao(self):
        self._consume(TokenType.IDENTIFIER, "esperado identificador na declaração")
        self._consume(TokenType.COLON, "esperado ':' após identificador")
        self.tipo()
        self._consume(TokenType.SEMICOLON, "esperado ';' ao final da declaração")

    def tipo(self):
        if not self._match_kw("int", "real"):
            self._error_here("esperado tipo 'int' ou 'real'")
            raise ParseError()

    def listaComandos(self):
        self.comando()
        while self._check(TokenType.LBRACE) or self._check(TokenType.IDENTIFIER) or self._check_kw("input", "print", "if", "while"):
            self.comando()

    def comando(self):
        try:
            if self._check(TokenType.IDENTIFIER):
                self.atribuicao()
            elif self._check_kw("input"):
                self.leitura()
            elif self._check_kw("print"):
                self.escrita()
            elif self._check_kw("if"):
                self.condicional()
            elif self._check_kw("while"):
                self.repeticao()
            elif self._check(TokenType.LBRACE):
                self.bloco()
            else:
                self._error_here("comando inválido")
                raise ParseError()
        except ParseError:
            self._synchronize()

    def atribuicao(self):
        self._consume(TokenType.IDENTIFIER, "esperado identificador na atribuição")
        self._consume(TokenType.ASSIGN_LEFT, "esperado '<-' após identificador")
        self.expressaoAritmetica()
        self._consume(TokenType.SEMICOLON, "esperado ';' ao final da atribuição")

    def leitura(self):
        self._consume_kw("input", "esperado 'input'")
        self._consume(TokenType.LPAREN, "esperado '(' após 'input'")
        self._consume(TokenType.IDENTIFIER, "esperado identificador dentro de input(...)")
        self._consume(TokenType.RPAREN, "esperado ')' após input(...)")
        self._consume(TokenType.SEMICOLON, "esperado ';' ao final de input(...)")

    def escrita(self):
        self._consume_kw("print", "esperado 'print'")
        self._consume(TokenType.LPAREN, "esperado '(' após 'print'")
        if not (self._match(TokenType.IDENTIFIER) or self._match(TokenType.STRING)):
            self._error_here("esperado identificador ou cadeia de caracteres em print(...)")
            raise ParseError()
        self._consume(TokenType.RPAREN, "esperado ')' após print(...)")
        self._consume(TokenType.SEMICOLON, "esperado ';' ao final de print(...)")

    def condicional(self):
        self._consume_kw("if", "esperado 'if'")
        self.expressaoRelacional()
        self._consume_kw("then", "esperado 'then' após condição do if")
        self.comando()
        if self._match_kw("else"):
            self.comando()

    def repeticao(self):
        self._consume_kw("while", "esperado 'while'")
        self.expressaoRelacional()
        self.comando()

    def bloco(self):
        self._consume(TokenType.LBRACE, "esperado '{' para iniciar bloco")
        self.listaComandos()
        self._consume(TokenType.RBRACE, "esperado '}' para finalizar bloco")

    def expressaoAritmetica(self):
        self.termo()
        while self._check(TokenType.MATH_OPERATOR) and self.current.value in {"+", "-"}:
            self._advance()
            self.termo()

    def termo(self):
        self.fator()
        while self._check(TokenType.MATH_OPERATOR) and self.current.value in {"*", "/"}:
            self._advance()
            self.fator()

    def fator(self):
        if self._match(TokenType.NUMINT) or self._match(TokenType.NUMREAL):
            return
        if self._check(TokenType.IDENTIFIER):
            self._advance()
            if self._match(TokenType.INCREMENT) or self._match(TokenType.DECREMENT):
                return
            return
        if self._match(TokenType.LPAREN):
            self.expressaoAritmetica()
            self._consume(TokenType.RPAREN, "esperado ')' após expressão")
            return
        self._error_here("esperado fator (número, identificador ou '(expr)')")
        raise ParseError()

    def expressaoRelacional(self):
        self.termoRelacional()
        while self._check_kw("E", "OU"):
            self._advance()
            self.termoRelacional()

    def termoRelacional(self):
        if self._match_kw("NAO"):
            self.termoRelacional()
            return
        if self._match(TokenType.LPAREN):
            self.expressaoRelacional()
            self._consume(TokenType.RPAREN, "esperado ')' após expressão relacional")
            return
        self.expressaoAritmetica()
        if not self._match(TokenType.REL_OPERATOR):
            self._error_here("esperado operador relacional (>, <, >=, <=, ==, !=)")
            raise ParseError()
        self.expressaoAritmetica()
