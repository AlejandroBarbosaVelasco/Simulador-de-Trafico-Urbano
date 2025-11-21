import pygame
import random

# --- Configuración Inicial de Pygame ---
pygame.init()

# --- Dimensiones y Colores ---
ANCHO_VENTANA = 720
ALTO_VENTANA = 720
DIMENSION_CELDA = ANCHO_VENTANA // 12  # 60 píxeles por celda

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
# Nuevos colores para simular calles, parques y aceras
VERDE_ACERA = (150, 200, 150)  # Color claro para el espacio entre las celdas (la acera)
VERDE_PARQUE = (50, 150, 50)  # Color oscuro para zonas verdes/parques
GRIS_CALLE = (60, 60, 60)      # Color para las calles
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)


# --- Definición del Espacio de Acera ---
ANCHO_ACERA = 4 # Ancho de la acera en píxeles. Debe ser pequeño, ej: 4 o 5.
DIMENSION_CONTENIDO = DIMENSION_CELDA - (2 * ANCHO_ACERA) # El área real de la calle/parque

# Cargar imagen de calle
img_calle = pygame.image.load("calle.png")
img_calle = pygame.transform.scale(img_calle, (DIMENSION_CONTENIDO, DIMENSION_CONTENIDO))

# --- Configuración de la Ventana (Igual que antes) ---
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Simulación de Tráfico con Aceras")

# --- Clase Semaforo (Igual que antes) ---
class Semaforo:
    def __init__(self, x, y, estado_inicial=ROJO):
        self.x = x
        self.y = y
        self.estado = estado_inicial 
        self.tiempo_cambio = pygame.time.get_ticks()

    def dibujar(self, superficie):
        # La posición del semáforo debe estar en el borde, junto a la acera.
        # Usaremos la celda (i, j) donde se definieron, y ajustaremos el centro
        
        # Centro de la celda (x, y)
        centro_x = self.x * DIMENSION_CELDA + DIMENSION_CELDA // 2
        centro_y = self.y * DIMENSION_CELDA + DIMENSION_CELDA // 2
        
        # Ajuste para posicionar el semáforo en la esquina de la acera (dentro del borde)
        # NOTA: Los semáforos se generan en posiciones PAR (esquinas verdes).
        
        # Si x es par, la calle está a la derecha (x+1) y arriba/abajo.
        # Ajustamos el centro para que esté ligeramente al lado de la acera (par)
        
        if self.x % 2 == 0:
            # Si x es par, el semáforo está a la izquierda de la calle. Lo movemos hacia la derecha.
            centro_x += DIMENSION_CELDA // 4 
        else:
            # Esto no debería ocurrir con la lógica de generación (x debería ser par)
            centro_x -= DIMENSION_CELDA // 4
            
        if self.y % 2 == 0:
            # Si y es par, el semáforo está arriba de la calle. Lo movemos hacia abajo.
            centro_y += DIMENSION_CELDA // 4
        else:
            # Esto no debería ocurrir con la lógica de generación (y debería ser par)
            centro_y -= DIMENSION_CELDA // 4

        radio = 8
        pygame.draw.circle(superficie, self.estado, (centro_x, centro_y), radio)
        
    def cambiar_estado(self, duracion_ms=3000):
        tiempo_actual = pygame.time.get_ticks()

        # Duraciones personalizadas para cada color
        duraciones = {
            ROJO: 3000,
            VERDE: 3000,
            AMARILLO: 1000
        }


        if tiempo_actual - self.tiempo_cambio > duraciones[self.estado]:
            # Cambiar el estado en secuencia ROJO → VERDE → AMARILLO → ROJO
            if self.estado == ROJO:
                self.estado = VERDE
            elif self.estado == VERDE:
                self.estado = AMARILLO
            elif self.estado == AMARILLO:
                self.estado = ROJO
            
            self.tiempo_cambio = tiempo_actual


# --- Generación de Posiciones de Semáforo Válidas (Igual que antes) ---
def generar_posiciones_semaforos(num_semaforos=10):
    semaforos = []
    posiciones_validas = []
    
    # El semáforo va en las esquinas de las zonas verdes (índices pares)
    for i in range(2, 11, 2):  # 2, 4, 6, 8, 10
        for j in range(2, 11, 2): # 2, 4, 6, 8, 10
            posiciones_validas.append((i, j)) 
            
    # Añadir 10 semáforos aleatorios
    posiciones_semaforos = random.sample(posiciones_validas, min(num_semaforos, len(posiciones_validas)))
    
    # Crear los objetos Semaforo
    for x, y in posiciones_semaforos:
        estado_inicial = random.choice([ROJO, VERDE])
        semaforos.append(Semaforo(x, y, estado_inicial))
        
    return semaforos

lista_semaforos = generar_posiciones_semaforos(10)


# --- Funciones de Dibujo ---
def dibujar_mapa_con_acera():
    ventana.fill(VERDE_ACERA)

    for i in range(12):
        for j in range(12):
            
            # Coordenadas reales dentro de la celda (sin acera)
            x_contenido = j * DIMENSION_CELDA + ANCHO_ACERA
            y_contenido = i * DIMENSION_CELDA + ANCHO_ACERA

            # Si ambos índices son pares -> parque (se queda como antes)
            if (i % 2 == 0) and (j % 2 == 0):
                rect_contenido = pygame.Rect(
                    x_contenido,
                    y_contenido,
                    DIMENSION_CONTENIDO,
                    DIMENSION_CONTENIDO
                )
                pygame.draw.rect(ventana, VERDE_PARQUE, rect_contenido)

            else:
                # Celda de calle -> dibujar textura
                ventana.blit(img_calle, (x_contenido, y_contenido))



def dibujar_semaforos(semaforos):
    for semaforo in semaforos:
        semaforo.dibujar(ventana)

# --- Bucle Principal del Juego ---
ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # --- Lógica de Actualización ---
    for semaforo in lista_semaforos:
        semaforo.cambiar_estado(3000)

    # --- Dibujo ---
    dibujar_mapa_con_acera() # Llamamos a la nueva función
    dibujar_semaforos(lista_semaforos)

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad de actualización (FPS)
    reloj.tick(30)

pygame.quit()