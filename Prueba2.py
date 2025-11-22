import pygame
pygame.init()

# Configuración de la cuadrícula
GRID_SIZE = 12
BLOCK_SIZE = 40
STREET_WIDTH = 30

# Tamaño exacto sin calles externas
WIDTH  = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH
HEIGHT = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ciudad 12x12 sin margen exterior")

GREEN = (80, 170, 60)

# ===== Cargar imágenes =====
img_hori = pygame.image.load("Calle Hori.png")
img_vert = pygame.image.load("Calle Verti.png")

# Escalar imágenes al tamaño exacto
img_hori = pygame.transform.scale(img_hori, (BLOCK_SIZE, STREET_WIDTH))
img_vert = pygame.transform.scale(img_vert, (STREET_WIDTH, BLOCK_SIZE))

running = True
while running:
    win.fill((50, 50, 50))  # fondo solo para ver diferencias

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            # Posición del bloque (sin offset)
            x = col * (BLOCK_SIZE + STREET_WIDTH)
            y = row * (BLOCK_SIZE + STREET_WIDTH)

            # Dibujar calles SOLO si no es el primer bloque
            # Calle horizontal arriba
            if row > 0:
                win.blit(img_hori, (x, y - STREET_WIDTH))

            # Calle vertical izquierda
            if col > 0:
                win.blit(img_vert, (x - STREET_WIDTH, y))

            # Dibujar bloque
            pygame.draw.rect(win, GREEN, (x, y, BLOCK_SIZE, BLOCK_SIZE))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
