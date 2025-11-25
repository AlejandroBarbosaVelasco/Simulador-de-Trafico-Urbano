# main.py
import pygame
from city_map import (
    GRID_SIZE, 
    BLOCK_SIZE, 
    STREET_WIDTH,
    generate_traffic_lights
)

pygame.init()

# Crear ventana
WIDTH  = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH
HEIGHT = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ciudad 12x12 con Semáforos Independientes")

GREEN = (80, 170, 60)

# Cargar imágenes de calles
img_hori = pygame.image.load("Calle Hori.png")
img_vert = pygame.image.load("Calle Verti.png")

img_hori = pygame.transform.scale(img_hori, (BLOCK_SIZE, STREET_WIDTH))
img_vert = pygame.transform.scale(img_vert, (STREET_WIDTH, BLOCK_SIZE))

# Crear semáforos como hilos
traffic_lights = generate_traffic_lights()

running = True
while running:

    win.fill((50, 50, 50))

    # Dibujar mapa
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            x = col * (BLOCK_SIZE + STREET_WIDTH)
            y = row * (BLOCK_SIZE + STREET_WIDTH)

            # Calles
            if row > 0:
                win.blit(img_hori, (x, y - STREET_WIDTH))
            if col > 0:
                win.blit(img_vert, (x - STREET_WIDTH, y))

            pygame.draw.rect(
                win, 
                GREEN,
                (x, y, BLOCK_SIZE, BLOCK_SIZE)
            )

    # Dibujar cada semáforo según su color actual
    for sem in traffic_lights:
        pygame.draw.circle(win, sem.current_color, (sem.x, sem.y), 8)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()

# Apagar hilos
for sem in traffic_lights:
    sem.stop()
