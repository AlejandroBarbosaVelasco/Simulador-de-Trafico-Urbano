import pygame
import random

# Asi se inicializa
pygame.init()

# Configuración de la cuadrícula
GRID_SIZE = 12
BLOCK_SIZE = 40
STREET_WIDTH = 30

# Tamaño exacto sin bordes
WIDTH  = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH
HEIGHT = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ciudad 12x12 sin margen exterior")

GREEN = (80, 170, 60)
RED = (220, 40, 40)

# ===== Cargar imágenes =====
img_hori = pygame.image.load("Calle Hori.png")
img_vert = pygame.image.load("Calle Verti.png")

# Escalar imágenes al tamaño exacto
img_hori = pygame.transform.scale(img_hori, (BLOCK_SIZE, STREET_WIDTH))
img_vert = pygame.transform.scale(img_vert, (STREET_WIDTH, BLOCK_SIZE))

# -----------------------------------------------------------
#  LISTA DE SEMÁFOROS
#
#  Cada semáforo será un diccionario con:
#  - row, col  → coordenadas en la cuadrícula
#  - x, y      → posición exacta en píxeles
#  - (aqui se pondria un hilo o estado)
# -----------------------------------------------------------
traffic_lights = []

# se eligen 12 posiciones sin repetir, evitando bordes
all_positions = [
    (r, c)
    for r in range(1, GRID_SIZE - 1)
    for c in range(1, GRID_SIZE - 1)
]

random.shuffle(all_positions)

for (r, c) in all_positions[:12]:

    # Calcular pixel exacto del cruce
    x = c * (BLOCK_SIZE + STREET_WIDTH) - STREET_WIDTH
    y = r * (BLOCK_SIZE + STREET_WIDTH) - STREET_WIDTH

    traffic_lights.append({
        "row": r,
        "col": c,
        "x": x,
        "y": y,
        "color": RED  # luego será parte del hilo
    })

# ===========================================================
#  (TODO)
#  Aquí PODRIA ir una clase Semaforo con hilos:
#
#  class Semaforo(Thread):
#       def run():
#           cambiar colores
#
# ===========================================================

running = True
while running:
    win.fill((50, 50, 50))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            # Posiciones de bloques
            x = col * (BLOCK_SIZE + STREET_WIDTH)
            y = row * (BLOCK_SIZE + STREET_WIDTH)

            # Dibujar calles
            if row > 0:
                win.blit(img_hori, (x, y - STREET_WIDTH))
            if col > 0:
                win.blit(img_vert, (x - STREET_WIDTH, y))

            # Dibujar bloque
            pygame.draw.rect(win, GREEN, (x, y, BLOCK_SIZE, BLOCK_SIZE))

    # -------------------------------------------------------
    # DIBUJAR SEMÁFOROS
    # -------------------------------------------------------
    for sem in traffic_lights:
        pygame.draw.circle(win, sem["color"], (sem["x"], sem["y"]), 8)

        # de forma predeterminada todos estan en rojo, solo es visual

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
