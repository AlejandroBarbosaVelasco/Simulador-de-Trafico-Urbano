import pygame
import random
import time

# --- Configuración Inicial de Pygame ---
pygame.init()

# --- Constantes y Configuración ---
ANCHO_VENTANA = 720
ALTO_VENTANA = 720

# Dimensiones de las celdas
DIMENSION_BLOQUE = 80  # Bloque Ancho (Calles Principales / Parques)
DIMENSION_BORDE = 50    # Bloque Angosto (Calles Laterales / Separadores)

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS_PARQUE = (50, 150, 50)    # Color para zonas verdes/parques
GRIS_CALLE = (60, 60, 60)      # Color para las calles
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
AZUL_BORDE = (100, 100, 255)   # Color para el borde angosto

# Estados de semáforo
ESTADOS_SEMAFORO = [ROJO, VERDE, AMARILLO]
DURACION_SEMAFORO = {
    ROJO: 3000,     # 3 segundos en rojo
    VERDE: 3000,    # 3 segundos en verde
    AMARILLO: 1000  # 1 segundo en amarillo
}

# --- Estructura del Mapa (12x12) ---
# 'W': Celda Ancha (110px) - Usada para Calles Principales y Parques
# 'N': Celda Angosta (10px) - Usada para Calles Laterales/Separadores
MAPA_ESTRUCTURA = [
    # 0    1    2    3    4    5    6    7    8    9    10   11
    ['W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N'],  # 0
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],  # 1
    ['W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N'],  # 2
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],  # 3
    ['W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N'],  # 4
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],  # 5
    ['W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N'],  # 6
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],  # 7
    ['W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N'],  # 8
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],  # 9
    ['W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N', 'W', 'N'],  # 10
    ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']   # 11
]

# --- Funciones de Utilidad ---
def obtener_tipo_celda(i, j):
    """Determina el tipo de celda basado en su posición y estructura"""
    tipo_dim = MAPA_ESTRUCTURA[i][j]

    if tipo_dim == 'N':
        return 'BORDER'
    elif i % 2 == 0 and j % 2 == 0:
        return 'PARK'
    elif (i % 2 == 0 and j % 2 != 0) or (i % 2 != 0 and j % 2 == 0):
        return 'STREET'
    else:
        return 'STREET'

def obtener_color_celda(tipo_celda):
    """Devuelve el color correspondiente al tipo de celda"""
    colores = {
        'PARK': GRIS_PARQUE,
        'STREET': GRIS_CALLE,
        'BORDER': AZUL_BORDE
    }
    return colores.get(tipo_celda, BLANCO)

def calcular_posicion_real(i, j):
    """Calcula la posición real en píxeles de una celda en la cuadrícula"""
    # Cálculo de X (Columna j)
    x_inicio = 0
    for col in range(j):
        dim = DIMENSION_BLOQUE if MAPA_ESTRUCTURA[0][col] == 'W' else DIMENSION_BORDE
        x_inicio += dim
    
    # Cálculo de Y (Fila i)
    y_inicio = 0
    for row in range(i):
        dim = DIMENSION_BLOQUE if MAPA_ESTRUCTURA[row][0] == 'W' else DIMENSION_BORDE
        y_inicio += dim
    
    # Dimensión de la celda actual
    ancho_celda = DIMENSION_BLOQUE if MAPA_ESTRUCTURA[i][j] == 'W' else DIMENSION_BORDE
    alto_celda = DIMENSION_BLOQUE if MAPA_ESTRUCTURA[i][0] == 'W' else DIMENSION_BORDE
    
    return x_inicio, y_inicio, ancho_celda, alto_celda

