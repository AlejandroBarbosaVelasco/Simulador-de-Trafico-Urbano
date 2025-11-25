# vehicle.py
import threading
import time

class Vehicle(threading.Thread):
    """
    Vehículo que sigue una ruta (lista de (r,c) pasos).
    Se asume:
    - intersection_locks: dict {(r,c): threading.Lock()}
    - traffic_lights: dict {(r,c): TrafficLight}  (puede faltar si no hay semáforo)
    """

    def __init__(self, vid, start, goal, path,
                 intersection_locks, traffic_lights,
                 step_time=0.3):
        super().__init__(daemon=True)
        self.vid = vid
        self.start_pos = start
        self.goal_pos = goal

        self.path = path[:]  # lista de nodos
        self.locks = intersection_locks
        self.traffic_lights = traffic_lights
        self.step_time = step_time
        self.finished = threading.Event()

    def can_enter_by_light(self, pos):
        """
        Comprueba semáforo en 'pos'. Solo permite entrada si no hay semáforo o está en GREEN.
        (Puedes adaptar la lógica para permitir YELLOW según comportamiento deseado.)
        """
        tl = self.traffic_lights.get(pos)
        if tl is None:
            return True
        return tl.current_color == "GREEN"

    def run(self):
        current = self.start_pos
        self.current_pos = current   # <<< NUEVO

        acquired = self.locks[current].acquire(timeout=5)
        if not acquired:
            print(f"[V{self.vid}] No pudo adquirir inicio {current}")
            self.finished.set()
            return

        for next_node in self.path[1:]:

            moved = False
            wait_start = time.time()

            while not moved:

                if not self.can_enter_by_light(next_node):
                    time.sleep(0.2)
                    continue

                got = self.locks[next_node].acquire(blocking=False)

                if got:
                    time.sleep(self.step_time)
                    self.locks[current].release()
                    current = next_node
                    self.current_pos = next_node   # <<< SE ACTUALIZA
                    moved = True
                else:
                    time.sleep(0.1)

                # Tiempo máximo esperando pasar
                if time.time() - wait_start > 10:
                    print(f"[V{self.vid}] Abortó por atasco en {next_node}")
                    self.finished.set()
                    return

            if current == self.goal_pos:
                break

        self.finished.set()


    def draw(self, screen, cell_size=40):
        # Convertir fila/columna a coordenadas de pantalla
        r, c = self.current_pos
        x = c * cell_size + cell_size // 2
        y = r * cell_size + cell_size // 2

        # Dibujar triángulo (pequeño)
        p1 = (x, y - 6)
        p2 = (x - 4, y + 6)
        p3 = (x + 4, y + 6)

        import pygame
        pygame.draw.polygon(screen, (255, 200, 0), [p1, p2, p3])
