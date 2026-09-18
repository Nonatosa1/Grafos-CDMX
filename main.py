"""
Uso:
    python main.py                                   # los 3 casos del proyecto
    python main.py --origen Zapata --destino Oceanía # cualquier par
    python main.py --caso 1 --algoritmo bfs --traza  # iteración por iteración
"""

import argparse
import sys

from busqueda import ALGORITMOS
from grafo import construir_grafo_metro

CASOS = [
    ("Cuatro Caminos", "Pantitlán"),
    ("Politécnico", "Tasqueña"),
    ("Zapata", "Oceanía"),
]


def tramos(n):
    return f"{n} tramo" if n == 1 else f"{n} tramos"


def imprimir_resultado(grafo, resultado):
    print(f"\n  [{resultado.algoritmo}]")
    if not resultado.encontrada:
        print("    No existe ruta.")
        return
    segmentos = grafo.segmentar_por_linea(resultado.ruta)
    print(f"    Costo: {tramos(resultado.costo)} "
          f"({len(resultado.ruta)} estaciones contando origen y destino)")
    print(f"    Transbordos: {len(segmentos) - 1}")
    print(f"    Estaciones exploradas por el algoritmo: {resultado.exploradas}")
    for linea, tramo in segmentos:
        print(f"    Línea {linea:>2}: {tramo[0]} -> {tramo[-1]} ({tramos(len(tramo) - 1)})")
    print("    Ruta: " + " -> ".join(resultado.ruta))


def imprimir_traza(resultado):
    tipo = "cola, sale por la IZQUIERDA" if resultado.algoritmo == "BFS" \
        else "pila, sale por la DERECHA (tope)"
    print(f"\n  Traza de {resultado.algoritmo} (frontera = {tipo})")
    for it in resultado.traza:
        print(f"\n  Iteración {it.numero}")
        print(f"    Sale:      {it.actual}" + (f"  <-- {it.nota}" if it.nota else ""))
        if it.agregadas:
            print(f"    Entran:    {', '.join(it.agregadas)}")
        print(f"    Frontera:  [{', '.join(it.frontera)}]")


def resolver(grafo, origen, destino, algoritmos, traza):
    origen = grafo.buscar_estacion(origen)
    destino = grafo.buscar_estacion(destino)
    print("=" * 78)
    print(f"{origen}  ->  {destino}")
    print("=" * 78)
    for nombre in algoritmos:
        resultado = ALGORITMOS[nombre](grafo, origen, destino, registrar=traza)
        if traza:
            imprimir_traza(resultado)
        imprimir_resultado(grafo, resultado)
    print()


def main():
    parser = argparse.ArgumentParser(description="Rutas en el Metro CDMX con BFS y DFS")
    parser.add_argument("--origen")
    parser.add_argument("--destino")
    parser.add_argument("--caso", type=int, choices=range(1, len(CASOS) + 1),
                        help="Resolver solo uno de los casos del proyecto")
    parser.add_argument("--algoritmo", choices=["bfs", "dfs", "ambos"], default="ambos")
    parser.add_argument("--traza", action="store_true",
                        help="Mostrar el proceso iteración por iteración")
    args = parser.parse_args()

    algoritmos = ["bfs", "dfs"] if args.algoritmo == "ambos" else [args.algoritmo]
    grafo = construir_grafo_metro()
    print(f"Grafo del Metro: {grafo.num_estaciones} estaciones, "
          f"{grafo.num_aristas} tramos\n")

    if args.origen or args.destino:
        if not (args.origen and args.destino):
            parser.error("--origen y --destino van juntos")
        casos = [(args.origen, args.destino)]
    elif args.caso:
        casos = [CASOS[args.caso - 1]]
    else:
        casos = CASOS

    try:
        for origen, destino in casos:
            resolver(grafo, origen, destino, algoritmos, args.traza)
    except KeyError as error:
        sys.exit(error.args[0])


if __name__ == "__main__":
    main()
