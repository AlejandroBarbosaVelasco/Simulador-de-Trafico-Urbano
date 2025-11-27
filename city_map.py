# city_map.py
import random
import threading
from traffic_light import TrafficLight
from vehicle import Vehicle

GRID_SIZE = 12
BLOCK_SIZE = 40
STREET_WIDTH = 30

# Crear locks para cada intersección
intersection_locks = [
    [threading.Lock() for _ in range(GRID_SIZE)]
    for _ in range(GRID_SIZE)
]


# ==========================================================
# GENERAR SEMÁFOROS
# ==========================================================
def generate_traffic_lights(green_time, yellow_time, red_time):
    lights = []

    # Solo intersecciones internas
    available = [
        (r, c)
        for r in range(1, GRID_SIZE - 1)
        for c in range(1, GRID_SIZE - 1)
    ]

    random.shuffle(available)

    for (r, c) in available[:20]:

        # Convertir grid → pixeles
        x = c * (BLOCK_SIZE + STREET_WIDTH) - STREET_WIDTH
        y = r * (BLOCK_SIZE + STREET_WIDTH) - STREET_WIDTH

        sem = TrafficLight(x, y, green_time, yellow_time, red_time)
        sem.row = r
        sem.col = c
        sem.start()

        lights.append(sem)

    return lights


# ==========================================================
# GENERAR VEHÍCULOS
# ==========================================================
def generate_vehicles(n, traffic_lights):

    vehicles = []

    cells = [
        (r, c)
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
    ]

    def grid_to_pos(cell):
        r, c = cell
        x = c * (BLOCK_SIZE + STREET_WIDTH)
        y = r * (BLOCK_SIZE + STREET_WIDTH)
        return (x, y)

    for _ in range(n):

        start = random.choice(cells)
        end = random.choice(cells)

        while end == start:
            end = random.choice(cells)

        v = Vehicle(
            start, end,
            grid_to_pos,
            traffic_lights,
            intersection_locks
        )

        v.start()
        vehicles.append(v)

    return vehicles
