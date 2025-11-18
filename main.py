import time

NUMERO_VEHICULOS = 20
LUCES = {
    'LUZ_VERDE' : 5,
    'LUZ_AMARILLA' : 2,
    'LUZ_ROJA' : 6
}
COORDENADAS_INICIO = {
    'X' : 0,
    'Y' : 0
}

COORDENADAS_DESTINO = {
    'X' : 0,
    'Y' : 0
}

def muestra_valores():
    print("Configuracion inicial: \n")
    print("Cantidad de vehiculos: ",NUMERO_VEHICULOS)
    print("\nTiempo de luces: ")
    for x,y in LUCES.items():
        print(x,y)
    print("\nCoordenadas de inicio: ")
    for x,y in COORDENADAS_INICIO.items():
        print(x,y)
    print("\nCoordenadas de destino: ")
    for x,y in COORDENADAS_DESTINO.items():
        print(x,y)

def cambio_valores():
    NUMERO_VEHICULOS = input("\n\nCantidad de vehiculos (Maximo 200 minimo 20): ")
    verificacion_vehicular = int(NUMERO_VEHICULOS) >= 20 and int(NUMERO_VEHICULOS) <=200
    print(verificacion_vehicular)
    while(not verificacion_vehicular):
        NUMERO_VEHICULOS = input("\n\nCantidad de vehiculos (Maximo 200 minimo 20): ")
        verificacion_vehicular = int(NUMERO_VEHICULOS) >= 20 and int(NUMERO_VEHICULOS) <=200
        print(verificacion_vehicular)

    print("\nTiempo de luces: ")
    for x,y in LUCES.items():
        z = input(f""+x+": ")
        LUCES[x] = z
    print("\nCoordenadas de inicio: ")
    for x,y in COORDENADAS_INICIO.items():
        z = input(f""+x+": ")
        COORDENADAS_INICIO[x] = z
    print("\nCoordenadas de destino: ")
    for x,y in COORDENADAS_DESTINO.items():
        z = input(f""+x+": ")
        COORDENADAS_DESTINO[x] = z


def menu():
    fg = True
    while(fg):
        print("----------Inicio del proyecto----------\n")
        muestra_valores()
        cambio = input("\n\nDesea cambiar los valores actuales?: (S/N)")
        if cambio == 'S':
            cambio_valores()
        elif cambio == 'N':
            fg = False
        else:
            print("Opcion no valida")
            time.sleep(3)


if __name__ == "__main__":
    menu()