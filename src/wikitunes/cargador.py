"""Cargador de los datos de la demo: CSV por tabla y arte ASCII en archivos de texto.

Uso:
    python -m wikitunes.cargador [--directorio datos]

Cada carga reemplaza el contenido de todas las tablas por el de los CSV en una sola transacción.
Si algo falla, no queda ningún cambio y el error indica el archivo y la línea.
"""

import argparse
import csv
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import mysql.connector

from wikitunes.configuracion import RAIZ_REPOSITORIO, ConfiguracionBD

# Orden que respeta las llaves foráneas. `genero` y `sello` son autorreferenciadas: en sus CSV
# los padres van antes que los hijos.
ORDEN_TABLAS: tuple[str, ...] = (
    "pais",
    "ciudad",
    "genero",
    "sello",
    "persona",
    "artista",
    "membresia",
    "artista_genero",
    "arte_artista",
    "album",
    "album_artista",
    "album_genero",
    "cancion",
    "cancion_genero",
    "album_cancion",
    "credito_artista",
    "credito_persona",
)

TABLA_ARTE = "arte_artista"
COLUMNAS_CSV_ARTE = ("artista_id", "archivo", "estilo")
DIRECTORIO_ARTE = "arte"


class ErrorDeCarga(Exception):
    """Error al cargar los datos, con un mensaje en español listo para mostrar."""


@dataclass
class FilaCsv:
    """Una fila de un CSV con la línea en la que termina (para los mensajes de error)."""

    linea: int
    valores: dict[str, str | None]


@dataclass
class TablaCsv:
    ruta: Path
    columnas: list[str]
    filas: list[FilaCsv] = field(default_factory=list)


