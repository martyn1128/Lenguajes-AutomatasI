import pandas as pd


class AnalizadorSintactico:
    def __init__(self, ruta_excel='App/models/Tabla.xlsx'):
        self.tabla = pd.read_excel(ruta_excel, sheet_name='TABLA')
        self.tabla.set_index(self.tabla.columns[0], inplace=True)
        self.tabla.index.name = None
        self.errores = ["Proceso finalizado con 0 Errores"]
        self.pil = []

    def _registrar_error(self, mensaje):
        if self.errores == ["Proceso finalizado con 0 Errores"]:
            self.errores = []
        self.errores.append(mensaje)


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
        self.errores = ["Proceso finalizado con 0 Errores"]
        self.pil = []
        pila = ['$', 'prog']
        token_actual, error = lexer.obtener_token()

        while len(pila) > 0:
            if not token_actual:
                if error:
                    self._registrar_error(error)
                    self.pil.append(pila)
                    token_actual, error = lexer.obtener_token()
                    continue
                break

            tk = token_actual.tipo

            if tk == 'Comentario':
                token_actual, error = lexer.obtener_token()
                continue

            if error:
                self._registrar_error(error)

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
            self.pil.append(f"{pila}")
            cima = pila.pop()

            if cima in self.tabla.index:
                if tk in self.tabla.columns:
                    produccion = self.tabla.loc[cima, tk]
                    produccion = str(produccion).strip()

                    if produccion == 'Salto':
                        token_actual, error = lexer.obtener_token()
                        pila.append(cima)
                        continue

                    if produccion == 'Saltar':
                        self.agrega_error(cima, token_actual.valor, token_actual.linea)
                        if tk == '$':
                            break
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
                        return self.pil
                    token_actual, error = lexer.obtener_token()
                else:
                    if token_actual:
                        self.agrega_error(cima, token_actual.valor, token_actual.linea)
                        if token_actual.tipo == '$':
                            break

                    else:
                        print(error)
                        self._registrar_error(error)
                    #pila.append(cima)
                    token_actual, error = lexer.obtener_token()

        return self.pil

    def agrega_error(self, cima, valor, linea):
        match cima:
            case 'L':
                cima = "expresion valida"
            case 'T':
                cima = "expresion valida"
            case '$':
                cima = "el final del programa"
            case 'modulo':
                cima = "procede, funcion o una declaracion"
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

        self._registrar_error(
            f"Error sintactico: Se esperaba ' {cima} ' antes de '{valor}' (Linea {linea})\n"
        )
