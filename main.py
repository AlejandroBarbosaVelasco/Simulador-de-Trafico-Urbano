# main.py
import pygame
from city_map import (
    GRID_SIZE, 
    BLOCK_SIZE, 
    STREET_WIDTH,
    generate_traffic_lights,
    generate_vehicles
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

# Crear hilos
traffic_lights = generate_traffic_lights()
vehicles = generate_vehicles(25, traffic_lights)

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

    # Dibujar cada semáforo
    for sem in traffic_lights:
        pygame.draw.circle(win, sem.current_color, (sem.x, sem.y), 8)

    # Dibujar vehículos
    for v in vehicles:
        x, y = v.get_pixel_position()

        points = [
            (x,     y - 8),
            (x - 6, y + 6),
            (x + 6, y + 6)
        ]

        pygame.draw.polygon(win, (255, 255, 255), points)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()

# Apagar hilos
for sem in traffic_lights:
    sem.stop()
for v in vehicles:
    v.stop()

# Esperar a que terminen
for sem in traffic_lights:
    sem.join()
for v in vehicles:
    v.join()

