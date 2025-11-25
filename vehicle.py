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
        self.start = start
        self.goal = goal
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
        # Adquirir lock del nodo inicial para indicar ocupación
        current = self.start
        acquired = self.locks[current].acquire(timeout=5)
        if not acquired:
            # no pudo adquirir nodo inicial -> abandona
            print(f"[V{self.vid}] No pudo adquirir inicio {current}")
            self.finished.set()
            return

        # Recorre path (primer elemento debe ser start)
        for next_node in self.path[1:]:
            moved = False
            while not moved:
                # Checar semáforo (si existe) y status del lock del next_node
                if not self.can_enter_by_light(next_node):
                    # semáforo no permite, esperar
                    time.sleep(0.2)
                    continue

                # Intentar adquirir el lock del siguiente nodo sin bloquear indefinidamente
                got = self.locks[next_node].acquire(blocking=False)
                if got:
                    # Movimiento: adquirimos next_node -> soltamos current
                    # (estrategia: acquire next then release current para evitar huecos)
                    time.sleep(self.step_time)  # simula desplazamiento entre nodos
                    self.locks[current].release()
                    current = next_node
                    moved = True
                else:
                    # No pudo adquirir (ocupado), esperar
                    time.sleep(0.1)

            # si llegó al destino último, termina
            if current == self.goal:
                break

        # Liberar lock final (si aún lo tiene)
        if self.locks[current].locked():
            try:
                self.locks[current].release()
            except RuntimeError:
                # ya liberado por alguna razón
                pass

        self.finished.set()
        # print(f"[V{self.vid}] Llegó a destino {self.goal}")
