# Grupo: Bruna Gabriela Soares de Lima - 30481961
# Ana Julia Grzyb - 32703902
# Patrick Luan Ventura Aragão - 29432294
# Júlio Pedro Santos Monteiro - 30199115

import sys
from lexical.scanner import Scanner
from lexical.parser import Parser

def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else r"programa.mc"
    scanner = Scanner(filename)
    parser = Parser(scanner)
    errors = parser.parse()
    if errors:
        print("Erros sintáticos encontrados:")
        for e in errors:
            print("-", e)
        raise SystemExit(1)
    print("Programa válido (sintaxe OK).")

if __name__ == "__main__":
    main()
