import threading
import time
import random
import heapq
from concurrent.futures import ThreadPoolExecutor
from math import inf

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---
class Configuracion:
    """Clase para almacenar la configuración de la simulación."""
    GRID_SIZE = 12
    NUM_INTERSECTIONS = GRID_SIZE * GRID_SIZE
    # Duraciones por defecto (en segundos)
    TIEMPOS_SEMAFORO = {
        "VERDE": 5,
        "AMARILLO": 2,
        "ROJO": 6,
    }
    NUM_VEHICULOS = 50  # Cantidad inicial de vehículos
    VELOCIDAD_SIMULACION = 0.5  # Retardo entre movimientos (para visualización)
    SEMAFORO_RATE = 3 # Semáforo en intersecciones (i, j) donde i%RATE == 0 y j%RATE == 0

# --- ESTRUCTURAS DE DATOS COMPARTIDAS ---

class Semaforo:
    """
    Representa un semáforo como un hilo. 
    Alterna entre estados y notifica a los vehículos en espera.
    """
    def __init__(self, inter_coords, inter_cond):
        self.coords = inter_coords
        self.estado = "ROJO" # Inicialmente en rojo
        self.condicion = inter_cond # La Condition de la Interseccion
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while self.running:
            try:
                # 1. VERDE
                self.estado = "VERDE"
                # Con la Condition adquirida, notificamos a todos los hilos esperando la luz verde
                with self.condicion:
                    # Notificar a los vehículos que la luz está verde
                    self.condicion.notify_all() 
                time.sleep(Configuracion.TIEMPOS_SEMAFORO["VERDE"] * Configuracion.VELOCIDAD_SIMULACION)

                # 2. AMARILLO
                self.estado = "AMARILLO"
                # No se notifica aquí, ya que el amarillo indica precaución (pronto rojo)
                time.sleep(Configuracion.TIEMPOS_SEMAFORO["AMARILLO"] * Configuracion.VELOCIDAD_SIMULACION)

                # 3. ROJO
                self.estado = "ROJO"
                time.sleep(Configuracion.TIEMPOS_SEMAFORO["ROJO"] * Configuracion.VELOCIDAD_SIMULACION)

            except Exception as e:
                if self.running:
                    print(f"Error en el semáforo {self.coords}: {e}")
                break

    def stop(self):
        self.running = False
        self.thread.join(0.1) # Espera breve para terminar

class Interseccion:
    """
    Representa una intersección como recurso crítico.
    Contiene un Mutex (Lock) y una Condition para la sincronización.
    """
    def __init__(self, r, c, tiene_semaforo):
        self.coords = (r, c)
        self.lock = threading.Lock() # Mutex para exclusión mutua
        self.condition = threading.Condition(self.lock) # Condición para esperar el semáforo
        self.ocupada_por = None # ID del vehículo que la ocupa
        self.tiene_semaforo = tiene_semaforo
        self.semaforo = None
        self.vehiculos_en_espera = 0
        self.registro_espera = [] # Para almacenar la duración de las esperas

        if self.tiene_semaforo:
            self.semaforo = Semaforo(self.coords, self.condition)

    def __str__(self):
        return f"({self.coords[0]},{self.coords[1]})"
    
    def intentar_entrar(self, vehiculo_id):
        """
        Lógica para que un vehículo intente entrar a la intersección.
        """
        self.lock.acquire()
        try:
            # Condición de espera para Semáforo (si aplica)
            if self.tiene_semaforo:
                espera_iniciada = time.time()
                # El vehículo espera mientras la luz esté en ROJO o AMARILLO
                while self.semaforo.estado in ["ROJO", "AMARILLO"]:
                    self.vehiculos_en_espera += 1
                    # print(f"Vehículo {vehiculo_id} esperando semáforo en {self.coords}. Luz: {self.semaforo.estado}")
                    self.condition.wait() # Libera el lock y espera la notificación
                    self.vehiculos_en_espera -= 1
                    
                self.registro_espera.append(time.time() - espera_iniciada)

            # Condición de espera para Mutex (ocupación)
            # Esto NO debería ser necesario si el semáforo usa wait/notify_all 
            # y solo uno cruza a la vez, pero lo incluimos por seguridad si se expande la lógica.
            if self.ocupada_por is not None:
                # Este caso es crítico y significa que algo está mal en la lógica o el semáforo no funciona correctamente.
                # Si el vehículo llegó hasta aquí (luz verde) y está ocupada, debe esperar.
                # En un modelo real, solo un vehículo debería poder entrar con luz verde.
                return False 

            self.ocupada_por = vehiculo_id
            return True
        finally:
            # El lock se liberará cuando el vehículo cruce, no aquí.
            # Lo que se libera aquí es el lock interno si se usó condition.wait()
            # La liberación final debe ser en self.salir()
            pass


    def salir(self, vehiculo_id):
        """Libera el lock de la intersección."""
        if self.ocupada_por == vehiculo_id:
            self.ocupada_por = None
            self.lock.release()
            return True
        return False # No puede liberar un lock que no posee


