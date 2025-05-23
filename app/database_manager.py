import mysql.connector
from mysql.connector import errorcode
from .db_config import DB_CONFIG

class DatabaseManager:
    """
    Gestiona todas las interacciones con la base de datos MySQL.
    Encapsula la lógica de conexión, ejecución de consultas y manejo de errores.
    """

    def __init__(self):
        """
        Inicializa el DatabaseManager con la configuración de la base de datos.
        """
        self.db_config = DB_CONFIG
        if not self.db_config:
            # Esto no debería ocurrir si db_config.py está bien y .env está cargado.
            raise ValueError("La configuración de la base de datos (DB_CONFIG) no está definida.")

    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, is_dml: bool = False):
        """
        Método privado para conectar, ejecutar una consulta y manejar la conexión/cursor.

        Args:
            query (str): La consulta SQL a ejecutar.
            params (tuple, optional): Tupla de parámetros para la consulta SQL (para consultas parametrizadas).
                                    Defaults to None.
            fetch_one (bool, optional): True para obtener solo un resultado (fetchone), 
                                        False para obtener todos (fetchall). Ignorado si is_dml es True.
                                        Defaults to False.
            is_dml (bool, optional): True si la consulta es DML (INSERT, UPDATE, DELETE) y requiere commit/rollback.
                                    Defaults to False.

        Returns:
            list or dict or int or None: 
                - Para SELECT (fetchall): Lista de diccionarios (filas).
                - Para SELECT (fetchone): Un diccionario (fila) o None si no hay resultado.
                - Para DML: Número de filas afectadas.
                - None si ocurre un error de base de datos.
        """
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)

            print(f"Ejecutando SQL: {query} con Parámetros: {params}") # Para depuración

            cursor.execute(query, params or ()) 

            if is_dml:
                conn.commit()
                print(f"Consulta DML ejecutada. Filas afectadas: {cursor.rowcount}")
                return cursor.rowcount
            elif fetch_one:
                return cursor.fetchone()
            else:
                return cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"Error de base de datos MySQL: {err}")
            print(f"Código de error MySQL: {err.errno}")
            print(f"Estado SQL: {err.sqlstate}")
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Detalle: Nombre de usuario o contraseña de base de datos incorrectos.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Detalle: La base de datos '{self.db_config.get('database')}' no existe o no es accesible.")
            
            if is_dml and conn:
                print("Realizando rollback de la transacción DML debido a un error.")
                conn.rollback()
            return None
        
        except Exception as e:
            print(f"Un error inesperado ocurrió durante la operación de base de datos: {e}")
            if is_dml and conn:
                conn.rollback()
            return None

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                # print("Conexión a la base de datos cerrada.")

    def fetch_all(self, query: str, params: tuple = None):
        """
        Ejecuta una consulta SELECT y devuelve todas las filas coincidentes.

        Args:
            query (str): La consulta SELECT a ejecutar.
            params (tuple, optional): Parámetros para la consulta. Defaults to None.

        Returns:
            list: Una lista de diccionarios, donde cada diccionario representa una fila.  Retorna una lista vacía si no hay resultados, o None si ocurre un error.
        """
        return self._execute_query(query, params, fetch_one=False, is_dml=False)

    def fetch_one(self, query: str, params: tuple = None):
        """
        Ejecuta una consulta SELECT y devuelve una única fila.

        Args:
            query (str): La consulta SELECT a ejecutar.
            params (tuple, optional): Parámetros para la consulta. Defaults to None.

        Returns:
            dict or None: Un diccionario que representa la fila, o None si no se encuentra ninguna fila o si ocurre un error.
        """
        return self._execute_query(query, params, fetch_one=True, is_dml=False)

    def execute_dml(self, query: str, params: tuple = None):
        """
        Ejecuta una consulta DML (Data Manipulation Language) como INSERT, UPDATE, DELETE.

        Args:
            query (str): La consulta DML a ejecutar.
            params (tuple, optional): Parámetros para la consulta. Defaults to None.

        Returns:
            int or None: El número de filas afectadas por la consulta DML, o None si ocurre un error.
        """
        return self._execute_query(query, params, is_dml=True)