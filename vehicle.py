# vehicle.py
import threading
import time
import heapq
import math
class Vehicle(threading.Thread):

    def __init__(self, start_cell, end_cell, grid_to_pos, 
                 traffic_lights, intersection_locks, speed=2):
        super().__init__()

        self.grid_to_pos = grid_to_pos
        self.traffic_lights = traffic_lights
        self.intersection_locks = intersection_locks

        # Ruta como lista de celdas
        self.route = self.calculate_route(start_cell, end_cell)

        # Posición de la celda actual
        self.row, self.col = self.route[0]

        # Posición en píxeles
        self.x, self.y = grid_to_pos(self.route[0])

        self.next_index = 1
        self.speed = speed
        self.running = True

        self.current_lock = None


    # -------------------------------------------------


    # -------------------------------------------------
    def calculate_route(self, start, end):
        """
        Planeación de ruta usando A* sobre la cuadrícula.
        """

        start_r, start_c = start
        end_r, end_c = end

        # Cola de prioridad (f, (r,c))
        pq = []
        heapq.heappush(pq, (0, start))

        came_from = {start: None}
        g_score = {start: 0}

        def heuristic(a, b):
            # Distancia Manhattan
            ar, ac = a
            br, bc = b
            return abs(ar - br) + abs(ac - bc)

        while pq:
            _, current = heapq.heappop(pq)

            if current == end:
                break

            r, c = current

            # Vecinos válidos (arriba, abajo, izquierda, derecha)
            neighbors = [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1)
            ]

            for nr, nc in neighbors:
                # Dentro de límites
                if 0 <= nr < 12 and 0 <= nc < 12:

                    tentative_g = g_score[current] + 1

                    if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                        g_score[(nr, nc)] = tentative_g
                        f = tentative_g + heuristic((nr, nc), end)
                        heapq.heappush(pq, (f, (nr, nc)))
                        came_from[(nr, nc)] = current

        # Reconstruir ruta
        route = []
        node = end

        while node:
            route.append(node)
            node = came_from.get(node)

        route.reverse()
        return route



    # -------------------------------------------------
    def get_traffic_light(self, row, col):
        """
        Busca si hay un semáforo en esa intersección
        """
        for sem in self.traffic_lights:
            if sem.row == row and sem.col == col:
                return sem
        return None


    # -------------------------------------------------
    def compute_next_position(self):
        """
        Obtiene la siguiente celda en la ruta
        """
        if self.next_index >= len(self.route):
            return self.row, self.col  # Llegó al destino

        return self.route[self.next_index]


    # -------------------------------------------------
    def run(self):
        while self.running:

            next_row, next_col = self.compute_next_position()

            # Ya llegó al destino
            if (next_row, next_col) == (self.row, self.col):
                time.sleep(0.1)
                continue

            # 1) Checar semáforo
            sem = self.get_traffic_light(next_row, next_col)
            if sem:
                while not sem.is_green() and self.running:
                    time.sleep(0.2)

            # 2) Intentar adquirir lock del cruce
            lock = self.intersection_locks[next_row][next_col]
            acquired = lock.acquire(blocking=False)

            while not acquired and self.running:
                time.sleep(0.2)
                acquired = lock.acquire(blocking=False)

            # Si tenía otro lock, liberarlo
            if self.current_lock:
                try:
                    self.current_lock.release()
                except RuntimeError:
                    pass

            self.current_lock = lock

            # Avanzar a la nueva celda
            self.row, self.col = next_row, next_col
            self.x, self.y = self.grid_to_pos((self.row, self.col))
            self.next_index += 1

            time.sleep(0.15)


    # -------------------------------------------------
    def stop(self):
        self.running = False
        if self.current_lock:
            try:
                self.current_lock.release()
            except RuntimeError:
                pass

    # -------------------------------------------------
    def get_pixel_position(self):
        return int(self.x), int(self.y)
