"""Configuración de la conexión a MySQL a partir de variables de entorno.

Las variables se leen del entorno y, si existe, de un archivo `.env` en el directorio actual o en
la raíz del repositorio. Las variables ya definidas en el entorno tienen prioridad.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]

VALORES_POR_DEFECTO = {
    "WIKITUNES_BD_HOST": "127.0.0.1",
    "WIKITUNES_BD_PUERTO": "3306",
    "WIKITUNES_BD_NOMBRE": "musica",
    "WIKITUNES_BD_USUARIO": "wikitunes",
    "WIKITUNES_BD_CLAVE": "wikitunes",
    "WIKITUNES_BD_CLAVE_ROOT": "raiz_wikitunes",
}


@dataclass(frozen=True)
class ConfiguracionBD:
    """Datos de conexión a la base `musica`."""

    host: str
    puerto: int
    nombre: str
    usuario: str
    clave: str
    clave_root: str

    @classmethod
    def desde_entorno(cls) -> "ConfiguracionBD":
        """Construye la configuración desde el entorno (y `.env`), con valores por defecto."""
        load_dotenv(Path.cwd() / ".env", override=False)
        load_dotenv(RAIZ_REPOSITORIO / ".env", override=False)

        def valor(variable: str) -> str:
            return os.getenv(variable, VALORES_POR_DEFECTO[variable])

        try:
            puerto = int(valor("WIKITUNES_BD_PUERTO"))
        except ValueError as error:
            raise ValueError(
                "WIKITUNES_BD_PUERTO debe ser un número entero, "
                f"no {valor('WIKITUNES_BD_PUERTO')!r}"
            ) from error
        return cls(
            host=valor("WIKITUNES_BD_HOST"),
            puerto=puerto,
            nombre=valor("WIKITUNES_BD_NOMBRE"),
            usuario=valor("WIKITUNES_BD_USUARIO"),
            clave=valor("WIKITUNES_BD_CLAVE"),
            clave_root=valor("WIKITUNES_BD_CLAVE_ROOT"),
        )

    def parametros_conector(self, *, como_root: bool = False) -> dict[str, object]:
        """Parámetros para `mysql.connector.connect`, del usuario de la app o de `root`."""
        return {
            "host": self.host,
            "port": self.puerto,
            "database": self.nombre,
            "user": "root" if como_root else self.usuario,
            "password": self.clave_root if como_root else self.clave,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "connection_timeout": 5,
        }
