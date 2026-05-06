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