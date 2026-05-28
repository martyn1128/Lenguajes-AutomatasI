import pandas as pd


class AnalizadorSintactico:
    def __init__(self, ruta_excel='App/models/Tabla.xlsx'):
        self.tabla = pd.read_excel(ruta_excel, sheet_name='TABLA')
        self.tabla.set_index(self.tabla.columns[0], inplace=True)
        self.tabla.index.name = None
        self.errores = []

    def extraer_simbolos_manual(self, produccion):
        """
        Extrae los símbolos de la regla iterando carácter por carácter
        manualmente y separándolos por espacio.
        """
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
        print(error)
        while len(pila) > 0:
            if token_actual :
                tk = token_actual.tipo
                if tk == 'Reservada' or tk == 'Parentesis' or tk == 'Llaves' or tk == 'Coma' or tk == 'DP'\
                        or tk == 'tipo' or tk == 'Asignacion':
                    tk = token_actual.valor
            else:
                return [error]
            print(pila, tk)
            cima = pila.pop()
            # CASO 1: Terminales
            if cima not in self.tabla.index:
                if cima == tk:
                    if cima == '$':
                        return self.errores if self.errores else ["Proceso finalizado con 0 Errores"]# Éxito
                    token_actual, error = lexer.obtener_token()
                else:
                    if token_actual:
                        self.errores.append(f"Error sintactico: Se esperaba '{cima}', se encontró '{token_actual.valor}' (Línea {token_actual.linea})\n")
                        # Freno: Si estamos en el fin del archivo, no sigas pidiendo tokens
                        if token_actual.tipo == '$': break
                    else:
                        print('HJola')
                        self.errores.append(error)
                    token_actual, error = lexer.obtener_token()


            # CASO 2: No-Terminales
            else:
                if tk in self.tabla.columns:
                    produccion = self.tabla.loc[cima, tk]
                    if pd.isna(produccion):
                        self.errores.append(f"Error sintactico: Se esperaba {cima} se encontro: {tk if tk != '$' else  "el final del programa"} (Línea {token_actual.linea})\n")
                        if tk == '$': break
                        token_actual, _ = lexer.obtener_token()
                        pila.append(cima)
                        continue

                    produccion = str(produccion).strip()

                    # Gestión de comandos especiales
                    if produccion == 'Saltar':
                        token_actual, _ = lexer.obtener_token()
                        pila.append(cima)
                        continue
                    if produccion == 'Sacar':
                        continue
                    if produccion in ['Ɛ', 'ε']:
                        continue
                    # Extracción correcta (Fuera del if del épsilon)
                    simbolos = self.extraer_simbolos_manual(produccion)
                    for i in range(len(simbolos) - 1, -1, -1):
                        pila.append(simbolos[i])

                else:
                    # Token desconocido para la tabla
                    if tk == '$':
                        break
                    token_actual, _ = lexer.obtener_token()
                    pila.append(cima)


        return self.errores if self.errores else ["Proceso finalizado con 0 errores"]
