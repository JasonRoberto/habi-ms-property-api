import http.server
from app.request_handler import APIRequestHandler
from config import HOST, PORT


def run_server(server_class=http.server.HTTPServer, handler_class=APIRequestHandler, host=HOST, port=PORT):
    """
    Configura e inicia el servidor HTTP.

    Args:
        server_class: La clase del servidor HTTP a utilizar.
        handler_class: La clase manejadora de solicitudes a utilizar.
        host (str): El hostname o IP en la que el servidor escuchará.
        port (int): El puerto en el que el servidor escuchará.
    """
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)

    print(f"Iniciando servidor HTTP en http://{host}:{port}/")
    print("Presiona Ctrl+C para detener el servidor.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor HTTP...")
    finally:
        httpd.server_close()
        print("Servidor HTTP cerrado correctamente.")


if __name__ == "__main__":
    run_server()
