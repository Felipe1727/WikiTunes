"""Textos de la interfaz: traducción de valores del esquema, fechas y normalización."""

import unicodedata
from datetime import date

TIPOS_ALBUM = {
    "LP": "LP",
    "EP": "EP",
    "Single": "Sencillo",
    "Compilation": "Compilación",
    "Live": "En vivo",
    "Soundtrack": "Banda sonora",
    "Remix": "Remezclas",
}

TIPOS_ARTISTA = {
    "Solista": "Solista",
    "Banda": "Banda",
    "Duo": "Dúo",
    "Colectivo": "Colectivo",
    "Orquesta": "Orquesta",
}

ROLES = {
    "Principal": "Intérprete principal",
    "Featuring": "Invitado (feat.)",
    "Remixer": "Remezclador",
    "Compositor": "Compositor",
    "Letrista": "Letrista",
    "Productor": "Productor",
    "Arreglista": "Arreglista",
    "Ingeniero": "Ingeniero",
    "Musico de sesion": "Músico de sesión",
}

MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def traducir(valor: str | None, tabla: dict[str, str]) -> str:
    """Traduce un valor del esquema (ENUM en inglés) al texto que ve el usuario."""
    if valor is None:
        return "—"
    return tabla.get(valor, valor)


def fecha_larga(fecha: date | None) -> str:
    """`1974-06-01` → `1 de junio de 1974`."""
    if fecha is None:
        return "fecha desconocida"
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def normalizar(texto: str) -> str:
    """Texto para comparar al buscar: sin mayúsculas, tildes ni comillas tipográficas."""
    texto = texto.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    descompuesto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).strip()
