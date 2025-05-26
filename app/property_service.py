from .database_manager import DatabaseManager
from .models import PropertyAPIResponseDTO
from typing import List, Dict, Optional, Any, Tuple

class PropertyService:
    """
    Contiene la lógica de negocio para la consulta de inmuebles.
    Interactúa con DatabaseManager para obtener datos de la base de datos
    y los formatea para ser enviados por APIRequestHandler.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Inicializa el servicio con una instancia de DatabaseManager.
        Permite inyección de dependencias para facilitar pruebas y flexibilidad.
        """
        self.db_manager = db_manager or DatabaseManager()
        
    def get_properties(self, filters: Optional[Dict[str, Any]] = None) -> List[PropertyAPIResponseDTO]:
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
        filters = filters or {}
        query, params = self._build_query_and_params(filters)
        properties_from_db = self.db_manager.fetch_all(query, tuple(params))

        if properties_from_db is None:
            return []

        return self._format_properties(properties_from_db)

    def _build_query_and_params(self, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Construye la consulta SQL y los parámetros según los filtros.
        """
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
                SELECT
                    sh_outer.property_id,
                    sh_outer.status_id
                FROM
                    status_history sh_outer
                INNER JOIN (
                    SELECT
                        property_id,
                        MAX(update_date) AS max_update_date
                    FROM
                        status_history
                    GROUP BY
                        property_id
                ) sh_inner ON sh_outer.property_id = sh_inner.property_id
                    AND sh_outer.update_date = sh_inner.max_update_date
            ) latest_status_history
                ON p.id = latest_status_history.property_id
            INNER JOIN
                status s ON latest_status_history.status_id = s.id
        """

        where_clauses = ["s.name IN (%s, %s, %s)"]
        params = ["pre_venta", "en_venta", "vendido"]

        if filters.get('year') is not None:
            where_clauses.append("p.year = %s")
            params.append(filters['year'])
        
        if filters.get('city'):
            where_clauses.append("LOWER(p.city) LIKE LOWER(%s)")
            params.append(f"%{filters['city']}%")

        if filters.get('status'):
            where_clauses.append("s.name = %s")
            params.append(filters['status'])

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        return base_query, params

    def _format_properties(self, properties_from_db: List[Dict[str, Any]]) -> List[PropertyAPIResponseDTO]:
        """
        Convierte los resultados de la base de datos en DTOs para la API.
        """
        formatted_properties = []
        for prop_row in properties_from_db:
            try:
                api_response_item = PropertyAPIResponseDTO(
                    direccion=prop_row["address"],
                    ciudad=prop_row["city"],
                    estado=prop_row["current_status"],
                    precio_venta=prop_row["price"],
                    descripcion=prop_row["description"]
                )
                formatted_properties.append(api_response_item)
            except KeyError as e:
                print(f"PropertyService: Falta la clave {e} en la fila de la BD al crear PropertyAPIResponseDTO. Fila: {prop_row}")
        return formatted_properties