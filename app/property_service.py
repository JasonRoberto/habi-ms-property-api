from .database_manager import DatabaseManager
from .models import PropertyAPIResponseDTO
from typing import List, Dict, Optional

class PropertyService:
    """
    Contiene la lógica de negocio para la consulta de inmuebles.
    Interactúa con DatabaseManager para obtener datos de la base de datos
    y los formatea para ser enviados por APIRequestHandler.
    """

    def __init__(self):
        """
        Inicializa el servicio con una instancia de DatabaseManager.
        """
        self.db_manager = DatabaseManager()
        
    def get_properties(self, filters: Optional[Dict[str, any]] = None) -> List[PropertyAPIResponseDTO]:
        """
        Obtiene una lista de inmuebles aplicando los filtros especificados.

        Args:
            filters (dict, optional): Un diccionario con los filtros a aplicar.
                Claves posibles: 'year' (int), 'city' (str), 'status' (str).
                Defaults to None (sin filtros adicionales más allá de los estados permitidos).

        Returns:
            List[PropertyAPIResponseDTO]: Una lista de instancias de PropertyAPIResponseDTO.
            Retorna una lista vacía si no hay resultados o si ocurre un error.
        """
        if filters is None:
            filters = {}

        # Base de la consulta SQL para obtener las propiedades con su último estado.
        # Esta consulta une las tablas property, status_history y status
        base_query = """
            SELECT
                p.address,
                p.city,
                s.name AS current_status,
                p.price,
                p.description
            FROM
                property p
            INNER JOIN (
                -- Subconsulta para obtener el último status_id para cada property_id
                -- basado en la fecha más reciente en status_history.
                SELECT
                    sh_outer.property_id,
                    sh_outer.status_id
                FROM
                    status_history sh_outer
                INNER JOIN (
                    -- Subconsulta para encontrar la fecha máxima de actualización (max_update_date)
                    -- para cada property_id en status_history.
                    SELECT
                        property_id,
                        MAX(update_date) AS max_update_date
                    FROM
                        status_history
                    GROUP BY
                        property_id
                ) sh_inner ON sh_outer.property_id = sh_inner.property_id AND sh_outer.update_date = sh_inner.max_update_date
            ) latest_status_history ON p.id = latest_status_history.property_id
            INNER JOIN
                status s ON latest_status_history.status_id = s.id
        """

        where_clauses = []
        params = []

        # Solo inmuebles con estados "pre_venta", "en_venta" o "vendido" deben ser visibles.
        where_clauses.append("s.name IN (%s, %s, %s)")
        params.extend(["pre_venta", "en_venta", "vendido"])

        if 'year' in filters and filters['year'] is not None:
            where_clauses.append("p.year = %s")
            params.append(filters['year'])
        
        if 'city' in filters and filters['city']:
            # búsqueda flexible
            where_clauses.append("LOWER(p.city) LIKE LOWER(%s)")
            params.append(f"%{filters['city']}%")

        if 'status' in filters and filters['status']:
            where_clauses.append("s.name = %s")
            params.append(filters['status'])
        
        final_query = base_query
        if where_clauses:
            final_query += " WHERE " + " AND ".join(where_clauses)
        
        # final_query += " ORDER BY p.price DESC"

        # print(f"PropertyService - Consulta SQL Final: {final_query}")
        # print(f"PropertyService - Parámetros: {tuple(params)}")

        properties_from_db = self.db_manager.fetch_all(final_query, tuple(params))

        if properties_from_db is None:
            # print("PropertyService: Error al obtener propiedades de la base de datos.")
            return []

        formatted_properties = []
        for prop_row in properties_from_db:
            try:
                api_response_item = PropertyAPIResponseDTO(
                    direccion=prop_row["address"],
                    ciudad=prop_row["city"],
                    estado=prop_row["current_status"], # 'current_status' alias de s.name
                    precio_venta=prop_row["price"],
                    descripcion=prop_row["description"]
                )
                formatted_properties.append(api_response_item)
            except KeyError as e:
                print(f"PropertyService: Falta la clave {e} en la fila de la BD al crear PropertyAPIResponseDTO. Fila: {prop_row}")
        
        return formatted_properties