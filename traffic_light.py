# traffic_light.py
import threading
import time
import random

class TrafficLight(threading.Thread):

    def __init__(self, x, y, 
                 green_time=5, yellow_time=2, red_time=6):
        super().__init__()

        self.x = x
        self.y = y
        
        self.green_time  = green_time
        self.yellow_time = yellow_time
        self.red_time    = red_time

        # El semáforo empieza aleatoriamente en verde o rojo
        self.current_color = random.choice([
            (0, 220, 0),     # Verde
            (220, 40, 40)    # Rojo
        ])

        self.running = True

    def is_green(self):
        return self.current_color == (0, 220, 0)

    def run(self):
        """
        Ciclo infinito cambiando entre verde → amarillo → rojo.
        """

        # Pequeño desfase para que no todos estén sincronizados
        time.sleep(random.uniform(0.2, 2.0))

        while self.running:

            # 🔵 Verde
            self.current_color = (0, 220, 0)
            time.sleep(self.green_time)

            # 🟡 Amarillo
            self.current_color = (240, 220, 0)
            time.sleep(self.yellow_time)

            # 🔴 Rojo
            self.current_color = (220, 40, 40)
            time.sleep(self.red_time)

    def stop(self):
        self.running = False
