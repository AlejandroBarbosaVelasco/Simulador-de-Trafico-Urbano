import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathfinder import astar
from city_map import GRID_SIZE, create_intersection_locks, generate_traffic_lights
from vehicle import Vehicle

import inspect
print("Vehicle viene del archivo:", inspect.getsourcefile(Vehicle))


# --------------------------
# CONFIGURACIÓN
# --------------------------
NUM_VEHICLES = 25
NUM_TRAFFIC_LIGHTS = 12
SEED = 42

intersection_locks = create_intersection_locks()
traffic_lights = generate_traffic_lights(num_lights=NUM_TRAFFIC_LIGHTS, seed=SEED)

def random_border_pos(grid_size):
    side = random.choice(["top","bottom","left","right"])
    if side == "top":
        return (0, random.randint(0, grid_size-1))
    if side == "bottom":
        return (grid_size-1, random.randint(0, grid_size-1))
    if side == "left":
        return (random.randint(0, grid_size-1), 0)
    return (random.randint(0, grid_size-1), grid_size-1)


# --------------------------
# GENERAR RUTAS
# --------------------------
random.seed(SEED)
vehicles_specs = []
for _ in range(NUM_VEHICLES):
    while True:
        s = random_border_pos(GRID_SIZE)
        g = random_border_pos(GRID_SIZE)
        if g != s:
            break
    vehicles_specs.append((s, g))

# Secuencial
start_seq = time.perf_counter()
paths_seq = []
for (s,g) in vehicles_specs:
    p = astar(s, g, GRID_SIZE)
    paths_seq.append(p)
end_seq = time.perf_counter()
time_seq = end_seq - start_seq

# Paralelo
start_par = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as exe:
    futures = [exe.submit(astar, s, g, GRID_SIZE) for (s,g) in vehicles_specs]
    paths_par = [f.result() for f in futures]
end_par = time.perf_counter()
time_par = end_par - start_par

print(f"Tiempo rutas secuencial: {time_seq:.4f} s")
print(f"Tiempo rutas paralelo:   {time_par:.4f} s")


# --------------------------
# CREAR VEHÍCULOS
# --------------------------
vehicles = []
for vid, ((s,g), path) in enumerate(zip(vehicles_specs, paths_par), start=1):
    if not path:
        print(f"[WARN] Vehículo {vid} sin ruta {s} -> {g}, ignorado")
        continue

    v = Vehicle(
        vid,
        s,
        g,
        path,
        intersection_locks,
        traffic_lights,
        step_time=0.15
    )
    vehicles.append(v)


# --------------------------
# INICIAR HILOS DE VEHÍCULOS
# --------------------------
for v in vehicles:
    v.start()


# --------------------------
# LOOP DE PYGAME
# --------------------------
import pygame
import sys

pygame.init()
CELL_SIZE = 40
WIDTH  = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Tráfico")
clock = pygame.time.Clock()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((50, 50, 50))

    # Dibujar cuadricula
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            pygame.draw.rect(
                screen,
                (100, 100, 100),
                (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                1
            )

    # Dibujar vehículos
    for v in vehicles:
        v.draw(screen, cell_size=CELL_SIZE)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


# --------------------------
# AHORA SÍ ESPERAR A QUE ACABEN
# --------------------------
timeout = 120
t0 = time.time()
for v in vehicles:
    remaining = max(0, timeout - (time.time() - t0))
    v.join(timeout=remaining)

for tl in traffic_lights.values():
    tl.stop()

print("Simulación finalizada.")
