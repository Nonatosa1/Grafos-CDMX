from collections import deque
from dataclasses import dataclass, field


@dataclass
class Iteracion:
    numero: int
    actual: str          # estación que se sacó de la frontera
    agregadas: list      # estaciones que se metieron a la frontera
    frontera: list       # contenido de la frontera al terminar la iteración
    nota: str = ""


@dataclass
class Resultado:
    algoritmo: str
    origen: str
    destino: str
    ruta: list                  # [] si no hay camino
    exploradas: int             # estaciones expandidas (visitadas)
    traza: list = field(default_factory=list)

    @property
    def encontrada(self):
        return bool(self.ruta)

    @property
    def costo(self):
        """Número de tramos recorridos (cada uno cuesta 1)."""
        return len(self.ruta) - 1 if self.ruta else None


def reconstruir_ruta(padres, destino):
    """Camina hacia atrás desde el destino siguiendo a los padres."""
    ruta = []
    estacion = destino
    while estacion is not None:
        ruta.append(estacion)
        estacion = padres[estacion]
    ruta.reverse()
    return ruta


def bfs(grafo, origen, destino, registrar=False):
    frontera = deque([origen])       # COLA
    padres = {origen: None}          # descubiertas (y de dónde vienen)
    traza = []
    iteracion = 0

    while frontera:
        actual = frontera.popleft()  # la más antigua
        iteracion += 1

        if actual == destino:
            if registrar:
                traza.append(Iteracion(iteracion, actual, [], list(frontera), "DESTINO"))
            ruta = reconstruir_ruta(padres, destino)
            return Resultado("BFS", origen, destino, ruta, iteracion, traza)

        agregadas = []
        for vecino in grafo.vecinos(actual):
            if vecino not in padres:
                # Se marca AL DESCUBRIRLA: la primera vez que BFS ve una
                # estación ya es por el camino más corto, así que no hace
                # falta volver a meterla.
                padres[vecino] = actual
                frontera.append(vecino)
                agregadas.append(vecino)

        if registrar:
            traza.append(Iteracion(iteracion, actual, agregadas, list(frontera)))

    return Resultado("BFS", origen, destino, [], iteracion, traza)


def dfs(grafo, origen, destino, registrar=False):
    frontera = [(origen, None)]      # PILA de (estación, quién la apiló)
    padres = {}                      # visitadas (y de dónde vienen)
    traza = []
    iteracion = 0
    exploradas = 0

    while frontera:
        actual, padre = frontera.pop()  # la más reciente
        iteracion += 1

        if actual in padres:
            # Se apiló dos veces por caminos distintos y ya se visitó.
            if registrar:
                traza.append(Iteracion(iteracion, actual, [], _nombres(frontera),
                                       "ya visitada: se descarta"))
            continue

        # Se marca AL SACARLA: así el padre es la rama más profunda que la
        # alcanzó, que es justamente el comportamiento de DFS.
        padres[actual] = padre
        exploradas += 1

        if actual == destino:
            if registrar:
                traza.append(Iteracion(iteracion, actual, [], _nombres(frontera), "DESTINO"))
            ruta = reconstruir_ruta(padres, destino)
            return Resultado("DFS", origen, destino, ruta, exploradas, traza)

        # Se apilan en orden inverso para que la primera en orden alfabético
        # quede hasta arriba y sea la siguiente en explorarse.
        agregadas = []
        for vecino in reversed(grafo.vecinos(actual)):
            if vecino not in padres:
                frontera.append((vecino, actual))
                agregadas.append(vecino)

        if registrar:
            traza.append(Iteracion(iteracion, actual, agregadas[::-1], _nombres(frontera)))

    return Resultado("DFS", origen, destino, [], exploradas, traza)


def _nombres(pila):
    return [estacion for estacion, _ in pila]


ALGORITMOS = {"bfs": bfs, "dfs": dfs}
