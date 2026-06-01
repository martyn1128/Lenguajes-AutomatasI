import pandas as pd


class AnalizadorSintactico:
    def __init__(self, ruta_excel='App/models/Tabla.xlsx'):
        self.tabla = pd.read_excel(ruta_excel, sheet_name='TABLA')
        self.tabla.set_index(self.tabla.columns[0], inplace=True)
        self.tabla.index.name = None
        self.errores = ["Proceso finalizado con 0 Errores"]

    def extraer_simbolos_manual(self, produccion):
        simbolos = []
        palabra_actual = ""

        for char in produccion:
            if char == ' ':
                if palabra_actual != "":
                    simbolos.append(palabra_actual)
                    palabra_actual = ""
            else:
                palabra_actual += char

        if palabra_actual != "":
            simbolos.append(palabra_actual)

        return simbolos

    def analizar(self, lexer):
        pila = ['$', 'prog']
        token_actual, error = lexer.obtener_token()

        while len(pila) > 0:
            if not token_actual and error:
                return [error]

            tk = token_actual.tipo

            if tk == 'Comentario':
                token_actual, error = lexer.obtener_token()
                continue

            if tk in [
                'Reservada',
                'Parentesis',
                'Llaves',
                'Coma',
                'DP',
                'tipo',
                'Asignacion',
                'OperadorMatematico',
                'OperadorRelacional'
            ]:
                tk = token_actual.valor

            print(pila, tk)
            cima = pila.pop()

            if cima in self.tabla.index:
                if tk in self.tabla.columns:
                    produccion = self.tabla.loc[cima, tk]
                    if pd.isna(produccion):
                        self.agrega_error(cima, token_actual.valor, token_actual.linea)
                        if tk == '$':
                            break
                        token_actual, error = lexer.obtener_token()
                        pila.append(cima)
                        continue

                    produccion = str(produccion).strip()

                    if produccion == 'Salto':
                        token_actual, error = lexer.obtener_token()
                        pila.append(cima)
                        continue

                    if produccion == 'Saltar':
                        self.agrega_error(cima, token_actual.valor, token_actual.linea)
                        token_actual, error = lexer.obtener_token()
                        pila.append(cima)
                        continue

                    if produccion == 'Sacar':
                        self.agrega_error(cima, token_actual.valor, token_actual.linea)
                        continue

                    if produccion in ['Ɛ', 'ε']:
                        continue

                    simbolos = self.extraer_simbolos_manual(produccion)
                    for i in range(len(simbolos) - 1, -1, -1):
                        pila.append(simbolos[i])
                else:
                    if tk == '$':
                        break
                    token_actual, error = lexer.obtener_token()
                    pila.append(cima)
            else:
                if cima == tk:
                    if cima == '$':
                        return self.errores
                    token_actual, error = lexer.obtener_token()
                else:
                    if token_actual:
                        self.agrega_error(cima, token_actual.valor, token_actual.linea)
                        if token_actual.tipo == '$':
                            break
                    else:
                        self.errores.append(error)
                    token_actual, error = lexer.obtener_token()

        return self.errores

    def agrega_error(self, cima, valor, linea):
        if self.errores == ["Proceso finalizado con 0 Errores"]:
            self.errores = []

        match cima:
            case 'L':
                cima = "expresion valida"
            case '$':
                cima = "el final del programa"
            case 'modulo':
                cima = "procede o funcion"
            case 'prog':
                cima = "programa"
            case "T'":
                cima = "id valido"
            case "llamada":
                cima = "llamada de metodo"
            case "Salto":
                cima = "operador o salto de linea"
            case "siglist":
                cima = ")"

        match valor:
            case '$':
                valor = "el final del programa"
            case '\n':
                valor = "salto de linea"

        self.errores.append(
            f"Error sintactico: Se esperaba ' {cima} ' antes de '{valor}' (Linea {linea})\n"
        )
