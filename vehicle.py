# vehicle.py
import threading
import time
import math

class Vehicle(threading.Thread):

    def __init__(self, start_cell, end_cell, grid_to_pos, speed=2):
        super().__init__()

        # Conversión grid→píxel
        self.grid_to_pos = grid_to_pos

        # Ruta como lista de celdas
        self.route = self.calculate_route(start_cell, end_cell)

        # Convertimos la primera celda a posición en pantalla
        self.x, self.y = grid_to_pos(self.route[0])

        # Target actual (la siguiente intersección)
        self.next_index = 1  
        self.speed = speed
        self.running = True

    def calculate_route(self, start, end):
        """
        Ruta recta estilo Manhattan
        """
        route = []
        r1, c1 = start
        r2, c2 = end

        # mover filas
        step = 1 if r1 <= r2 else -1
        for r in range(r1, r2 + step, step):
            route.append((r, c1))

        # mover columnas
        step = 1 if c1 <= c2 else -1
        for c in range(c1 + step, c2 + step, step):
            route.append((r2, c))

        return route

    def run(self):
        while self.running:

            # ¿Llegó al destino final?
            if self.next_index >= len(self.route):
                time.sleep(0.02)
                continue

            # Punto objetivo
            tx, ty = self.grid_to_pos(self.route[self.next_index])

            # Dirección normalizada
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist < 1:  # llegó a la intersección
                self.next_index += 1
                continue

            dx /= dist
            dy /= dist

            # Avanzar en línea recta
            self.x += dx * self.speed
            self.y += dy * self.speed

            time.sleep(0.02)

    def stop(self):
        self.running = False

    def get_pixel_position(self):
        return (int(self.x), int(self.y))
