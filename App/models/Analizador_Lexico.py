import re

class AnalizadorLexico:
    def __init__(self):
        patrones = [
            ('Hexadecimal', r"[-+]?0[xX][\da-fA-F]+"),
            ('Octal', r"[-+]?0[oO][0-7]+"),
            ('Flotante', r'[-+]?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?'),
            ('Entero', r"[-+]?\d+"),

            ('KeyWord', r"\b(and|or|not|for|if|in|is|else|while|import|def|class|print|None|pass|try|with)\b"),

            ('ID', r"[a-zA-Z_][a-zA-Z0-9_]*"),

            ('Operador', r"\*\*=|//=|==|<=|>=|\+=|\*=|-=|/=|!=|\*\*|//|[\*\+\-/=<>%]"),

            ('Parentesis', r'[\(\)]'),
            ('Llaves', r'[\{\}]'),
            ('Cadena', r'"[^"]*"'),

            ('Espacio', r'[ \t\n]+'),

            ('Error', r'.'),
        ]

        self.expresion = '|'.join(f'(?P<{nombre}>{reg})' for nombre, reg in patrones)

    def analizar(self, cadena=""):
        tokens = []

        for match in re.finditer(self.expresion, cadena):
            tipo = match.lastgroup
            valor = match.group()

            if tipo == 'Espacio':
                continue

            elif tipo == 'Error':
                tokens.append(("Error", valor))

            elif tipo == 'Hexadecimal':
                tokens.append(("Entero", int(valor, 16)))

            elif tipo == 'Octal':
                tokens.append(("Entero", int(valor, 8)))

            elif tipo == 'Entero':
                tokens.append((tipo, int(valor)))

            elif tipo == 'Flotante':
                tokens.append((tipo, float(valor)))

            else:
                tokens.append((tipo, valor))

        return tokens


# ----------- PROGRAMA PRINCIPAL -----------

def main():
    analizador = AnalizadorLexico()

    while True:
        print("1.- Analizador Léxico")
        print("2.- Salir")

        try:
            op = int(input("Elija una opción: "))
        except ValueError:
            print("Ingresa un número válido\n")
            continue

        if op == 1:
            cadena = input("\nEscribe código: ")

            resultado = analizador.analizar(cadena)

            print("\nComponentes léxicos encontrados:")
            print(f"{'Tipo':<15} | {'Valor'}")
            print("-" * 30)

            for tipo, valor in resultado:
                print(f"{tipo:<15} | {valor}")

            print("-" * 30 + "\n")

        elif op == 2:
            print("Saliendo del programa...")
            break

        else:
            print("Opción inválida\n")


if __name__ == "__main__":
    main()