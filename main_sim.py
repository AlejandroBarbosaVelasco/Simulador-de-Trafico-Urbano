# main_sim.py
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathfinder import astar
from city_map import GRID_SIZE, create_intersection_locks, generate_traffic_lights
from vehicle import Vehicle

# Configuración
NUM_VEHICLES = 25   # Cambia aquí: entre 20 y 30
NUM_TRAFFIC_LIGHTS = 12
SEED = 42

# Genera locks y semáforos
intersection_locks = create_intersection_locks()
traffic_lights = generate_traffic_lights(num_lights=NUM_TRAFFIC_LIGHTS, seed=SEED)

# Generar pares start/goal en los bordes
def random_border_pos(grid_size):
    side = random.choice(["top","bottom","left","right"])
    if side == "top":
        return (0, random.randint(0, grid_size-1))
    if side == "bottom":
        return (grid_size-1, random.randint(0, grid_size-1))
    if side == "left":
        return (random.randint(0, grid_size-1), 0)
    return (random.randint(0, grid_size-1), grid_size-1)

random.seed(SEED)
vehicles_specs = []
for i in range(NUM_VEHICLES):
    while True:
        s = random_border_pos(GRID_SIZE)
        g = random_border_pos(GRID_SIZE)
        if g != s:
            break
    vehicles_specs.append((s, g))

# 1) Planificación secuencial
start_seq = time.perf_counter()
paths_seq = []
for (s,g) in vehicles_specs:
    p = astar(s, g, GRID_SIZE)
    paths_seq.append(p)
end_seq = time.perf_counter()
time_seq = end_seq - start_seq

# 2) Planificación en paralelo (ThreadPool)
start_par = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as exe:
    futures = [exe.submit(astar, s, g, GRID_SIZE) for (s,g) in vehicles_specs]
    paths_par = [f.result() for f in futures]
end_par = time.perf_counter()
time_par = end_par - start_par

print(f"Tiempo rutas secuencial: {time_seq:.4f} s")
print(f"Tiempo rutas paralelo:   {time_par:.4f} s")

# Para efectos de simulación usaremos las rutas calculadas (paths_par)
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

    vehicles.append(v)   # 👈 SE GUARDA EL OBJETO Vehicle

# Iniciar vehículos
for v in vehicles:
    v.start()

# Esperar a que terminen (con timeout máximo por seguridad)
timeout = 120  # segundos
t0 = time.time()
for v in vehicles:
    remaining = max(0, timeout - (time.time() - t0))
    v.join(timeout=remaining)

# Parar semáforos
for tl in traffic_lights.values():
    tl.stop()

print("Simulación finalizada.")
