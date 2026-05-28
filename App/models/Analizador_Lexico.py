import re


class Token:
    def __init__(self, tipo, valor, linea):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea

    def __str__(self):
        return f"<{self.tipo}, {self.valor}>"


class AnalizadorLexico:
    def __init__(self, codigo_fuente):
        self.codigo = codigo_fuente
        self.posicion = 0
        self.linea = 1

        # Patrones ajustados EXACTAMENTE a las columnas de tu tabla LL(1)
        patrones = [
            # Palabras reservadas de tu lenguaje
            ('Reservada', r"\b(programa|procede|funcion|if|while|else|return|and|or|not|VERDADERO|FALSO|print|Finprog)\b"),
            ('tipo', r"\b(int|float|char|string)"),
            ('FuncionNativa', r"\bleer\(\)"),  # leer() completo

            # Tipos de datos literales
            ('num', r"\b\d+(\.\d+)?\b"),
            ('litcad', r'"[^"]*"'),
            ('litcar', r"'[^']'"),
            ('noid', r"\b[0-9][a-zA-Z0-9_]*\b"),
            # Identificadores (variables, nombres de funcion)
            ('id', r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),

            # Operadores y Símbolos de un solo carácter o dobles
            ('OperadorRelacional', r"==|!=|>=|<=|>|<"),
            ('OperadorMatematico', r"[\+\-\*/]"),
            ('Asignacion', r"="),
            ('Parentesis', r"[\(\)]"),
            ('Llaves', r"[\{\}]"),
            ('Coma', r","),
            ('DP', r":"),

            # Control de espacios y saltos de línea
            ('Salto', r"\n"),
            ('Espacio', r"[ \t\r]+"),

            # Cualquier otra cosa es un error léxico
            ('Error', r".")
        ]

        # Unimos todo en una sola gran expresión regular nombrada
        self.regex = re.compile('|'.join(f'(?P<{nombre}>{reg})' for nombre, reg in patrones))

    def obtener_todos_los_tokens_gui(self):
        """Método auxiliar exclusivo para llenar la tabla visual de la GUI"""
        lista_tokens = []
        token, error = self.obtener_token()
        while token.tipo != '$' if token else 1:
            # Formateamos el token para que tu GUI lo lea como string
            if error:
                lista_tokens.append(f"{error}\n")
            if token:
                lista_tokens.append(f"<{token.tipo}, {token.valor}>\n")
            token, error = self.obtener_token()
        return lista_tokens

    def obtener_token(self):
        """Método On-Demand: Lee y devuelve solo el SIGUIENTE token."""
        error = None
        while self.posicion < len(self.codigo):
            match = self.regex.match(self.codigo, self.posicion)
            if match:
                tipo = match.lastgroup
                valor = match.group()
                self.posicion = match.end()  # Avanzamos el puntero global

                if tipo == "Salto":
                    self.linea += 1
                    continue
                elif tipo == "Espacio":
                    continue

                elif tipo == "Error":
                    error = f"Error Léxico: Carácter no reconocido '{valor}' en la línea {self.linea}"
                    return False, error
                elif tipo == "noid":
                    error = f"Error Léxico: Id invalido '{valor}' en la línea {self.linea}"
                    return False, error

                # Para el parser, si es un símbolo o palabra reservada, la columna de la matriz es el valor mismo.
                # Ej: Si es un '+', buscamos la columna '+'. Si es un id, buscamos la columna 'id'.
                if tipo in ["Reservada", "OperadorRelacional", "OperadorMatematico", "Asignacion", "Parentesis",
                            "Llaves", "Coma", "FuncionNativa"]:
                    return Token(tipo, valor, self.linea), error
                else:
                    return Token(tipo, valor, self.linea), error
            else:
                self.posicion += 1  # Prevenir bucle infinito en caso catastrófico

        return Token('$', '$', self.linea), error  # Fin de archivo