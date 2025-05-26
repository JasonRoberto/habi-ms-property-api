from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Property:
    """
    Representa un inmueble de la tabla 'property'.
    """
    id: int
    address: str
    city: str
    price: int
    description: Optional[str] = None
    year: Optional[int] = None


@dataclass
class Status:
    """
    Representa un estado de la tabla 'status'.
    """
    id: int
    name: str
    label: str


@dataclass
class StatusHistory:
    """
    Representa un registro de la tabla 'status_history'.
    """
    id: int
    property_id: int
    status_id: int
    update_date: datetime

# --- Modelo para la Salida de la API ---


@dataclass
class PropertyAPIResponseDTO:
    """
    Representa la estructura de datos de un inmueble tal como se devuelve en la API.
    """
    direccion: str
    ciudad: str
    estado: str
    precio_venta: int
    descripcion: Optional[str] = None
