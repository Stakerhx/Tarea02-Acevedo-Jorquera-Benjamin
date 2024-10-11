import requests  # Para hacer solicitudes HTTP
import getopt    # Para manejar argumentos de línea de comandos
import sys       # Para interactuar con el sistema
import os        # Para ejecutar comandos en la terminal
import re        # Para buscar patrones de texto (en este caso, direcciones MAC)

# Esta función consulta el fabricante de una dirección MAC usando una API
def consultar_mac(mac_address):

    # Consulta el fabricante de una dirección MAC en la API y devuelve el nombre y el tiempo de respuesta.
    
    API_ENDPOINT = 'https://api.maclookup.app/v2/macs/'  # URL de la API que vamos a usar

    try:
        # Hacemos la solicitud a la API con la dirección MAC

        respuesta = requests.get(API_ENDPOINT + mac_address)

        # Si la solicitud fue exitosa

        if respuesta.status_code == 200:
            datos = respuesta.json()  # Convertimos la respuesta a formato JSON
            fabricante = datos.get("company", "Fabricante no encontrado")  # Obtenemos el fabricante
            tiempo_respuesta = respuesta.elapsed.total_seconds() * 1000  # Tiempo de respuesta en ms
            return fabricante, tiempo_respuesta
        else:
            return "Error en la consulta", None
    except Exception as error:
        return f"Error al hacer la consulta: {error}", None

# Esta función consulta la tabla ARP del sistema y obtiene el fabricante de cada MAC

def consultar_arp():

    # Muestra la tabla ARP y consulta el fabricante de cada dirección MAC en la tabla.
    
    print("Consultando la tabla ARP.")
    command = "arp -a"  # Comando para obtener la tabla ARP
    try:
        arp_table = os.popen(command).read()  # Ejecuta el comando y lee el resultado
        print("MAC/Vendor:")
        
        # Buscamos todas las direcciones MAC en el resultado de arp -a
         
        mac_addresses = re.findall(r"([0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5})", arp_table)
        
        # Para cada dirección MAC encontrada, consultamos el fabricante

        for mac in mac_addresses:
            fabricante, tiempo_respuesta = consultar_mac(mac)
            if fabricante:
                print(f"{mac} / {fabricante} - Tiempo de respuesta: {tiempo_respuesta:.2f} ms")
            else:
                print(f"{mac} / No encontrado")
    
    except Exception as e:
        print(f"Error al consultar la tabla ARP: {e}")

# Muestra cómo usar el programa

def mostrar_ayuda():
    
    # Muestra las instrucciones de uso para el programa del help.

    help_text = (
        "Uso: OUILookup.py --mac <direccion_mac> | --arp | [--help]\n"
        " -m, --mac  : Dirección MAC a consultar. Ejemplo: aa:bb:cc:00:00:00.\n"
        " -a, --arp  : Muestra los fabricantes de los hosts en la tabla ARP.\n"
        "     --help : Muestra este mensaje de ayuda.\n"
    )
    print(help_text)

# Función principal para procesar los argumentos y ejecutar las opciones

def main(argv):
    # Lee los argumentos del programa y ejecuta la opción solicitada.
    
    mac_address = None
    mostrar_arp = False

    # Aquí procesamos los argumentos que el usuario pasó al programa
    try:
        opts, args = getopt.getopt(argv, "m:a", ["mac=", "arp", "help"])
    except getopt.GetoptError:
        mostrar_ayuda()
        sys.exit(2)

    # Revisamos cada opción pasada
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            mostrar_ayuda()
            sys.exit()
        elif opt in ("-m", "--mac"):
            mac_address = arg
        elif opt in ("-a", "--arp"):
            mostrar_arp = True

    # Dependiendo de lo que pidió el usuario, ejecutamos la opción correspondiente
    if mac_address:
        fabricante, tiempo_respuesta = consultar_mac(mac_address)
        print(f"Dirección MAC : {mac_address}")
        print(f"Fabricante    : {fabricante}")
        if tiempo_respuesta is not None:
            print(f"Tiempo de respuesta: {tiempo_respuesta:.2f} ms")
    elif mostrar_arp:
        consultar_arp()
    else:
        mostrar_ayuda()

# Punto de entrada del programa
if __name__ == "__main__":
    main(sys.argv[1:])
