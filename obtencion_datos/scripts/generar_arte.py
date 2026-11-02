"""Genera el arte ASCII de cada artista de la demo en `datos/arte/`.

Uso:
    uv run python obtencion_datos/scripts/generar_arte.py

Cada logo parte de una fuente de pyfiglet y se completa a mano con el rasgo que identifica al
artista (la «T» alargada de The Beatles, las alas de Wings, el teclado de Billy Preston...). El
criterio de cada uno está documentado en `obtencion_datos/README.md`.
"""

from pathlib import Path

import pyfiglet

DESTINO = Path(__file__).resolve().parents[2] / "datos" / "arte"


def figlet(texto: str, fuente: str) -> list[str]:
    """Texto en la fuente indicada, sin líneas vacías al principio ni al final."""
    lineas = [
        linea.rstrip()
        for linea in pyfiglet.figlet_format(texto, font=fuente, width=300).splitlines()
    ]
    while lineas and not lineas[-1]:
        lineas.pop()
    while lineas and not lineas[0]:
        lineas.pop(0)
    return lineas


def centrar(lineas: list[str], ancho: int) -> list[str]:
    margen = (ancho - max(len(linea) for linea in lineas)) // 2
    return [(" " * margen + linea).rstrip() for linea in lineas]


def the_beatles() -> list[str]:
    """El logo de la «T» alargada (drop-T), con «THE» pequeño sobre la B."""
    beatles = figlet("BEATLES", "ansi_regular")
    columna_t = beatles[0].index("████████") + 3
    tronco = [" " * columna_t + "██"] * 2 + [" " * columna_t + "▀▀"]
    the = ["▀█▀ █ █ █▀▀", " █  █▀█ █▀▀", " ▀  ▀ ▀ ▀▀▀"]
    return the + beatles + tronco


def king_crimson() -> list[str]:
    """Letras «ensangrentadas», en el rojo carmesí que da nombre a la banda."""
    king, crimson = figlet("KING", "bloody"), figlet("CRIMSON", "bloody")
    return centrar(king, max(len(linea) for linea in crimson)) + crimson


def john_lennon() -> list[str]:
    """Su firma manuscrita bajo sus lentes redondos."""
    lentes = [
        '   .-"""-.     .-"""-.',
        "  /       \\___/       \\",
        "  \\       /   \\       /",
        "   '-...-'     '-...-'",
    ]
    return lentes + [""] + figlet("John Lennon", "script")


def paul_mccartney() -> list[str]:
    """Firma en cursiva y su bajo Höfner de violín."""
    bajo = [
        "   .-.",
        "  (   )=========================:|",
        "   '-'   Höfner 500/1",
    ]
    return figlet("Paul McCartney", "smscript") + [""] + bajo


def george_harrison() -> list[str]:
    """Letras inclinadas entre guirnaldas de inspiración india."""
    guirnalda = "~*~" * 22
    return [guirnalda] + figlet("George Harrison", "smslant") + [guirnalda]


def ringo_starr() -> list[str]:
    """El «star» de su nombre: letras de cartel estelar entre estrellas."""
    ringo, starr = figlet("RINGO", "starwars"), figlet("STARR", "starwars")
    ancho = max(len(linea) for linea in ringo + starr)
    estrellas = "*   .   *   .   *   .   *   .   *"
    return [estrellas] + centrar(ringo, ancho) + centrar(starr, ancho) + [estrellas]


def plastic_ono_band() -> list[str]:
    """Minimalista y conceptual: minúsculas dentro de un marco."""
    texto = figlet("plastic ono band", "smslant")
    ancho = max(len(linea) for linea in texto)
    marco = "─" * (ancho + 2)
    return (
        ["┌" + marco + "┐"]
        + ["│ " + linea.ljust(ancho) + " │" for linea in texto]
        + ["└" + marco + "┘"]
    )


def wings() -> list[str]:
    """El nombre entre dos alas."""
    texto = figlet("WINGS", "ansi_shadow")
    izquierda = ["  __.--~~", " /__.-~~ ", "/_.-~~   ", "    ~-._ ", "       ~ ", "         "]
    derecha = ["~~--.__  ", " ~~-.__\\ ", "   ~~-._\\", " _.-~    ", " ~       ", "         "]
    return [
        (izquierda[i] + "  " + texto[i].ljust(40) + "  " + derecha[i]).rstrip()
        for i in range(len(texto))
    ]


def traveling_wilburys() -> list[str]:
    """Rótulo de marquesina de época entre bordes de carretera."""
    borde = "=~" * 28 + "="
    return (
        [borde]
        + centrar(figlet("Traveling", "broadway_kb"), len(borde))
        + centrar(figlet("Wilburys", "broadway_kb"), len(borde))
        + [borde]
    )


def billy_preston() -> list[str]:
    """El nombre sobre un teclado de piano."""
    teclas = [
        "|| | | || | | | || | | || | | | || | | ||",
        "||_|_|_||_|_|_|_||_|_|_||_|_|_|_||_|_|_||",
    ]
    return figlet("Billy Preston", "small_shadow") + [""] + centrar(teclas, 44)


ARTES = {
    "the_beatles": the_beatles,
    "king_crimson": king_crimson,
    "john_lennon": john_lennon,
    "paul_mccartney": paul_mccartney,
    "george_harrison": george_harrison,
    "ringo_starr": ringo_starr,
    "plastic_ono_band": plastic_ono_band,
    "wings": wings,
    "traveling_wilburys": traveling_wilburys,
    "billy_preston": billy_preston,
}


def principal() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre, generar in ARTES.items():
        lineas = [linea.rstrip() for linea in generar()]
        ruta = DESTINO / f"{nombre}.txt"
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
        print(f"{ruta.name}: {max(len(linea) for linea in lineas)} columnas, {len(lineas)} líneas")


if __name__ == "__main__":
    principal()