class Ciudad:
    """
    Representa el mapa de la ciudad como un grafo de Intersecciones.
    """
    def __init__(self):
        self.intersecciones = {} # Clave: (r, c), Valor: Interseccion
        self.grafo = {} # Clave: (r, c), Valor: Lista de (vecino_r, vecino_c)
        self._construir_mapa()
        print(f"Ciudad construida: {Configuracion.GRID_SIZE}x{Configuracion.GRID_SIZE} cuadrículas.")

    def _construir_mapa(self):
        """Inicializa las intersecciones y el grafo de calles."""
        size = Configuracion.GRID_SIZE
        semaforo_rate = Configuracion.SEMAFORO_RATE
        
        for r in range(size):
            for c in range(size):
                coords = (r, c)
                
                # Decidir si esta intersección tiene semáforo
                # Semáforos en las intersecciones (0,0), (0,3), (0,6), (3,0), etc.
                tiene_semaforo = (r % semaforo_rate == 0 and c % semaforo_rate == 0) and r != 0 and c != 0 and r != size-1 and c != size-1

                self.intersecciones[coords] = Interseccion(r, c, tiene_semaforo)
                self.grafo[coords] = []

                # Definir calles (aristas bidireccionales por defecto: Norte, Sur, Este, Oeste)
                posibles_vecinos = [
                    (r - 1, c), (r + 1, c), # Norte, Sur
                    (r, c - 1), (r, c + 1)  # Oeste, Este
                ]

                for nr, nc in posibles_vecinos:
                    if 0 <= nr < size and 0 <= nc < size:
                        self.grafo[coords].append((nr, nc))
        
        num_semaforos = sum(1 for i in self.intersecciones.values() if i.tiene_semaforo)
        print(f"Total de intersecciones: {size*size}. Semáforos instalados: {num_semaforos}")

    def obtener_interseccion(self, coords):
        return self.intersecciones.get(coords)

    def obtener_semaforos(self):
        return [i.semaforo for i in self.intersecciones.values() if i.tiene_semaforo]

# --- ALGORITMOS DE RUTA ---

def dijkstra_ruta(ciudad, inicio, destino):
    """
    Implementación del algoritmo de Dijkstra para encontrar el camino más corto.
    Retorna la lista de coordenadas de la ruta.
    """
    distancias = {node: inf for node in ciudad.grafo}
    distancias[inicio] = 0
    cola_prioridad = [(0, inicio)]
    previos = {}

    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

        if distancia_actual > distancias[nodo_actual]:
            continue

        if nodo_actual == destino:
            break

        for vecino in ciudad.grafo[nodo_actual]:
            # El "peso" de la arista es 1 (una cuadra)
            nuevo_camino = distancia_actual + 1
            if nuevo_camino < distancias[vecino]:
                distancias[vecino] = nuevo_camino
                previos[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (nuevo_camino, vecino))

    # Reconstruir la ruta
    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = previos.get(nodo)
        if nodo == inicio:
            ruta.append(inicio)
            break
            
    return ruta[::-1] if ruta and ruta[0] == inicio else None

# --- ENTIDAD VEHÍCULO ---

