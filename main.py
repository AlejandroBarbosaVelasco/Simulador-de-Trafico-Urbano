import pygame
import pygame_menu
from juego import start_game, WIDTH, HEIGHT

# --- 1. Configuración Global ---
pygame.init()
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sistema de Tráfico - Menú")

menu_resultados = pygame_menu.Menu('Resultados de la Simulación', WIDTH, HEIGHT, 
                                   theme=pygame_menu.themes.THEME_BLUE)

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


def mostrar_ranking_vacio():
    # Esto es solo para que no se vea feo si entran antes de jugar
    menu_resultados.clear()
    menu_resultados.add.label("Aún no hay datos.\n¡Juega una partida!", font_size=20)
    menu_resultados.add.button('Volver', pygame_menu.events.BACK)

mostrar_ranking_vacio() # Inicializarlo vacío

# --- FUNCIÓN PARA ACTUALIZAR EL MENÚ CON DATOS REALES ---
def actualizar_menu_resultados(ranking, promedio, total):
    """
    Recibe la lista ordenada de tuplas (id, tiempo) y las estadísticas
    """
    # A. Limpiamos los widgets viejos
    menu_resultados.clear()
    
    # B. Agregamos el Resumen Estadístico
    menu_resultados.add.label('ESTADÍSTICAS', font_size=30, underline=True)
    menu_resultados.add.label(f"Total Vehículos: {total}", font_size=20)
    menu_resultados.add.label(f"Tiempo Promedio: {promedio:.4f} s", font_size=20)
    menu_resultados.add.vertical_margin(20)
    
    # C. Agregamos la tabla de posiciones (Scrollable si son muchos)
    menu_resultados.add.label('RANKING (Menor Tiempo)', font_size=25)
    
    # Creamos un frame (scroll area) si esperas muchos datos, 
    # o simplemente agregamos labels si son pocos (ej. < 15)
    for i, (id_vehiculo, tiempo) in enumerate(ranking):
        # Top 3 resaltados        
        color = (255, 201, 60) if i == 0 else (80, 80, 80) # Oro para el 1ro
        texto = f"#{i+1} - {id_vehiculo}: {tiempo:.4f} s"
        menu_resultados.add.label(texto, font_size=18, font_color=color)

    # D. Botón para regresar
    menu_resultados.add.vertical_margin(20)
    menu_resultados.add.button('Volver al Menú', pygame_menu.events.BACK)
    menu_resultados.add.vertical_margin(20)



# --- Juego Actual (Encapsulado) ---
def iniciar_juego():
    # Usas 'config_juego' para acceder a las variables
    # Llamamos a la función del otro archivo pasando los parametros
    vehiculos = start_game(surface, config_juego['vehiculos'], 
                           config_juego['green_time'], 
                           config_juego['yellow_time'], 
                           config_juego['red_time'])
    # Cuando start_simulation termine (return), el código sigue aquí:
    # Reiniciamos el menú para que se vuelva a dibujar correctamente
    # (Esto es necesario porque el juego "ensució" la pantalla)
    
    if not vehiculos: return
    
    vehiculos_ordenados = sorted(vehiculos.items(), key=lambda item: item[1])

    # print("--- Ranking por tiempo (Menor a Mayor) ---")
    # for id_vehiculo,tiempo_recorrido in vehiculos_ordenados:
    #     print(f"{id_vehiculo}: {tiempo_recorrido:.4f} s")

    tiempos = vehiculos.values()
    promedio = sum(tiempos) / len(tiempos)
    # print(f"--- Estadísticas ---")
    # print(f"Total vehículos: {len(tiempos)}")
    # print(f"Tiempo promedio: {promedio:.4f} segundos")
    total = len(tiempos)

    actualizar_menu_resultados(vehiculos_ordenados, promedio, total)

    main_menu._open(menu_resultados)

    # pass 

# --- CONFIGURACIÓN DEL MENÚ ---
main_menu = pygame_menu.Menu('Simulación de Tráfico', WIDTH, HEIGHT,
                       theme=pygame_menu.themes.THEME_DARK)

main_menu.add.label('Parametros de Simulación\n')

# Input numérico para vehículos (slider o text input)
main_menu.add.range_slider('Num Vehículos: ', 
                     default=20, 
                     range_values=(20, 200), 
                     increment=1,
                     onchange=set_vehiculos)
main_menu.add.range_slider('Num Vehículos: ', 
                     default=5, 
                     range_values=(1, 10), 
                     increment=1,
                     onchange=set_green_time)
main_menu.add.range_slider('Num Vehículos: ', 
                     default=2, 
                     range_values=(1, 10), 
                     increment=1,
                     onchange=set_yellow_time)
main_menu.add.range_slider('Num Vehículos: ', 
                     default=5, 
                     range_values=(1, 10), 
                     increment=1,
                     onchange=set_red_time)

main_menu.add.label('\n')
main_menu.add.button('INICIAR SIMULACIÓN', iniciar_juego)
main_menu.add.button('Ver Últimos Resultados', menu_resultados)
main_menu.add.button('Salir', pygame_menu.events.EXIT)

if __name__ == '__main__':
    main_menu.mainloop(surface)
