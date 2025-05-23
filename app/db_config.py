import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Check for missing environment variables
missing_configs = []
for key, value in DB_CONFIG.items():
    if value is None:
        missing_configs.append(key.upper())

if missing_configs:
    raise ValueError(f"Error: Faltan las siguientes variables de entorno requeridas para la BD: {', '.join(missing_configs)}. "
                     "Asegúrate de que el archivo .env existe en la raíz del proyecto y está configurado correctamente.")

print("Configuración de base de datos cargada exitosamente.")