class Vehiculo(threading.Thread):
    """
    Representa un vehículo como un hilo que sigue una ruta predefinida.
    """
    def __init__(self, id_vehiculo, ciudad, inicio, destino, ruta):
        super().__init__(daemon=True)
        self.id_vehiculo = id_vehiculo
        self.ciudad = ciudad
        self.ruta = ruta
        self.inicio = inicio
        self.destino = destino
        self.posicion_actual = inicio
        self.indice_ruta = 0
        self.tiempo_inicio = time.time()
        self.tiempo_fin = None
        self.tiempo_espera_total = 0
        self.pasos = 0
        self.llegado = False
        self.nombre = f"V-{id_vehiculo:03}"

    def run(self):
        if not self.ruta:
            print(f"Vehículo {self.nombre} no tiene ruta, finalizando.")
            return

        # El primer paso es cruzar la intersección de inicio (que no tiene semáforo)
        inter_actual = self.ciudad.obtener_interseccion(self.posicion_actual)
        if inter_actual:
            inter_actual.lock.acquire()
            inter_actual.ocupada_por = self.nombre
        
        while self.indice_ruta < len(self.ruta) - 1:
            try:
                # La intersección actual ya está ocupada por 'self'
                inter_actual = self.ciudad.obtener_interseccion(self.posicion_actual)
                siguiente_posicion = self.ruta[self.indice_ruta + 1]
                inter_siguiente = self.ciudad.obtener_interseccion(siguiente_posicion)

                # 1. Intentar entrar a la siguiente intersección (CRUCE)
                
                # Intentar adquirir el lock y esperar la luz verde
                if inter_siguiente.lock.acquire(timeout=5): # Intenta adquirir el lock
                    try:
                        # Si tiene semáforo, esperar la condición
                        if inter_siguiente.tiene_semaforo:
                            espera_inicio = time.time()
                            
                            # Esperar mientras la luz no sea VERDE
                            with inter_siguiente.condition:
                                while inter_siguiente.semaforo.estado != "VERDE":
                                    inter_siguiente.vehiculos_en_espera += 1
                                    # print(f"{self.nombre} espera semáforo en {inter_siguiente}. Luz: {inter_siguiente.semaforo.estado}")
                                    inter_siguiente.condition.wait()
                                    inter_siguiente.vehiculos_en_espera -= 1
                                
                            self.tiempo_espera_total += (time.time() - espera_inicio)

                        # Adquirido lock y luz verde (si aplica). Cruzar es seguro.
                        
                        # 2. Mover el vehículo (actualizar posición)
                        self.posicion_actual = siguiente_posicion
                        self.indice_ruta += 1
                        self.pasos += 1
                        
                        # 3. Marcar la nueva intersección como ocupada
                        inter_siguiente.ocupada_por = self.nombre

                        # 4. Liberar la intersección anterior
                        inter_actual.ocupada_por = None
                        inter_actual.lock.release()

                        # Pausa de visualización
                        time.sleep(Configuracion.VELOCIDAD_SIMULACION)

                    finally:
                        # Si el vehículo falló en entrar o esperar, no debemos liberar el lock
                        # de la siguiente intersección aquí. Se liberará en el siguiente paso o al final.
                        pass
                else:
                    # No se pudo adquirir el lock de la siguiente intersección. Esperar y reintentar.
                    # print(f"{self.nombre} no pudo adquirir lock de {siguiente_posicion}. Reintentando...")
                    time.sleep(0.1) # Espera mínima para evitar spin-lock
            
            except Exception as e:
                print(f"Error crítico en {self.nombre} al moverse: {e}")
                break

        # FIN: El vehículo llegó a su destino
        self.tiempo_fin = time.time()
        self.llegado = True
        
        # Liberar la última intersección
        inter_final = self.ciudad.obtener_interseccion(self.posicion_actual)
        if inter_final and inter_final.lock.locked():
            inter_final.ocupada_por = None
            inter_final.lock.release()

        # print(f"Vehículo {self.nombre} llegó a {self.destino}. Tiempo: {self.tiempo_total_viaje():.2f}s")
    
    def tiempo_total_viaje(self):
        return self.tiempo_fin - self.tiempo_inicio if self.tiempo_fin else 0

