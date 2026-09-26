"""Configuración de la aplicación: ubicación del CSV de inventario y clave de Groq."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY_CSV_PATH = PROJECT_ROOT / "data" / "inventory.csv"

INVENTORY_CSV_PATH_VAR = "INVENTORY_CSV_PATH"
GROQ_API_KEY_VAR = "GROQ_API_KEY"


@dataclass(frozen=True)
class Settings:
    inventory_csv_path: Path
    # Solo la necesita el agente; None si no está definida.
    groq_api_key: str | None


def get_settings() -> Settings:
    """Construye la configuración a partir del entorno y de `.env`.

    Las variables ya definidas en el entorno tienen prioridad sobre `.env`.
    Una ruta relativa se resuelve desde la raíz del proyecto, no desde el
    directorio de trabajo, para que el resultado no dependa de dónde se ejecute.
    """
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    raw_path = os.getenv(INVENTORY_CSV_PATH_VAR, "").strip()
    if not raw_path:
        path = DEFAULT_INVENTORY_CSV_PATH
    else:
        path = Path(raw_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path

    groq_api_key = os.getenv(GROQ_API_KEY_VAR, "").strip() or None
    return Settings(inventory_csv_path=path, groq_api_key=groq_api_key)
