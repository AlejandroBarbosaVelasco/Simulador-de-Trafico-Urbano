# traffic_light.py
import threading
import time

class TrafficLight(threading.Thread):

    def __init__(self, x, y, 
                 green_time=5, yellow_time=2, red_time=6):
        super().__init__()

        self.x = x
        self.y = y
        
        self.green_time  = green_time
        self.yellow_time = yellow_time
        self.red_time    = red_time

        self.current_color = (255, 0, 0)  # Empieza en rojo
        self.running = True

    def run(self):
        """
        Ciclo infinito cambiando entre verde → amarillo → rojo.
        """
        while self.running:

            # Verde
            self.current_color = (0, 220, 0)
            time.sleep(self.green_time)

            # Amarillo
            self.current_color = (240, 220, 0)
            time.sleep(self.yellow_time)

            # Rojo
            self.current_color = (220, 40, 40)
            time.sleep(self.red_time)

    def stop(self):
        self.running = False