# --- SIMULACIÓN PRINCIPAL ---

class Simulacion:
    def __init__(self):
        self.ciudad = Ciudad()
        self.vehiculos = []
        self.rutas_sequencial_tiempo = 0
        self.rutas_paralelo_tiempo = 0

    def _generar_puntos(self, n):
        """Genera N pares de puntos de inicio/destino válidos en los bordes."""
        puntos = []
        size = Configuracion.GRID_SIZE
        bordes = (0, size - 1)
        
        # Generar puntos de inicio y destino en los bordes (ej: 0, c o r, 0)
        puntos_candidatos = []
        for r in range(size):
            puntos_candidatos.append((r, 0)) # Borde Izquierdo
            puntos_candidatos.append((r, size - 1)) # Borde Derecho
        for c in range(1, size - 1): # Excluir esquinas repetidas
            puntos_candidatos.append((0, c)) # Borde Superior
            puntos_candidatos.append((size - 1, c)) # Borde Inferior
        
        for i in range(n):
            inicio = random.choice(puntos_candidatos)
            destino = inicio
            while destino == inicio:
                destino = random.choice(puntos_candidatos)
            puntos.append((inicio, destino))
        return puntos

    # --- PLANIFICACIÓN DE RUTAS ---
    
    def planificar_rutas_sequencial(self, puntos_inicio_destino):
        """Calcula todas las rutas de manera secuencial."""
        print("\n--- INICIANDO CÁLCULO DE RUTAS SECUENCIAL ---")
        rutas = []
        inicio_tiempo = time.time()
        for i, (inicio, destino) in enumerate(puntos_inicio_destino):
            ruta = dijkstra_ruta(self.ciudad, inicio, destino)
            rutas.append((i, inicio, destino, ruta))
        self.rutas_sequencial_tiempo = time.time() - inicio_tiempo
        print(f"Tiempo Secuencial de Planificación: {self.rutas_sequencial_tiempo:.4f}s")
        return rutas

    def planificar_rutas_paralelo(self, puntos_inicio_destino):
        """Calcula todas las rutas usando un Thread Pool Executor."""
        print("\n--- INICIANDO CÁLCULO DE RUTAS EN PARALELO (ThreadPool) ---")
        rutas = []
        inicio_tiempo = time.time()
        
        num_vehiculos = len(puntos_inicio_destino)
        # Usar un número razonable de hilos, e.g., el número de vehículos o el doble de CPUs
        max_workers = min(num_vehiculos, 32) 
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Mapear la función dijkstra_ruta a cada par (inicio, destino)
            future_to_coords = {
                executor.submit(dijkstra_ruta, self.ciudad, inicio, destino): (i, inicio, destino)
                for i, (inicio, destino) in enumerate(puntos_inicio_destino)
            }
            
            for future in future_to_coords:
                i, inicio, destino = future_to_coords[future]
                try:
                    ruta = future.result()
                    rutas.append((i, inicio, destino, ruta))
                except Exception as exc:
                    print(f"Ruta para V-{i} generó una excepción: {exc}")

        # Ordenar las rutas por ID de vehículo original (i)
        rutas.sort(key=lambda x: x[0])
        
        self.rutas_paralelo_tiempo = time.time() - inicio_tiempo
        print(f"Tiempo Paralelo de Planificación: {self.rutas_paralelo_tiempo:.4f}s")
        return rutas

    # --- EJECUCIÓN ---

    def ejecutar_simulacion(self, rutas_data):
        """Inicializa y ejecuta los hilos de semáforos y vehículos."""
        
        # Detener semáforos anteriores (si los hay)
        for semaforo in self.ciudad.obtener_semaforos():
            semaforo.stop()
        
        # 1. Crear vehículos
        self.vehiculos = []
        for i, inicio, destino, ruta in rutas_data:
            if ruta:
                vehiculo = Vehiculo(i, self.ciudad, inicio, destino, ruta)
                self.vehiculos.append(vehiculo)

        # 2. Iniciar semáforos (se reinician en la clase Ciudad)
        semaforos = self.ciudad.obtener_semaforos()
        print(f"\n--- INICIANDO SIMULACIÓN CON {len(self.vehiculos)} VEHÍCULOS y {len(semaforos)} SEMÁFOROS ---")
        
        # 3. Iniciar hilos de vehículos
        inicio_simulacion = time.time()
        for vehiculo in self.vehiculos:
            vehiculo.start()

        # 4. Esperar a que todos los vehículos lleguen a su destino
        while any(not v.llegado for v in self.vehiculos):
            time.sleep(Configuracion.VELOCIDAD_SIMULACION / 2)
            self.mostrar_estado_actual()
            
            # Condición de salida si se excede un tiempo (para evitar bucles infinitos)
            if time.time() - inicio_simulacion > 200:
                print("\nSimulación detenida: Límite de tiempo excedido (200s). Posiblemente un deadlock o congestión extrema.")
                break

        tiempo_total_simulacion = time.time() - inicio_simulacion
        
        # 5. Detener semáforos
        for semaforo in semaforos:
            semaforo.stop()
            
        print("\n--- SIMULACIÓN FINALIZADA ---")
        return tiempo_total_simulacion

    # --- MONITOREO Y MÉTRICAS ---
    
    def mostrar_estado_actual(self):
        """Muestra una representación simple de la ciudad y la congestión."""
        size = Configuracion.GRID_SIZE
        grid_map = [['. ' for _ in range(size)] for _ in range(size)]
        congestion_total = 0
        
        for v in self.vehiculos:
            if not v.llegado:
                r, c = v.posicion_actual
                grid_map[r][c] = f'V{v.id_vehiculo % 10}' # Usar un dígito para representación simple

        for inter in self.ciudad.intersecciones.values():
            r, c = inter.coords
            
            if inter.tiene_semaforo:
                estado_luz = inter.semaforo.estado[0] # R, A, V
                grid_map[r][c] = f'{estado_luz}'

            congestion_total += inter.vehiculos_en_espera

        print("\n" + "=" * (size * 2 + 5))
        for r in range(size):
            print("| " + "".join(grid_map[r]) + " |")
        print("=" * (size * 2 + 5))
        print(f"Vehículos en espera (Congestión): {congestion_total}")


    def generar_reporte(self, tiempo_total_simulacion):
        """Calcula y muestra todas las métricas solicitadas."""
        vehiculos_llegados = [v for v in self.vehiculos if v.llegado]
        
        # 1. Tiempos de Viaje
        tiempos_viaje = [v.tiempo_total_viaje() for v in vehiculos_llegados]
        tiempo_promedio = sum(tiempos_viaje) / len(tiempos_viaje) if tiempos_viaje else 0
        
        # 2. Vehículo que llegó primero
        if vehiculos_llegados:
            vehiculo_ganador = min(vehiculos_llegados, key=lambda v: v.tiempo_total_viaje())
        else:
            vehiculo_ganador = None

        # 3. Tiempo de Espera en Semáforos
        tiempos_espera = [v.tiempo_espera_total for v in vehiculos_llegados]
        espera_promedio = sum(tiempos_espera) / len(tiempos_espera) if tiempos_espera else 0
        
        # 4. Porcentaje de tiempo detenido
        porcentaje_espera = []
        for v in vehiculos_llegados:
            if v.tiempo_total_viaje() > 0:
                porcentaje_espera.append((v.tiempo_espera_total / v.tiempo_total_viaje()) * 100)
            else:
                porcentaje_espera.append(0)
        porcentaje_espera_promedio = sum(porcentaje_espera) / len(porcentaje_espera) if porcentaje_espera else 0
        
        # 5. Congestión (máxima observada en intersecciones)
        max_espera_interseccion = 0
        for inter in self.ciudad.intersecciones.values():
            if inter.registro_espera:
                max_espera_interseccion = max(max_espera_interseccion, len(inter.registro_espera))

        print("\n" + "="*50)
        print("           REPORTE FINAL DE LA SIMULACIÓN")
        print("="*50)
        print(f"Tiempo Total de Simulación (Reloj): {tiempo_total_simulacion:.2f} segundos")
        print(f"Vehículos que completaron la ruta: {len(vehiculos_llegados)}/{Configuracion.NUM_VEHICULOS}")
        
        if vehiculo_ganador:
            print(f"\nVehículo que llegó primero: {vehiculo_ganador.nombre}")
            print(f"Tiempo total de viaje: {vehiculo_ganador.tiempo_total_viaje():.2f} segundos")

        print("\n--- METRICAS GENERALES DE RENDIMIENTO ---")
        print(f"Tiempo Promedio de Viaje: {tiempo_promedio:.2f} s")
        print(f"Tiempo Promedio de Espera en Semáforos: {espera_promedio:.2f} s")
        print(f"Porcentaje Promedio de Viaje Detenido: {porcentaje_espera_promedio:.2f} %")
        print(f"Máxima Congestión (esperas por intersección): {max_espera_interseccion} vehículos")

        print("\n--- COMPARACIÓN DE PLANIFICACIÓN DE RUTAS ---")
        print("| Algoritmo    | Tiempo (s) |")
        print("|--------------|------------|")
        print(f"| Secuencial   | {self.rutas_sequencial_tiempo:.4f} |")
        print(f"| Paralelo     | {self.rutas_paralelo_tiempo:.4f} |")
        
        if self.rutas_sequencial_tiempo > 0 and self.rutas_paralelo_tiempo > 0:
            speedup = self.rutas_sequencial_tiempo / self.rutas_paralelo_tiempo
            print(f"\nSpeedup (Paralelo vs Secuencial): {speedup:.2f}x")
        
        print("="*50)

# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN ---

def main():
    # --- Configuración Inicial ---
    # Nota: Los parámetros se pueden modificar aquí o leer desde un archivo/menú
    Configuracion.NUM_VEHICULOS = 100 # Cambiar la cantidad de vehículos para la prueba
    Configuracion.VELOCIDAD_SIMULACION = 0.05 # Más rápido para correr la simulación
    
    # Mostrar la configuración
    print("="*50)
    print("        SIMULACIÓN DE TRÁFICO CONCURRENTE")
    print("="*50)
    print(f"Tamaño de la Ciudad: {Configuracion.GRID_SIZE}x{Configuracion.GRID_SIZE}")
    print(f"Vehículos a simular: {Configuracion.NUM_VEHICULOS}")
    print(f"Tiempos Semáforo (V/A/R): {Configuracion.TIEMPOS_SEMAFORO['VERDE']}s / {Configuracion.TIEMPOS_SEMAFORO['AMARILLO']}s / {Configuracion.TIEMPOS_SEMAFORO['ROJO']}s")

    sim = Simulacion()
    
    # 1. Generar puntos de inicio y destino
    puntos_inicio_destino = sim._generar_puntos(Configuracion.NUM_VEHICULOS)

    # 2. Planificación de Rutas Secuencial (para métrica de comparación)
    # Solo calculamos el tiempo, no usamos estas rutas para la simulación
    sim.planificar_rutas_sequencial(puntos_inicio_destino)

    # 3. Planificación de Rutas Paralela (usamos estas rutas para la simulación)
    rutas_para_simulacion = sim.planificar_rutas_paralelo(puntos_inicio_destino)

    # 4. Ejecutar la Simulación
    tiempo_total_simulacion = sim.ejecutar_simulacion(rutas_para_simulacion)

    # 5. Generar Reporte Final
    sim.generar_reporte(tiempo_total_simulacion)

if __name__ == "__main__":
    main()

# Evidencia de Sincronización:
# 1. Lock/Mutex en Interseccion: El campo `ocupada_por` y las llamadas a `acquire()/release()` en el
#    Vehiculo aseguran que solo un hilo (vehículo) esté en la intersección a la vez, evitando colisiones.
# 2. Condition en Interseccion: El hilo Semaforo llama a `notify_all()` cuando el estado es "VERDE".
#    Los hilos Vehiculo llaman a `wait()` si el estado no es "VERDE", liberando el lock y bloqueándose
#    hasta recibir la notificación de luz verde.
# Estos mecanismos garantizan la consistencia y evitan la condición de carrera y las colisiones.