import re


class Token:
    def __init__(self, tipo, valor, linea):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea

    def __str__(self):
        return f"<{self.tipo}, {self.valor}>"


class TablaSimbolos:
    def __init__(self, nombre_tabla=None):
        self.tablas = {}
        self.nombre_tabla = nombre_tabla

    def buscar_nombre_local(self, nombre):
        for lista_datos in self.tablas.values():
            for datos in lista_datos:
                if datos[0] == nombre:
                    return True

        return False

    def agregar_tabla(self, com, nombre, tipo, valor, link=None):
        if self.buscar_nombre_local(nombre):
            return False

        if com not in self.tablas:
            self.tablas[com] = []

        self.tablas[com].append([nombre, tipo, valor, link])
        return True

    def imprimir(self, nivel=0):
        espacio = "    " * nivel

        print(espacio + "+" + "-" * 85 + "+")
        print(
            espacio +
            f"| {'Componente':<15} | "
            f"{'Nombre':<15} | "
            f"{'Tipo':<15} | "
            f"{'Valor':<15} | "
            f"{'Link':<10} |"
        )
        print(espacio + "+" + "-" * 85 + "+")

        for com, lista_datos in self.tablas.items():
            for datos in lista_datos:
                nombre = datos[0]
                tipo = datos[1]
                valor = datos[2]
                link = datos[3]

                tiene_link = "Si" if isinstance(link, TablaSimbolos) else "No"

                print(
                    espacio +
                    f"| {str(com):<15} | "
                    f"{str(nombre):<15} | "
                    f"{str(tipo):<15} | "
                    f"{str(valor):<15} | "
                    f"{tiene_link:<10} |"
                )

        print(espacio + "+" + "-" * 85 + "+")

        for com, lista_datos in self.tablas.items():
            for datos in lista_datos:
                link = datos[3]

                if isinstance(link, TablaSimbolos):
                    print()
                    nombre_subtabla = link.nombre_tabla if link.nombre_tabla else datos[0]
                    print(espacio + f"Subtabla de: {nombre_subtabla}")
                    link.imprimir(nivel + 1)

    def buscar_metodo(self, nombre):
        for lista_datos in self.tablas.values():
            for datos in lista_datos:
                enlace = datos[3]
                if datos[0] == nombre and isinstance(enlace, TablaSimbolos):
                    return datos

        for lista_datos in self.tablas.values():
            for datos in lista_datos:
                enlace = datos[3]
                if isinstance(enlace, TablaSimbolos):
                    encontrado = enlace.buscar_metodo(nombre)
                    if encontrado:
                        return encontrado

        return None


