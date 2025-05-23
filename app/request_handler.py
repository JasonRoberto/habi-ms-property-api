import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import dataclasses

from .property_service import PropertyService

class APIRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.property_service = PropertyService()
        super().__init__(request, client_address, server)


    def _send_json_response(self, status_code, data, content_type="application/json"):
        """
        Envía una respuesta HTTP en formato JSON.

        Args:
            status_code (int): El código de estado HTTP.
            data (dict or list): Los datos a enviar como JSON.
            content_type (str): El tipo de contenido de la respuesta.
        """
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _parse_filters(self, query_string):
        """
        Analiza los parámetros de filtro de la cadena de consulta (query string).
        Convierte 'year' a entero y valida 'status'.

        Args:
            query_string (str): La cadena de consulta de la URL.

        Returns:
            dict: Un diccionario con los filtros parseados y validados.
            Puede devolver un segundo valor booleano indicando si hubo errores.
        """
        parsed_query = parse_qs(query_string)
        filters = {}
        errors = []

        # Procesar filtro 'year'
        if 'year' in parsed_query:
            year_str = parsed_query['year'][0] # Toma el primer valor si se envían múltiples
            try:
                filters['year'] = int(year_str)
            except ValueError:
                errors.append(f"El valor para 'year' ('{year_str}') no es un entero válido.")

        # Procesar filtro 'city'
        if 'city' in parsed_query:
            filters['city'] = parsed_query['city'][0]

        # Procesar filtro 'status'
        if 'status' in parsed_query:
            status_value = parsed_query['status'][0]
            # Estados permitidos según los requerimientos
            allowed_statuses = ["pre_venta", "en_venta", "vendido"]
            if status_value in allowed_statuses:
                filters['status'] = status_value
            else:
                errors.append(f"El valor para 'status' ('{status_value}') no es válido. Valores permitidos: {', '.join(allowed_statuses)}.")

        return filters, errors # Devolvemos filtros válidos y lista de errores

    def do_GET(self):
        """
        Maneja las solicitudes GET entrantes.
        """
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # --- Enrutamiento Básico ---
        if path == "/properties":
            
            filters, filter_errors = self._parse_filters(parsed_url.query)

            if filter_errors:
                error_response = {"error": "Parámetros de filtro inválidos", "details": filter_errors}
                self._send_json_response(400, error_response)
                return
                

            try:
                # print(f"Solicitud GET para /properties con filtros: {filters}")
                properties = self.property_service.get_properties(filters)
                properties_as_dicts = [dataclasses.asdict(prop) for prop in properties]

                self._send_json_response(200, properties_as_dicts)
                
            except Exception as e:
                # print(f"Error interno procesando /properties: {e}")
                self._send_json_response(500, {"error": "Error interno del servidor"})

        elif path == "/health":
            self._send_json_response(200, {"status": "ok", "message": "Servidor funcionando correctamente"})
        
        else:
            self._send_json_response(404, {"error": "Endpoint no encontrado"})