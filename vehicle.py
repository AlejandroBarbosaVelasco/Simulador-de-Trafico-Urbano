# vehicle.py
import threading
import time
import heapq
import random

GRID_SIZE = 12  # asegúrate que coincide con city_map.GRID_SIZE si lo exportas

class Vehicle(threading.Thread):

    def __init__(self, start_cell, end_cell, grid_to_pos, traffic_lights, intersection_locks, speed=0.2):
        super().__init__()

        self.grid_to_pos = grid_to_pos
        self.traffic_lights = traffic_lights
        self.intersection_locks = intersection_locks

        # Ruta como lista de celdas (A*)
        self.route = self.calculate_route(start_cell, end_cell)

        # Información para debug
        print(f"[INFO] Vehículo {id(self)} creado. Ruta: {start_cell} -> {end_cell}. Pasará por {len(self.route)} celdas.")

        # Posición de la celda actual
        self.row, self.col = self.route[0]

        # Posición en píxeles
        self.x, self.y = grid_to_pos(self.route[0])

        self.next_index = 1
        self.speed = speed
        self.running = True

        self.current_lock = None

        self.execution_time = 0.0

    # -------------------------------------------------
    def calculate_route(self, start, end):
        """
        Planeación de ruta usando A* sobre la cuadrícula.
        """
        start_r, start_c = start
        end_r, end_c = end

        pq = []
        heapq.heappush(pq, (0, start))

        came_from = {start: None}
        g_score = {start: 0}

        def heuristic(a, b):
            ar, ac = a
            br, bc = b
            return abs(ar - br) + abs(ac - bc)

        while pq:
            _, current = heapq.heappop(pq)

            if current == end:
                break

            r, c = current

            neighbors = [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1)
            ]

            for nr, nc in neighbors:
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:

                    tentative_g = g_score[current] + 1

                    if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                        g_score[(nr, nc)] = tentative_g
                        f = tentative_g + heuristic((nr, nc), end)
                        heapq.heappush(pq, (f, (nr, nc)))
                        came_from[(nr, nc)] = current

        route = []
        node = end

        # Si no hay camino (por algún bug), devolvemos [start] para no romper nada
        if end not in came_from:
            return [start]

        while node:
            route.append(node)
            node = came_from.get(node)

        route.reverse()
        return route

    # -------------------------------------------------
    def get_traffic_light(self, row, col):
        for sem in self.traffic_lights:
            # asumimos que cada semaforo tiene sem.row y sem.col (como en city_map)
            if getattr(sem, "row", None) == row and getattr(sem, "col", None) == col:
                return sem
        return None

    # -------------------------------------------------
    def compute_next_position(self):
        if self.next_index >= len(self.route):
            return self.row, self.col  # Llegó al destino

        return self.route[self.next_index]

    # -------------------------------------------------
    def run(self):
        start_time = time.perf_counter()
        print(f"[START] Vehículo {id(self)} inició su recorrido.")
        try:
            while self.running:

                next_row, next_col = self.compute_next_position()

                # Ya llegó al destino
                if (next_row, next_col) == (self.row, self.col):
                    if self.next_index >= len(self.route):

                        # Calcular el tiempo en total
                        end_time = time.perf_counter()
                        self.execution_time = end_time - start_time

                        print(f"[OK] Vehículo {id(self)} llegó a su destino final en {self.route[-1]}")
                        print(f"[TIME] Tiempo total de ejecución: {self.execution_time:.4f} segundos")
                        self.running = False
                        # liberar si por casualidad aún tiene lock
                        if self.current_lock:
                            try:
                                self.current_lock.release()
                            except RuntimeError:
                                pass
                            self.current_lock = None
                        break
                    time.sleep(0.1)
                    continue

                # 1) Semáforo: si existe y está rojo, esperar hasta verde
                sem = self.get_traffic_light(next_row, next_col)
                if sem:
                    # while not sem.is_green() and self.running:
                    while not sem.is_green() and self.running and not sem.is_yellow():
                        time.sleep(0.2)

                # 2) Estrategia de locking (evitar deadlocks):
                #    Liberamos el lock actual antes de intentar adquirir el siguiente.
                #    Esto evita espera circular entre vehículos adyacentes.
                if self.current_lock:
                    try:
                        self.current_lock.release()
                    except RuntimeError:
                        pass
                    self.current_lock = None

                lock = self.intersection_locks[next_row][next_col]

                # Intentar adquirir el lock objetivo con backoff
                acquired = lock.acquire(blocking=False)
                tries = 0
                while not acquired and self.running:
                    # backoff con algo de aleatoriedad para reducir contención
                    time.sleep(0.05 + random.random() * 0.15)
                    acquired = lock.acquire(blocking=False)
                    tries += 1
                    # diagnóstico si está demasiado tiempo esperando
                    if tries == 50:
                        print(f"[WARN] Vehículo {id(self)} esperando mucho por intersección {(next_row, next_col)}")

                if not self.running:
                    # si se pidió stop mientras esperaba, asegurarnos de no quedarnos con lock
                    if acquired:
                        try:
                            lock.release()
                        except RuntimeError:
                            pass
                    break

                # Al adquirir el lock del objetivo, lo marcamos como current_lock
                self.current_lock = lock

                # Avanzar a la nueva celda
                self.row, self.col = next_row, next_col
                self.x, self.y = self.grid_to_pos((self.row, self.col))
                self.next_index += 1

                time.sleep(0.05)
        finally:
            # --- Calcular tiempo si se detuvo abruptamente (stop) ---
            # Esto asegura que si llamas a stop(), también tengas un registro del tiempo que corrió.
            if self.execution_time == 0.0:
                 self.execution_time = time.perf_counter() - start_time
                 print(f"[STOP] Vehículo detenido. Tiempo corrido: {self.execution_time:.4f} s")

    # -------------------------------------------------
    def stop(self):
        self.running = False
        # intentar soltar lock si se tiene
        if self.current_lock:
            try:
                self.current_lock.release()
            except RuntimeError:
                pass
            self.current_lock = None

    # -------------------------------------------------
    def get_pixel_position(self):
        return int(self.x), int(self.y), self.running
