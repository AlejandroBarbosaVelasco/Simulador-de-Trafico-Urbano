# city_map.py
import random
from traffic_light import TrafficLight
import threading

# Reutiliza tus constantes
GRID_SIZE = 12
BLOCK_SIZE = 40
STREET_WIDTH = 30

# Todas las intersecciones se mapean como nodos (r, c) con locks para sincronización
def create_intersection_locks():
    locks = {}
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            locks[(r, c)] = threading.Lock()
    return locks

def generate_traffic_lights(num_lights=12, seed=None, green_time=5, yellow_time=2, red_time=6):
    """
    Crea num_lights TrafficLight threads en posiciones aleatorias dentro de 1..GRID_SIZE-2.
    Devuelve dict: { (r,c): TrafficLight }
    """
    if seed is not None:
        random.seed(seed)

    available = [
        (r, c)
        for r in range(1, GRID_SIZE - 1)
        for c in range(1, GRID_SIZE - 1)
    ]
    random.shuffle(available)
    selected = available[:num_lights]

    lights = {}
    for pos in selected:
        tl = TrafficLight(pos, green_time=green_time, yellow_time=yellow_time, red_time=red_time)
        tl.start()
        lights[pos] = tl

    return lights
