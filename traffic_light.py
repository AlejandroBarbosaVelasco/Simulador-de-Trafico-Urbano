# traffic_light.py
import threading
import time

class TrafficLight(threading.Thread):
    """
    Semáforo independiente que cicla Green -> Yellow -> Red.
    current_color: "GREEN", "YELLOW", "RED"
    """

    COLORS = {
        "GREEN": (0, 220, 0),
        "YELLOW": (240, 220, 0),
        "RED": (220, 40, 40)
    }

    def __init__(self, pos, green_time=5.0, yellow_time=2.0, red_time=6.0):
        super().__init__(daemon=True)
        self.pos = pos  # (row, col)
        self.green_time = green_time
        self.yellow_time = yellow_time
        self.red_time = red_time

        self.current_color = "RED"
        self._running = threading.Event()
        self._running.set()

    def run(self):
        while self._running.is_set():
            # Verde
            self.current_color = "GREEN"
            time.sleep(self.green_time)
            # Amarillo
            self.current_color = "YELLOW"
            time.sleep(self.yellow_time)
            # Rojo
            self.current_color = "RED"
            time.sleep(self.red_time)

    def stop(self):
        self._running.clear()

    def color_rgb(self):
        return self.COLORS[self.current_color]