class AnalizadorLexico:
    def __init__(self, codigo_fuente):
        self.codigo = codigo_fuente
        self.posicion = 0
        self.linea = 1

        self.tablaO = None
        self.tabla = None
        self.declaracion_pendiente = None

        self.pila_tablas = []

        patrones = [
            ('Comentario', r"#.*"),
            ('Reservada', r"\b(programa|procede|funcion|if|while|else|return|and|or|not|TRUE|FALSE|print|leer)\b"),
            ('tipo', r"\b(int|float|char|string)\b"),
            ('num_error', r"(?:0[xX](?:$|[0-9a-fA-F]*[^0-9a-fA-F\s][A-Za-z0-9]*)|0[oO](?:$|[0-7]*[89][0-9]*)|[0-9]+\.(?![0-9])|[0-9]+(?:\.[0-9]+)?[eE][+-]?(?![0-9]))"),
            ('noid', r"\b(?!0[xX][0-9a-fA-F]+\b)(?!0[oO][0-7]+\b)[0-9]+[a-zA-Z_][a-zA-Z0-9_]*\b"),
            ('num', r"(?:[1-9][0-9]*((\.[0-9]*[1-9])?([eE][+-]?[0-9]+)?)?|0[oO][0-7]+|0[xX][0-9a-fA-F]+)|\b0\b"),
            ('cero', r"0[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"),
            ('litcad', r'"[^"]*"'),
            ('litcar', r"'[^']'"),
            ('id', r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
            ('OperadorRelacional', r"==|!=|>=|<=|>|<"),
            ('OperadorMatematico', r"[\+\-\*/]"),
            ('Asignacion', r"="),
            ('Parentesis', r"[\(\)]"),
            ('Llaves', r"[\{\}]"),
            ('Coma', r","),
            ('DP', r":"),
            ('Salto', r"\n"),
            ('Espacio', r"[ \t\r]+"),
            ('Error', r"."),
        ]

        self.regex = re.compile(
            '|'.join(f'(?P<{nombre}>{reg})' for nombre, reg in patrones)
        )

    def obtener_todos_los_tokens_gui(self):
        lista_tokens = []
        token, error = self.obtener_token()

        while token and token.tipo != '$':
            if error:
                lista_tokens.append(f"{error}\n")
            lista_tokens.append(f"<{token.tipo}, {token.valor}>\n")
            token, error = self.obtener_token()

        return lista_tokens

    def _siguiente_token_significativo(self, posicion):
        while posicion < len(self.codigo):
            match = self.regex.match(self.codigo, posicion)
            if not match:
                return None

            tipo = match.lastgroup
            valor = match.group()
            posicion = match.end()

            if tipo in ["Espacio", "Comentario"]:
                continue

            if tipo == "Salto":
                return None

            if tipo == "Error":
                return None

            return tipo, valor

        return None

    def obtener_token(self):
        error = None

        while self.posicion < len(self.codigo):
            match = self.regex.match(self.codigo, self.posicion)

            if not match:
                break

            tipo = match.lastgroup
            valor = match.group()
            self.posicion = match.end()
            tipo_registro = tipo
            registrar_actual = True

            if tipo == "Espacio":
                continue

            if tipo == "Comentario":
                continue

            if tipo == "Salto":
                self.linea += 1
                if self.posicion >= len(self.codigo):
                    continue
                return Token(tipo, valor, self.linea), error

            if tipo == "Error":
                error = (
                    f"Error Lexico: Caracter no reconocido "
                    f"'{valor}' en linea {self.linea}"
                )
                return False, error

            if tipo == "noid":
                error = (
                    f"Error Lexico: Id invalido "
                    f"'{valor}' en linea {self.linea}"
                )
                return False, error

            if tipo == "num_error":
                error = f"Error Lexico: Numero invalido '{valor}' en la linea {self.linea}"
                return False, error

            if tipo == "cero":
                error = (
                    f"Error Lexico: Los ceros al inicio de un numero no son permitidos "
                    f"'{valor}' en la linea {self.linea}"
                )
                return False, error

            if tipo == "id":
                if self.declaracion_pendiente:
                    tabla_padre = self.pila_tablas[-1] if self.pila_tablas else self.tabla

                    if tabla_padre:
                        tabla_padre.agregar_tabla(
                            self.declaracion_pendiente,
                            valor,
                            "idp",
                            valor,
                            self.tabla,
                        )

                    if self.tabla:
                        self.tabla.nombre_tabla = valor

                    tipo_registro = "idp"
                    registrar_actual = False
                    self.declaracion_pendiente = None
                else:
                    siguiente = self._siguiente_token_significativo(self.posicion)

                    if siguiente and siguiente[1] == "(":
                        tipo = "idp"
                        tipo_registro = "idp"
                        if not (self.tablaO and self.tablaO.buscar_metodo(valor)):
                            error = (
                                f"Error: '{valor}' "
                                f"no esta declarado como metodo o funcion {self.linea}"
                            )
                            return False, error

            if valor == "programa":
                if not self.tablaO:
                    self.tablaO = TablaSimbolos(nombre_tabla="programa")
                    self.tabla = self.tablaO

            elif valor in ["funcion", "procede"]:
                nueva_tabla = TablaSimbolos()

                self.pila_tablas.append(self.tabla)
                self.tabla = nueva_tabla
                self.declaracion_pendiente = valor

                return Token(tipo, valor, self.linea), error

            elif valor == "}":
                if self.pila_tablas:
                    self.tabla = self.pila_tablas.pop()

            if self.declaracion_pendiente and tipo != "Salto":
                self.declaracion_pendiente = None

            if registrar_actual and self.tabla:
                self.agregar_tabla(
                    self.tabla,
                    valor,
                    valor,
                    tipo_registro,
                    valor,
                    None,
                )

            return Token(tipo, valor, self.linea), error

        return Token('$', '$', self.linea), error

    def agregar_tabla(self, tabla, com, nombre, tipo, valor, link):
        tabla.agregar_tabla(com, nombre, tipo, valor, link)
