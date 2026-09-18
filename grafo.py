import difflib
import unicodedata
from collections import defaultdict

from datos_metro import ALIAS, LINEAS


def normalizar(texto):
    """'Politécnico' -> 'politecnico'. Quita acentos, espacios y signos."""
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_acentos = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    return "".join(c for c in sin_acentos.lower() if c.isalnum())


class Grafo:
    def __init__(self):
        self._adyacencia = defaultdict(set)        # estación -> {vecinos}
        self._lineas_de_arista = defaultdict(set)  # {a, b} -> {líneas del tramo}
        self._lineas_de_estacion = defaultdict(set)

    # ------------------------------------------------------------ construcción
    def agregar_arista(self, a, b, linea):
        self._adyacencia[a].add(b)
        self._adyacencia[b].add(a)
        self._lineas_de_arista[frozenset((a, b))].add(linea)
        self._lineas_de_estacion[a].add(linea)
        self._lineas_de_estacion[b].add(linea)

    # --------------------------------------------------------------- consultas
    def vecinos(self, estacion):
        return sorted(self._adyacencia[estacion], key=normalizar)

    def lineas_entre(self, a, b):
        return self._lineas_de_arista[frozenset((a, b))]

    def lineas_de(self, estacion):
        return self._lineas_de_estacion[estacion]

    def son_vecinas(self, a, b):
        return b in self._adyacencia[a]

    @property
    def estaciones(self):
        return list(self._adyacencia)

    @property
    def num_estaciones(self):
        return len(self._adyacencia)

    @property
    def num_aristas(self):
        return len(self._lineas_de_arista)

    def buscar_estacion(self, nombre):
        """Convierte lo que escribe el usuario en el nombre exacto del nodo."""
        indice = {}
        for estacion in self._adyacencia:
            indice[normalizar(estacion)] = estacion
            for parte in estacion.split("/"):  # "Zócalo/Tenochtitlan" -> "Zócalo"
                indice.setdefault(normalizar(parte), estacion)
        for alias, real in ALIAS.items():
            indice[normalizar(alias)] = real

        clave = normalizar(nombre)
        if clave in indice:
            return indice[clave]

        parecidas = difflib.get_close_matches(clave, indice, n=3, cutoff=0.6)
        sugerencias = ", ".join(sorted({indice[p] for p in parecidas}))
        mensaje = f"No existe la estación '{nombre}'."
        if sugerencias:
            mensaje += f" ¿Quisiste decir: {sugerencias}?"
        raise KeyError(mensaje)

    # --------------------------------------------------- lectura de una ruta
    def segmentar_por_linea(self, ruta):
        if len(ruta) < 2:
            return []
        segmentos = []
        inicio = 0
        lineas_actuales = set(self.lineas_entre(ruta[0], ruta[1]))
        for i in range(1, len(ruta) - 1):
            siguientes = self.lineas_entre(ruta[i], ruta[i + 1])
            comunes = lineas_actuales & siguientes
            if comunes:
                lineas_actuales = comunes
            else:  # la siguiente arista es de otra línea: hubo transbordo en ruta[i]
                segmentos.append((sorted(lineas_actuales)[0], ruta[inicio:i + 1]))
                inicio = i
                lineas_actuales = set(siguientes)
        segmentos.append((sorted(lineas_actuales)[0], ruta[inicio:]))
        return segmentos


def construir_grafo_metro(lineas=LINEAS):
    grafo = Grafo()
    for linea, estaciones in lineas.items():
        for actual, siguiente in zip(estaciones, estaciones[1:]):
            grafo.agregar_arista(actual, siguiente, linea)
    return grafo
