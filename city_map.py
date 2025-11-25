# city_map.py
import random
from traffic_light import TrafficLight

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
