import heapq
# import networkx as nx
import matplotlib.pyplot as plt


# Cada hilo debe de llamar a la funcion dijkstra, si queremos ser mas realistas pensaba en que deben de llamarlo cada que cruza una interseccion
# esto debido a que si hay una congestion, que tomen la desicion de ir por otro lado

def dijkstra(grafo, nodo_origen):
    # Inicializar las distancias mas cortas conocidas como infinito
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[nodo_origen] = 0 # La distancia de inicio con el nodo origen es 0

    # Diccionario para reconstruir caminos
    predecesores = {nodo: None for nodo in grafo}

    # Cola de prioridad para explorar los nodos, inicializada con el nodo origen
    cola_prioridad = [(0, nodo_origen)] # (distancia, nodo)

    # Mientras hay nodos por explorar
    while cola_prioridad:
        #obtener el nodo con la menor distancia conocida
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

        # Si la distancia actual es mayor que la registrada, continua
        if distancia_actual > distancias[nodo_actual]:
            continue

        # Explorar los vecinos del nodo actual
        for vecino, peso in grafo[nodo_actual].items():
            # Calcula la distancia al vecino a traves del nodo actual
            nueva_distancia = distancia_actual + peso

            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                # Guardar quién lleva al vecino
                predecesores[vecino] = nodo_actual
                #Agregar el vecino a la cola de prioridad
                heapq.heappush(cola_prioridad, (nueva_distancia, vecino))
    
    return distancias, predecesores

def reconstruir_camino(predecesores, origen, destino):
    camino = []
    actual = destino

    while actual is not None:
        camino.append(actual)
        actual = predecesores[actual]

    camino.reverse()

    # Validar si realmente se alcanzó el destino
    if camino[0] != origen:
        return None  # No hay camino

    return camino

def calcular_camino(grafo, nodo_origen, nodo_destino):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[nodo_origen] = 0 # La distancia de inicio con el nodo origen es 0
    predecesores = {nodo: None for nodo in grafo}
    cola_prioridad = [(0, nodo_origen)] # (distancia, nodo)
    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
        if distancia_actual > distancias[nodo_actual]:
            continue
        for vecino, peso in grafo[nodo_actual].items():
            nueva_distancia = distancia_actual + peso
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (nueva_distancia, vecino))

    camino = []
    actual = nodo_destino
    while actual is not None:
        camino.append(actual)
        actual = predecesores[actual]
    camino.reverse()
    if camino[0] != nodo_origen:
        return None  
    return camino, distancias



# def graficar_grafo(grafo, camino_resaltado=None):
#     # Crear un grafo dirigido usando NetworkX
#     G = nx.DiGraph()

#     # Añadir los nodos y las aristas con pesos
#     for nodo, vecinos in grafo.items():
#         for vecino, peso in vecinos.items():
#             G.add_edge(nodo, vecino, weight=peso)

#     # Obtener las posiciones de los nodos para la gráfica
#     # nx.spring_layout es un algoritmo de disposición (layout)
#     pos = nx.spring_layout(G, seed=42)

#     # Dibujar nodos y etiquetas
#     nx.draw(
#         G, 
#         pos, 
#         with_labels=True, 
#         node_color='lightblue', 
#         node_size=2000, 
#         font_size=10, 
#         font_weight='bold'
#     )

#     # Dibujar las etiquetas de las aristas (pesos)
#     labels = nx.get_edge_attributes(G, 'weight')
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10)

#     if camino_resaltado:
#         # Crear lista de aristas del camino (ej: A->B, B->C)
#         aristas_camino = list(zip(camino_resaltado, camino_resaltado[1:]))
        
#         # Dibujar nodos del camino en rojo
#         nx.draw_networkx_nodes(G, pos, nodelist=camino_resaltado, node_color='orange', node_size=2000)
        
#         # Dibujar aristas del camino en rojo y más gruesas
#         nx.draw_networkx_edges(G, pos, edgelist=aristas_camino, edge_color='red', width=2.5)
        
#         print(f"\n--> Camino visualizado en el gráfico: {' -> '.join(camino_resaltado)}")

#     # Mostrar la gráfica
#     plt.title("Representación gráfica del grafo")
#     plt.show()

# --- Ejemplo de uso del código ---

# Define el grafo en el formato esperado:
# {Origen: {Destino: Peso, ...}, ...}

if __name__ == "__main__":

    grafo = {
        'A1': {'A2':1, 'B1':1},
        'A2': {'A1':1, 'B2':1, 'A3':1},
        'A3': {'A2':1, 'B3':1},
        'B1': {'A1':1, 'B2':1, 'C1':1},
        'B2': {'B1':1, 'B3':1, 'A2':1, 'C2':1},
        'B3': {'B2':1, 'A3':1, 'C3':1},
        'C1': {'C2':1, 'B1':1},
        'C2': {'C1':1, 'B2':1, 'C3':1},
        'C3': {'C2':1, 'B3':1},
    }

    origen = 'A1'
    destino = 'C3'

    # Ejecutar djkstra desde el nodo 'a'
    # distancias, predecesores = dijkstra(grafo, origen)
    # camino = reconstruir_camino(predecesores, origen, destino)
    # costo_total = distancias[destino]

    camino, distancias = calcular_camino(grafo, origen, destino)
    costo_total = distancias[destino]

    if camino:
        print("----------------RESULTADOS----------------")
        print(f"Origen: {origen}")
        print(f"Destino: {destino}")
        print(f"Ruta más corta: {' -> '.join(camino)}")
        print(f"Siguiente calle: {camino[1]}")
        print(f"Costo total: {costo_total}")
        print("------------------------------------------")
        
        # graficar_grafo(grafo, camino_resaltado=camino)
    else:
        print(f"No existe un camino entre {origen} y {destino}")