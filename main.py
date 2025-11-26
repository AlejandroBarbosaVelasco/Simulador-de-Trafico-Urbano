# main.py
import pygame
from city_map import (
    GRID_SIZE, 
    BLOCK_SIZE, 
    STREET_WIDTH,
    generate_traffic_lights,
    generate_vehicles
)

# pygame.init()

# Crear ventana
WIDTH  = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH
HEIGHT = GRID_SIZE * BLOCK_SIZE + (GRID_SIZE - 1) * STREET_WIDTH

# win = pygame.display.set_mode((WIDTH, HEIGHT)) # Setea la ventana con el tamaño proporcionado
# pygame.display.set_caption("Ciudad 12x12 con Semáforos Independientes")

GREEN = (80, 170, 60)
# green_time, yellow_time, red_time, 
def start_game(surface, vehiculos, green_time, yellow_time, red_time):
    """
    surface: La ventana de pygame que ya creó el menú.
    num_vehiculos: El valor que capturamos en el menú.
    """

    # Cargar imágenes de calles
    img_hori = pygame.image.load("Calle Hori.png")
    img_vert = pygame.image.load("Calle Verti.png")

    img_hori = pygame.transform.scale(img_hori, (BLOCK_SIZE, STREET_WIDTH))
    img_vert = pygame.transform.scale(img_vert, (STREET_WIDTH, BLOCK_SIZE))

# --- INICIO DE HILOS USANDO EL PARAMETRO DEL MENU ---
    traffic_lights = generate_traffic_lights(green_time, yellow_time, red_time)
    vehicles = generate_vehicles(vehiculos, traffic_lights)

    running = True
    clock = pygame.time.Clock()
    while running:
        # Usamos la 'surface' que nos pasaron, no creamos una nueva
        surface.fill((50, 50, 50))

        # Dibujar mapa
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):

                x = col * (BLOCK_SIZE + STREET_WIDTH)
                y = row * (BLOCK_SIZE + STREET_WIDTH)

                # Calles
                if row > 0: surface.blit(img_hori, (x, y - STREET_WIDTH))
                if col > 0: surface.blit(img_vert, (x - STREET_WIDTH, y))

                pygame.draw.rect(
                    surface, 
                    GREEN,
                    (x, y, BLOCK_SIZE, BLOCK_SIZE)
                )

        # Dibujar cada semáforo
        for sem in traffic_lights:
            pygame.draw.circle(surface, sem.current_color, (sem.x, sem.y), 8)

        # Dibujar vehículos
        for v in vehicles:
            x, y = v.get_pixel_position()

            points = [
                (x,     y - 8),
                (x - 6, y + 6),
                (x + 6, y + 6)
            ]

            # Imprime y colorea los vehiculos
            pygame.draw.polygon(surface, (255, 255, 255), points)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Opción para volver al menú con ESC
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        pygame.display.update()
        clock.tick(60) # Limitar FPS es importante para no quemar CPU

    # pygame.quit()

    # --- LIMPIEZA DE HILOS (Crucial antes de volver al menú) ---
    for sem in traffic_lights:
        sem.stop()
    for v in vehicles:
        v.stop()

    # Esperar a que terminen
    for sem in traffic_lights:
        sem.join()
    for v in vehicles:
        v.join()

    print("Simulación finalizada. Volviendo al menú.")
    # AQUI DEBE DE RETORNARSE LOS TIEMPOS DE CADA HILO CON UN RETURN
