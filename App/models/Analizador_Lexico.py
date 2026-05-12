import re

class AnalizadorLexico:
    def __init__(self):
        patrones = [
            ('num', r"[1-9][0-9]*((\.[0-9]*[1-9])?([eE][+-]?[1-9][0-9]*)?)?|0[oO][0-7]+|0[xX][1-9][0-9]*a-fA-F]+")
,
            ('KeyWord', r"\b(and|or|not|for|if|in|is|else|while|import|def|class|print|None|pass|try|with)\b"),

            ('id', r"[a-zA-Z_][a-zA-Z0-9_]*"),

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
            if tipo == "Espacio":
                pass
            elif tipo == "Operador" or tipo == "Parentesis" or tipo == "KeyWord" or tipo == "Llaves":
                tokens.append(valor)
            else:
                tokens.append(tipo)

        return tokens