# city_map.py
import random
from traffic_light import TrafficLight
from vehicle import Vehicle

GRID_SIZE = 12
BLOCK_SIZE = 40
STREET_WIDTH = 30


def generate_traffic_lights():

    lights = []

    # Posiciones válidas para intersecciones internas
    available = [
        (r, c)
        for r in range(1, GRID_SIZE - 1)
        for c in range(1, GRID_SIZE - 1)
    ]

    random.shuffle(available)

    for (r, c) in available[:12]:

        # Conversión de coordenadas de grid → píxeles
        x = c * (BLOCK_SIZE + STREET_WIDTH) - STREET_WIDTH
        y = r * (BLOCK_SIZE + STREET_WIDTH) - STREET_WIDTH

        semaforo = TrafficLight(x, y)

        # Iniciar hilo del semáforo
        semaforo.start()
        lights.append(semaforo)

    return lights


def generate_vehicles(n=20):
    vehicles = []

    # Todas las celdas de intersección
    cells = [
        (r, c)
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
    ]

    # Convertir celda → coordenada pixel en el cruce
    def grid_to_pos(cell):
        r, c = cell
        x = c * (BLOCK_SIZE + STREET_WIDTH)
        y = r * (BLOCK_SIZE + STREET_WIDTH)
        return (x, y)

    for _ in range(n):

        start = random.choice(cells)
        end   = random.choice(cells)

        while end == start:
            end = random.choice(cells)

        v = Vehicle(start, end, grid_to_pos)
        print(f"Posicion inicial: {start} Posicion final: {end}")
        v.start()
        vehicles.append(v)

    return vehicles
