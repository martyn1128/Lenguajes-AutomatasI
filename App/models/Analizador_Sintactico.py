import pandas as pd
class AnalizadorSintactico:
    def __init__(self):
        self.mensaje = "Estamos trabajando en esto..."
        self.tabla = pd.read_excel('App/models/Tabla.xlsx', sheet_name='TABLA', header=2)
        self.tabla = self.tabla.iloc[:, 2:]
        self.tabla.set_index(self.tabla.columns[0], inplace=True)
        self.tabla.index.name = None

    def analizar(self, lista_tokens):
        # 1. Inicializar la pila con el símbolo de fin de archivo ($) y el No-Terminal inicial
        pila = ['$']
        pila.append('E')  # 'prog' es tu símbolo inicial según tu Excel

        # Clonamos la lista de tokens y nos aseguramos de que termine en '$'
        tokens = lista_tokens.copy()
        errores = ""
        if tokens[-1] != '$':
            tokens.append('$')

        posicion = 0  # Puntero para saber qué token estamos leyendo

        while len(pila) > 0:
            print("pila:", pila, "Tokens", tokens[posicion:])
            cima = pila.pop() # Ver lo que hay arriba de la pila
            token_actual = tokens[posicion]  # El token que viene del código fuente
            # CASO 1: La cima de la pila es igual al token actual
            if cima == token_actual:
                if cima == '$':
                    errores += "¡Análisis sintáctico exitoso! El código es correcto."
                else:
                    posicion += 1  # Avanzamos al siguiente token de la entrada

            # CASO 2: La cima es un No-Terminal (Buscamos en la matriz de Pandas)
            else:
                # Validar si el No-Terminal existe en las filas y el token en las columnas
                if cima in self.tabla.index and token_actual in self.tabla.columns:
                    produccion = self.tabla.loc[cima, token_actual]

                    # Si la celda está vacía (NaN), es un error sintáctico
                    if pd.isna(produccion):
                        errores += f"Error sintáctico: No hay regla para {cima} con el token '{token_actual}'"

                    # Si la producción es Épsilon (Ɛ), no metemos nada a la pila (solo se hizo el pop)
                    if produccion == 'Ɛ' or produccion.strip() == 'Ɛ':
                        continue

                    # Si tiene símbolos, los separamos e invertimos
                    # Se invierten porque el primero debe quedar hasta arriba de la pila
                    simbolos = produccion
                    for x in range(len(simbolos)):
                        try:
                            s = simbolos[-1]
                            simbolos = simbolos[:len(simbolos) - 1]
                            if s == "'":
                                s = simbolos[len(simbolos) -1] + s
                                simbolos = simbolos[:len(simbolos) -1]
                            elif s == "d":
                                s = simbolos[len(simbolos) - 1] + s
                                simbolos = simbolos[:len(simbolos) - 1]
                            elif s == "m":
                                s = "num"
                                simbolos = simbolos[:len(simbolos) - 2]
                            pila.append(s)
                        except IndexError:
                            pass
                else:
                    errores+= f"Error: El símbolo '{cima}' o el token '{token_actual}' no pertenecen a la gramática."

        return errores