# --- Clase Semaforo ---
class Semaforo:
    def __init__(self, i, j, estado_inicial=ROJO):
        self.i = i  # Fila (Y)
        self.j = j  # Columna (X)
        self.estado = estado_inicial 
        self.tiempo_cambio = pygame.time.get_ticks()

    def obtener_posicion_real(self):
        """Calcula la posición real del semáforo en la ventana"""
        x_inicio, y_inicio, ancho_celda, alto_celda = calcular_posicion_real(self.i, self.j)
        
        # Posicionar el semáforo en la esquina inferior derecha del bloque
        centro_x = x_inicio + ancho_celda - 10 
        centro_y = y_inicio + alto_celda - 10
        
        return centro_x, centro_y

    def dibujar(self, superficie):
        """Dibuja el semáforo en la superficie especificada"""
        centro_x, centro_y = self.obtener_posicion_real()
        radio = 8
        
        # Dibujar un poste simulado para el semáforo
        pygame.draw.line(superficie, NEGRO, (centro_x, centro_y), (centro_x, centro_y + 15), 2)
        
        # Dibujar el estado de luz
        pygame.draw.circle(superficie, self.estado, (centro_x, centro_y), radio)
        
    def cambiar_estado(self):
        """Cambia el estado del semáforo según el tiempo transcurrido"""
        tiempo_actual = pygame.time.get_ticks()
        duracion_actual = DURACION_SEMAFORO.get(self.estado, 3000)

        if tiempo_actual - self.tiempo_cambio > duracion_actual:
            # Cambiar el estado en secuencia ROJO → VERDE → AMARILLO → ROJO
            if self.estado == ROJO:
                self.estado = VERDE
            elif self.estado == VERDE:
                self.estado = AMARILLO
            elif self.estado == AMARILLO:
                self.estado = ROJO
            
            self.tiempo_cambio = tiempo_actual

# --- Funciones de Generación y Dibujo ---
def generar_posiciones_semaforos(num_semaforos=10):
    """Genera una lista de semáforos en posiciones válidas"""
    semaforos = []
    posiciones_validas = []
    
    # Los semáforos se colocan en los bloques anchos ('W') que son parques (i, j par)
    for i in range(len(MAPA_ESTRUCTURA)):
        for j in range(len(MAPA_ESTRUCTURA[0])):
            if MAPA_ESTRUCTURA[i][j] == 'W' and obtener_tipo_celda(i, j) == 'PARK':
                posiciones_validas.append((i, j)) 
    
    # Añadir semáforos aleatorios
    if posiciones_validas:
        num_semaforos = min(num_semaforos, len(posiciones_validas))
        posiciones_semaforos = random.sample(posiciones_validas, num_semaforos)
        
        # Crear los objetos Semaforo
        for i, j in posiciones_semaforos:
            estado_inicial = random.choice([ROJO, VERDE])
            semaforos.append(Semaforo(i, j, estado_inicial))
    
    return semaforos

def dibujar_mapa_personalizado(ventana):
    """Dibuja el mapa completo en la ventana especificada"""
    ventana.fill(BLANCO)  # Fondo blanco general

    for i in range(len(MAPA_ESTRUCTURA)):
        for j in range(len(MAPA_ESTRUCTURA[i])):
            x_actual, y_actual, ancho_celda, alto_celda = calcular_posicion_real(i, j)
            
            # Determinar color y tipo
            tipo_celda = obtener_tipo_celda(i, j)
            color = obtener_color_celda(tipo_celda)

            # Dibujar el bloque de la celda
            rect_celda = pygame.Rect(x_actual, y_actual, ancho_celda, alto_celda)
            pygame.draw.rect(ventana, color, rect_celda)
            
            # Dibujar borde para ver las celdas independientes
            pygame.draw.rect(ventana, NEGRO, rect_celda, 1)

def dibujar_semaforos(ventana, semaforos):
    """Dibuja todos los semáforos en la ventana"""
    for semaforo in semaforos:
        semaforo.dibujar(ventana)

# --- Configuración de la Ventana ---
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Simulación de Tráfico con Celdas Independientes")

# --- Inicialización ---
lista_semaforos = generar_posiciones_semaforos(10)
reloj = pygame.time.Clock()

# --- Bucle Principal del Juego ---
ejecutando = True
while ejecutando:
    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # --- Lógica de Actualización ---
    for semaforo in lista_semaforos:
        semaforo.cambiar_estado()

    # --- Dibujo ---
    dibujar_mapa_personalizado(ventana) 
    dibujar_semaforos(ventana, lista_semaforos)

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad de actualización (FPS)
    reloj.tick(30)

pygame.quit()