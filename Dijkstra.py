import heapq
import networkx as nx
import matplotlib.pyplot as plt

def dijkstra(grafo, nodo_origen):
    # Inicializar las distancias mas cortas conocidas como infinito
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[nodo_origen] = 0 # La distancia de inicio con el nodo origen es 0

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
                #Agregar el vecino a la cola de prioridad
                heapq.heappush(cola_prioridad, (nueva_distancia, vecino))
    
    return distancias

def graficar_grafo(grafo):
    # Crear un grafo dirigido usando NetworkX
    G = nx.DiGraph()

    # Añadir los nodos y las aristas con pesos
    for nodo, vecinos in grafo.items():
        for vecino, peso in vecinos.items():
            G.add_edge(nodo, vecino, weight=peso)

    # Obtener las posiciones de los nodos para la gráfica
    # nx.spring_layout es un algoritmo de disposición (layout)
    pos = nx.spring_layout(G)

    # Dibujar nodos y etiquetas
    nx.draw(
        G, 
        pos, 
        with_labels=True, 
        node_color='lightblue', 
        node_size=2000, 
        font_size=10, 
        font_weight='bold'
    )

    # Dibujar las etiquetas de las aristas (pesos)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=10)

    # Mostrar la gráfica
    plt.title("Representación gráfica del grafo")
    plt.show()

# --- Ejemplo de uso del código ---

# Define el grafo en el formato esperado:
# {Origen: {Destino: Peso, ...}, ...}
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

# Ejecutar djkstra desde el nodo 'a'
resultado = dijkstra(grafo, 'A1')

# Mostrar las distancias mas cortas desde 'a'
print("Distancias mas cortas desde '0': ")
for nodo, distancia in resultado.items():
    print(f'Nodo {nodo}: {distancia}')


# Llama a la función con el ejemplo
graficar_grafo(grafo)