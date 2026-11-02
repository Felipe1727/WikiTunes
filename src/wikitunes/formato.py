"""Formato de duraciones y periodos para mostrarlos en la interfaz."""

from datetime import date, timedelta


def formatear_duracion(duracion: timedelta | int | None) -> str:
    """Duración como `m:ss`, o `h:mm:ss` si pasa de una hora. `None` → `"—"`."""
    if duracion is None:
        return "—"
    segundos = int(duracion.total_seconds()) if isinstance(duracion, timedelta) else int(duracion)
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)
    if horas:
        return f"{horas}:{minutos:02d}:{segundos:02d}"
    return f"{minutos}:{segundos:02d}"


def formatear_periodo(inicio: date | None, fin: date | None) -> str:
    """Periodo en años: `1972–1974`, `1969–` si sigue abierto, `1970` si es el mismo año."""
    if inicio is None and fin is None:
        return "—"
    desde = str(inicio.year) if inicio else "?"
    if fin is None:
        return f"{desde}–"
    if inicio is not None and inicio.year == fin.year:
        return desde
    return f"{desde}–{fin.year}"
