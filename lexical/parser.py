from typing import Optional

from lexical.scanner import Scanner
from lexical.token import TokenType, Token
from lexical.syntax_tree import SyntaxNode

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.current = None
        self.errors = []
        self.root: Optional[SyntaxNode] = None
        self._advance()

    def _advance(self):
        self.current = self.scanner.next_token()

    def _check(self, *types):
        return self.current is not None and self.current.type in types

    def _check_kw(self, *kws):
        return self.current is not None and self.current.type == TokenType.RESERVED and self.current.value in kws

    def _token_node(self, token: Token, label: str | None = None) -> SyntaxNode:
        if label is None:
            if token.type == TokenType.RESERVED:
                label = str(token.value)
            else:
                label = token.type
        return SyntaxNode(label, token=token)

    def _match(self, *types, capture: bool = True, label: str | None = None):
        if self._check(*types):
            t = self.current
            self._advance()
            if capture:
                return self._token_node(t, label=label)
            return t
        return None

    def _match_kw(self, *kws, capture: bool = True, label: str | None = None):
        if self._check_kw(*kws):
            t = self.current
            self._advance()
            if capture:
                return self._token_node(t, label=label or str(t.value))
            return t
        return None

    def _consume(self, ttype, msg, label: str | None = None):
        if self._check(ttype):
            t = self.current
            self._advance()
            return self._token_node(t, label=label)
        self._error_here(msg)
        raise ParseError()

    def _consume_kw(self, kw, msg):
        if self._check_kw(kw):
            t = self.current
            self._advance()
            return self._token_node(t, label=str(t.value))
        self._error_here(msg)
        raise ParseError()

    def _error_here(self, message):
        if self.current is None:
            self.errors.append(f"[EOF] Erro sintático: {message}")
        else:
            self.errors.append(f"[linha {self.current.line}, col {self.current.column}] Erro sintático perto de '{self.current.value}': {message}")

    def _synchronize(self):
        while self.current is not None:
            if self._match(TokenType.SEMICOLON, capture=False):
                return
            if self._check_kw("if", "while", "print", "input", "var"):
                return
            if self._check(TokenType.RBRACE):
                return
            self._advance()

    def parse(self):
        try:
            self.root = self.programa()
            if self.current is not None:
                self._error_here("tokens após o fechamento de 'main'.")
        except ParseError:
            self.root = None
            self._synchronize()
        return self.errors

    def programa(self):
        node = SyntaxNode("programa")
        node.add_child(self._consume_kw("main", "esperado 'main' no início do programa"))
        node.add_child(self._consume(TokenType.LBRACE, "esperado '{' após 'main'"))
        node.add_child(self.corpo())
        node.add_child(self._consume(TokenType.RBRACE, "esperado '}' ao final do programa"))
        return node

    def corpo(self):
        node = SyntaxNode("corpo")
        node.add_child(self.secaoDeclaracoes())
        node.add_child(self.listaComandos())
        return node

    def secaoDeclaracoes(self):
        node = SyntaxNode("secaoDeclaracoes")
        node.add_child(self._consume_kw("var", "esperado 'var' no início da seção de declarações"))
        node.add_child(self._consume(TokenType.LBRACE, "esperado '{' após 'var'"))
        node.add_child(self.listaDeclaracoes())
        node.add_child(self._consume(TokenType.RBRACE, "esperado '}' ao final da seção 'var'"))
        return node

    def listaDeclaracoes(self):
        node = SyntaxNode("listaDeclaracoes")
        node.add_child(self.declaracao())
        while self._check(TokenType.IDENTIFIER):
            node.add_child(self.declaracao())
        return node

    def declaracao(self):
        node = SyntaxNode("declaracao")
        node.add_child(self._consume(TokenType.IDENTIFIER, "esperado identificador na declaração"))
        node.add_child(self._consume(TokenType.COLON, "esperado ':' após identificador"))
        node.add_child(self.tipo())
        node.add_child(self._consume(TokenType.SEMICOLON, "esperado ';' ao final da declaração"))
        return node

    def tipo(self):
        node = SyntaxNode("tipo")
        tipo_node = self._match_kw("int", "real")
        if tipo_node is None:
            self._error_here("esperado tipo 'int' ou 'real'")
            raise ParseError()
        node.add_child(tipo_node)
        return node

    def listaComandos(self):
        node = SyntaxNode("listaComandos")
        node.add_child(self.comando())
        while (
            self._check(TokenType.LBRACE)
            or self._check(TokenType.IDENTIFIER)
            or self._check_kw("input", "print", "if", "while")
        ):
            node.add_child(self.comando())
        return node

    def comando(self):
        node = SyntaxNode("comando")
        try:
            if self._check(TokenType.IDENTIFIER):
                node.add_child(self.atribuicao())
            elif self._check_kw("input"):
                node.add_child(self.leitura())
            elif self._check_kw("print"):
                node.add_child(self.escrita())
            elif self._check_kw("if"):
                node.add_child(self.condicional())
            elif self._check_kw("while"):
                node.add_child(self.repeticao())
            elif self._check(TokenType.LBRACE):
                node.add_child(self.bloco())
            else:
                self._error_here("comando inválido")
                raise ParseError()
        except ParseError:
            self._synchronize()
        return node

    def atribuicao(self):
        node = SyntaxNode("atribuicao")
        node.add_child(self._consume(TokenType.IDENTIFIER, "esperado identificador na atribuição"))
        node.add_child(self._consume(TokenType.ASSIGN_LEFT, "esperado '<-' após identificador"))
        node.add_child(self.expressaoAritmetica())
        node.add_child(self._consume(TokenType.SEMICOLON, "esperado ';' ao final da atribuição"))
        return node

    def leitura(self):
        node = SyntaxNode("leitura")
        node.add_child(self._consume_kw("input", "esperado 'input'"))
        node.add_child(self._consume(TokenType.LPAREN, "esperado '(' após 'input'"))
        node.add_child(self._consume(TokenType.IDENTIFIER, "esperado identificador dentro de input(...)", label="IDENTIFIER"))
        node.add_child(self._consume(TokenType.RPAREN, "esperado ')' após input(...)", label="RPAREN"))
        node.add_child(self._consume(TokenType.SEMICOLON, "esperado ';' ao final de input(...)"))
        return node

    def escrita(self):
        node = SyntaxNode("escrita")
        node.add_child(self._consume_kw("print", "esperado 'print'"))
        node.add_child(self._consume(TokenType.LPAREN, "esperado '(' após 'print'"))
        value_node = self._match(TokenType.IDENTIFIER, TokenType.STRING)
        if value_node is None:
            self._error_here("esperado identificador ou cadeia de caracteres em print(...)")
            raise ParseError()
        node.add_child(value_node)
        node.add_child(self._consume(TokenType.RPAREN, "esperado ')' após print(...)", label="RPAREN"))
        node.add_child(self._consume(TokenType.SEMICOLON, "esperado ';' ao final de print(...)"))
        return node

    def condicional(self):
        node = SyntaxNode("condicional")
        node.add_child(self._consume_kw("if", "esperado 'if'"))
        node.add_child(self.expressaoRelacional())
        node.add_child(self._consume_kw("then", "esperado 'then' após condição do if"))
        node.add_child(self.comando())
        else_node = self._match_kw("else")
        if else_node is not None:
            node.add_child(else_node)
            node.add_child(self.comando())
        return node

    def repeticao(self):
        node = SyntaxNode("repeticao")
        node.add_child(self._consume_kw("while", "esperado 'while'"))
        node.add_child(self.expressaoRelacional())
        node.add_child(self.comando())
        return node

    def bloco(self):
        node = SyntaxNode("bloco")
        node.add_child(self._consume(TokenType.LBRACE, "esperado '{' para iniciar bloco"))
        node.add_child(self.listaComandos())
        node.add_child(self._consume(TokenType.RBRACE, "esperado '}' para finalizar bloco"))
        return node

    def expressaoAritmetica(self):
        node = SyntaxNode("expressaoAritmetica")
        node.add_child(self.termo())
        while self._check(TokenType.MATH_OPERATOR) and self.current.value in {"+", "-"}:
            op_token = self.current
            self._advance()
            node.add_child(self._token_node(op_token, label=str(op_token.value)))
            node.add_child(self.termo())
        return node

    def termo(self):
        node = SyntaxNode("termo")
        node.add_child(self.fator())
        while self._check(TokenType.MATH_OPERATOR) and self.current.value in {"*", "/"}:
            op_token = self.current
            self._advance()
            node.add_child(self._token_node(op_token, label=str(op_token.value)))
            node.add_child(self.fator())
        return node

    def fator(self):
        node = SyntaxNode("fator")
        value_node = self._match(TokenType.NUMINT, TokenType.NUMREAL)
        if value_node is not None:
            node.add_child(value_node)
            return node
        if self._check(TokenType.IDENTIFIER):
            identifier = self.current
            self._advance()
            node.add_child(self._token_node(identifier))
            inc_dec = self._match(TokenType.INCREMENT, TokenType.DECREMENT)
            if inc_dec is not None:
                node.add_child(inc_dec)
            return node
        if self._check(TokenType.LPAREN):
            node.add_child(self._consume(TokenType.LPAREN, "esperado '(' antes da expressão", label="LPAREN"))
            node.add_child(self.expressaoAritmetica())
            node.add_child(self._consume(TokenType.RPAREN, "esperado ')' após expressão", label="RPAREN"))
            return node
        self._error_here("esperado fator (número, identificador ou '(expr)')")
        raise ParseError()

    def expressaoRelacional(self):
        node = SyntaxNode("expressaoRelacional")
        node.add_child(self.termoRelacional())
        while self._check_kw("E", "OU"):
            connector = self.current
            self._advance()
            node.add_child(self._token_node(connector, label=str(connector.value)))
            node.add_child(self.termoRelacional())
        return node

    def termoRelacional(self):
        node = SyntaxNode("termoRelacional")
        nao_node = self._match_kw("NAO")
        if nao_node is not None:
            node.add_child(nao_node)
            node.add_child(self.termoRelacional())
            return node
        if self._check(TokenType.LPAREN):
            node.add_child(self._consume(TokenType.LPAREN, "esperado '(' antes da expressão relacional", label="LPAREN"))
            node.add_child(self.expressaoRelacional())
            node.add_child(self._consume(TokenType.RPAREN, "esperado ')' após expressão relacional", label="RPAREN"))
            return node
        node.add_child(self.expressaoAritmetica())
        rel_op = self._match(TokenType.REL_OPERATOR)
        if rel_op is None:
            self._error_here("esperado operador relacional (>, <, >=, <=, ==, !=)")
            raise ParseError()
        node.add_child(rel_op)
        node.add_child(self.expressaoAritmetica())
        return node