def leer_csv(ruta: Path) -> TablaCsv:
    """Lee un CSV (UTF-8, RFC 4180) con encabezado. Las celdas vacías pasan a `None`."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        lector = csv.reader(archivo)
        try:
            columnas = next(lector)
        except StopIteration as error:
            raise ErrorDeCarga(
                f"{ruta.name}: el archivo está vacío (falta el encabezado)"
            ) from error
        columnas = [columna.strip() for columna in columnas]
        tabla = TablaCsv(ruta=ruta, columnas=columnas)
        for registro in lector:
            if not registro:
                continue
            if len(registro) != len(columnas):
                raise ErrorDeCarga(
                    f"{ruta.name}, línea {lector.line_num}: tiene {len(registro)} celdas "
                    f"y el encabezado tiene {len(columnas)}"
                )
            valores = {
                columna: (celda if celda != "" else None)
                for columna, celda in zip(columnas, registro, strict=True)
            }
            tabla.filas.append(FilaCsv(linea=lector.line_num, valores=valores))
    return tabla


def validar_columnas(tabla: TablaCsv, nombre_tabla: str, columnas_tabla: set[str]) -> None:
    """Falla si el encabezado nombra columnas que la tabla no tiene."""
    desconocidas = [columna for columna in tabla.columnas if columna not in columnas_tabla]
    if desconocidas:
        raise ErrorDeCarga(
            f"{tabla.ruta.name}: columna desconocida para la tabla {nombre_tabla}: "
            + ", ".join(desconocidas)
        )


def leer_arte(directorio_arte: Path, archivo: str) -> str:
    """Lee un archivo de arte dentro de `directorio_arte`, sin los saltos de línea finales."""
    base = directorio_arte.resolve()
    ruta = (base / archivo).resolve()
    if not ruta.is_relative_to(base):
        raise ErrorDeCarga(f"el archivo de arte {archivo!r} está fuera de {DIRECTORIO_ARTE}/")
    if not ruta.is_file():
        raise ErrorDeCarga(f"no existe el archivo de arte {DIRECTORIO_ARTE}/{archivo}")
    # newline="" conserva el texto tal cual (sin traducir finales de línea).
    with ruta.open(encoding="utf-8", newline="") as contenido:
        return contenido.read().rstrip("\n")


def filas_de_arte(tabla: TablaCsv, directorio_arte: Path) -> TablaCsv:
    """Convierte `arte_artista.csv` (artista_id, archivo, estilo) en filas de la tabla."""
    validar_columnas(tabla, TABLA_ARTE, set(COLUMNAS_CSV_ARTE))
    if "archivo" not in tabla.columnas or "artista_id" not in tabla.columnas:
        raise ErrorDeCarga(f"{tabla.ruta.name}: faltan las columnas artista_id y archivo")
    resultado = TablaCsv(ruta=tabla.ruta, columnas=["artista_id", "arte", "estilo"])
    for fila in tabla.filas:
        archivo = fila.valores["archivo"]
        if archivo is None:
            raise ErrorDeCarga(f"{tabla.ruta.name}, línea {fila.linea}: falta el archivo")
        try:
            arte = leer_arte(directorio_arte, archivo)
        except ErrorDeCarga as error:
            raise ErrorDeCarga(f"{tabla.ruta.name}, línea {fila.linea}: {error}") from error
        resultado.filas.append(
            FilaCsv(
                linea=fila.linea,
                valores={
                    "artista_id": fila.valores["artista_id"],
                    "arte": arte,
                    "estilo": fila.valores.get("estilo"),
                },
            )
        )
    return resultado


def _columnas_de_tabla(cursor, nombre_tabla: str) -> set[str]:
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s",
        (nombre_tabla,),
    )
    return {fila[0] for fila in cursor.fetchall()}


def _vaciar_tablas(cursor) -> None:
    # Sin comprobar llaves foráneas solo durante el borrado (tablas autorreferenciadas).
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    try:
        for nombre_tabla in reversed(ORDEN_TABLAS):
            cursor.execute(f"DELETE FROM `{nombre_tabla}`")
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def _insertar(cursor, nombre_tabla: str, tabla: TablaCsv) -> None:
    columnas = ", ".join(f"`{columna}`" for columna in tabla.columnas)
    marcadores = ", ".join(["%s"] * len(tabla.columnas))
    sql = f"INSERT INTO `{nombre_tabla}` ({columnas}) VALUES ({marcadores})"
    for fila in tabla.filas:
        try:
            cursor.execute(sql, tuple(fila.valores[columna] for columna in tabla.columnas))
        except mysql.connector.Error as error:
            raise ErrorDeCarga(
                f"{tabla.ruta.name}, línea {fila.linea}: {error.msg} (error {error.errno})"
            ) from error


def leer_directorio(directorio: Path) -> dict[str, TablaCsv]:
    """Lee los CSV presentes en `directorio`, en el orden de carga. Los ausentes se omiten."""
    tablas: dict[str, TablaCsv] = {}
    for nombre_tabla in ORDEN_TABLAS:
        ruta = directorio / f"{nombre_tabla}.csv"
        if not ruta.is_file():
            continue
        tabla = leer_csv(ruta)
        if nombre_tabla == TABLA_ARTE:
            tabla = filas_de_arte(tabla, directorio / DIRECTORIO_ARTE)
        tablas[nombre_tabla] = tabla
    return tablas


def cargar(conexion, directorio: Path, *, confirmar: bool = True) -> dict[str, int]:
    """Reemplaza el contenido de la base por el de `directorio` en una sola transacción.

    Devuelve cuántas filas se cargaron por tabla. Con `confirmar=False` no hace COMMIT: quien
    llama decide (las pruebas hacen ROLLBACK). Ante cualquier error deshace la transacción.
    """
    tablas = leer_directorio(directorio)
    if conexion.in_transaction:
        conexion.rollback()
    conexion.start_transaction()
    cursor = conexion.cursor()
    try:
        for nombre_tabla, tabla in tablas.items():
            validar_columnas(tabla, nombre_tabla, _columnas_de_tabla(cursor, nombre_tabla))
        _vaciar_tablas(cursor)
        for nombre_tabla, tabla in tablas.items():
            _insertar(cursor, nombre_tabla, tabla)
        if confirmar:
            conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
    return {nombre_tabla: len(tabla.filas) for nombre_tabla, tabla in tablas.items()}


def principal(argumentos: Sequence[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        prog="python -m wikitunes.cargador",
        description="Carga los datos de la demo (CSV y arte ASCII) en la base de datos.",
    )
    analizador.add_argument(
        "--directorio",
        type=Path,
        default=RAIZ_REPOSITORIO / "datos",
        help="directorio con los CSV y la carpeta arte/ (por defecto: datos/ del repositorio)",
    )
    opciones = analizador.parse_args(argumentos)

    configuracion = ConfiguracionBD.desde_entorno()
    try:
        conexion = mysql.connector.connect(**configuracion.parametros_conector(como_root=True))
    except mysql.connector.Error as error:
        print(f"No se pudo conectar a la base de datos: {error}", file=sys.stderr)
        return 1
    try:
        cantidades = cargar(conexion, opciones.directorio)
    except ErrorDeCarga as error:
        print(f"Error al cargar los datos: {error}", file=sys.stderr)
        print("No se guardó ningún cambio.", file=sys.stderr)
        return 1
    finally:
        conexion.close()

    total = sum(cantidades.values())
    print(f"Datos cargados desde {opciones.directorio}: {total} filas en {len(cantidades)} tablas.")
    for nombre_tabla, cantidad in cantidades.items():
        print(f"  {nombre_tabla}: {cantidad}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
