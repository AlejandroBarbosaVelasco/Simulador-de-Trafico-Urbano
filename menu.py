import pygame
import pygame_menu
from main import start_game, WIDTH, HEIGHT

# --- 1. Configuración Global ---
pygame.init()
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sistema de Tráfico - Menú")

# Variables donde guardaremos la data del menú
config_juego = {
    'green_time': 5,
    'yellow_time': 2,
    'red_time': 6,
    'vehiculos' : 20,
    # Coordenadas de inicio y fin TODO
}

def set_vehiculos(valor):
    # pygame-menu devuelve el valor tal cual para sliders/text inputs
    config_juego['vehiculos'] = int(valor)
def set_green_time(valor):
    config_juego['green_time'] = int(valor)

def set_yellow_time(valor):
    config_juego['yellow_time'] = int(valor)

def set_red_time(valor):
    config_juego['red_time'] = int(valor)

# --- 2. Juego Actual (Encapsulado) ---
def iniciar_juego():
    # Usas 'config_juego' para acceder a las variables
    # Llamamos a la función del otro archivo pasando los parametros
    start_game(surface, config_juego['vehiculos'], config_juego['green_time'], config_juego['yellow_time'], config_juego['red_time'])

    # Cuando start_simulation termine (return), el código sigue aquí:
    # Reiniciamos el menú para que se vuelva a dibujar correctamente
    # (Esto es necesario porque el juego "ensució" la pantalla)
    pass 

# --- CONFIGURACIÓN DEL MENÚ ---
menu = pygame_menu.Menu('Configuración', WIDTH, HEIGHT,
                       theme=pygame_menu.themes.THEME_DARK)

menu.add.label('Parametros de Simulación\n')

# Input numérico para vehículos (slider o text input)
menu.add.range_slider('Num Vehículos: ', 
                     default=20, 
                     range_values=(20, 200), 
                     increment=1,
                     onchange=set_vehiculos)
menu.add.range_slider('Num Vehículos: ', 
                     default=5, 
                     range_values=(1, 10), 
                     increment=1,
                     onchange=set_green_time)
menu.add.range_slider('Num Vehículos: ', 
                     default=2, 
                     range_values=(1, 10), 
                     increment=1,
                     onchange=set_yellow_time)
menu.add.range_slider('Num Vehículos: ', 
                     default=5, 
                     range_values=(1, 10), 
                     increment=1,
                     onchange=set_red_time)

menu.add.label('\n')
menu.add.button('INICIAR SIMULACIÓN', iniciar_juego)
menu.add.button('Salir', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)
