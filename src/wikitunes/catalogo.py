"""Consultas del catálogo musical: procedimientos almacenados, fichas y listados.

`Catalogo` recibe una conexión abierta (ver `wikitunes.conexion.conectar`) y devuelve dataclasses
de `wikitunes.modelos`. Las consultas centrales usan los procedimientos almacenados; las fichas y
los listados son SELECT de solo lectura.
"""

from collections import defaultdict
from datetime import date

from wikitunes.conexion import Fila, consultar, llamar_procedimiento
from wikitunes.modelos import (
    AparicionEnAlbum,
    Arte,
    CreditoArtista,
    CreditoPersona,
    FichaArtista,
    FichaCancion,
    FichaGenero,
    FichaPersona,
    Integrante,
    Membresia,
    NodoGenero,
    Participacion,
    Pista,
    Referencia,
    ResumenAlbum,
    Tracklist,
)

NOMBRE_PERSONA = "COALESCE(p.nombre_conocido, p.nombre_legal)"


def _resumen_album(fila: Fila) -> ResumenAlbum:
    return ResumenAlbum(
        id=fila["album_id"],
        titulo=fila["titulo"],
        tipo=fila["tipo"],
        fecha_lanzamiento=fila["fecha_lanzamiento"],
    )


class Catalogo:
    """Acceso de solo lectura al catálogo musical."""

    def __init__(self, conexion) -> None:
        self.conexion = conexion

    def _consultar(self, sql: str, *parametros) -> list[Fila]:
        return consultar(self.conexion, sql, parametros)

    # --- Listados para el autocompletado --------------------------------------------------

    def personas(self) -> list[Referencia]:
        filas = self._consultar(
            f"SELECT p.persona_id AS id, {NOMBRE_PERSONA} AS nombre FROM persona p ORDER BY nombre"
        )
        return [Referencia(f["id"], f["nombre"]) for f in filas]

    def artistas(self) -> list[Referencia]:
        filas = self._consultar("SELECT artista_id AS id, nombre FROM artista ORDER BY nombre")
        return [Referencia(f["id"], f["nombre"]) for f in filas]

    def albumes(self) -> list[ResumenAlbum]:
        filas = self._consultar(
            "SELECT album_id, titulo, tipo, fecha_lanzamiento FROM album "
            "ORDER BY fecha_lanzamiento, titulo"
        )
        return [_resumen_album(f) for f in filas]

    def generos(self) -> list[Referencia]:
        filas = self._consultar("SELECT genero_id AS id, nombre FROM genero ORDER BY nombre")
        return [Referencia(f["id"], f["nombre"]) for f in filas]

    def canciones(self) -> list[Referencia]:
        filas = self._consultar(
            "SELECT cancion_id AS id, titulo AS nombre FROM cancion ORDER BY titulo"
        )
        return [Referencia(f["id"], f["nombre"]) for f in filas]

    # --- Procedimientos almacenados -------------------------------------------------------

    def canciones_de_persona(self, persona: Referencia) -> list[Participacion]:
        """`sp_canciones_de_persona` con el nombre exacto, solo con las filas de esa persona."""
        (filas,) = llamar_procedimiento(self.conexion, "sp_canciones_de_persona", persona.nombre)
        filas = [f for f in filas if f["persona"] == persona.nombre]
        # La vista tiene el id de cada canción: sirve para navegar a su ficha.
        ids: dict[tuple, list[int]] = defaultdict(list)
        for f in self._consultar(
            "SELECT cancion_id, cancion, via, rol FROM v_participacion_persona "
            "WHERE persona_id = %s ORDER BY cancion_id",
            persona.id,
        ):
            ids[(f["cancion"], f["via"], f["rol"])].append(f["cancion_id"])
        resultado = []
        for f in filas:
            candidatos = ids.get((f["cancion"], f["via"], f["rol"]))
            resultado.append(
                Participacion(
                    cancion_id=candidatos.pop(0) if candidatos else None,
                    cancion=f["cancion"],
                    via=f["via"],
                    rol=f["rol"],
                )
            )
        return resultado

    def subgeneros(self, genero: str) -> list[NodoGenero]:
        """`sp_subgeneros`: el género y todos sus subgéneros, en orden de ruta."""
        (filas,) = llamar_procedimiento(self.conexion, "sp_subgeneros", genero)
        return [NodoGenero(f["genero_id"], f["nombre"], int(f["nivel"]), f["ruta"]) for f in filas]

    def tracklist(self, album_id: int) -> Tracklist | None:
        """`sp_tracklist`: pistas y resumen del álbum (los dos resultados del procedimiento)."""
        conjuntos = llamar_procedimiento(self.conexion, "sp_tracklist", album_id)
        pistas, resumen = conjuntos[0], conjuntos[1]
        if not resumen:
            return None
        ids = {
            (f["numero_disco"], f["numero_pista"]): f["cancion_id"]
            for f in self._consultar(
                "SELECT numero_disco, numero_pista, cancion_id FROM album_cancion "
                "WHERE album_id = %s",
                album_id,
            )
        }
        datos = resumen[0]
        return Tracklist(
            album_id=album_id,
            titulo=datos["titulo"],
            tipo=datos["tipo"],
            cantidad_pistas=int(datos["pistas"]),
            duracion_total=datos["duracion_total"],
            pistas=[
                Pista(
                    disco=f["disco"],
                    numero=f["pista"],
                    cancion_id=ids.get((f["disco"], f["pista"])),
                    cancion=f["cancion"],
                    interpretes=f["interpretes"],
                    duracion=f["duracion"],
                )
                for f in pistas
            ],
        )

    def integrantes_en_fecha(self, artista: str, fecha: date) -> list[Integrante]:
        """`sp_integrantes_en_fecha`, con el id de cada persona para navegar."""
        (filas,) = llamar_procedimiento(self.conexion, "sp_integrantes_en_fecha", artista, fecha)
        ids = {
            (f["persona"], f["fecha_inicio"]): f["persona_id"]
            for f in self._consultar(
                f"SELECT p.persona_id, {NOMBRE_PERSONA} AS persona, m.fecha_inicio "
                "FROM membresia m JOIN persona p ON p.persona_id = m.persona_id "
                "JOIN artista a ON a.artista_id = m.artista_id WHERE a.nombre = %s",
                artista,
            )
        }
        return [
            Integrante(
                persona_id=ids.get((f["persona"], f["fecha_inicio"])),
                persona=f["persona"],
                rol=f["rol"],
                fecha_inicio=f["fecha_inicio"],
                fecha_fin=f["fecha_fin"],
            )
            for f in filas
        ]

    def historial_integrantes(self, artista: str) -> list[Integrante]:
        """`sp_historial_integrantes`: todos los periodos de membresía del artista."""
        (filas,) = llamar_procedimiento(self.conexion, "sp_historial_integrantes", artista)
        return [
            Integrante(f["persona_id"], f["persona"], f["rol"], f["fecha_inicio"], f["fecha_fin"])
            for f in filas
        ]

    def artistas_de_album(self, album_id: int) -> list[Referencia]:
        """Los artistas de la portada del álbum, en su orden."""
        filas = self._consultar(
            "SELECT a.artista_id AS id, a.nombre FROM album_artista aa "
            "JOIN artista a ON a.artista_id = aa.artista_id WHERE aa.album_id = %s "
            "ORDER BY aa.orden, a.nombre",
            album_id,
        )
        return [Referencia(f["id"], f["nombre"]) for f in filas]

    # --- Fichas ---------------------------------------------------------------------------

    def arte_de_artista(self, artista_id: int) -> Arte | None:
        filas = self._consultar(
            "SELECT arte, estilo FROM arte_artista WHERE artista_id = %s", artista_id
        )
        return Arte(filas[0]["arte"], filas[0]["estilo"]) if filas else None

    def ficha_artista(self, artista_id: int) -> FichaArtista | None:
        filas = self._consultar(
            "SELECT a.artista_id, a.nombre, a.tipo, a.anio_formacion, a.anio_disolucion, "
            "c.nombre AS ciudad, pa.nombre AS pais FROM artista a "
            "LEFT JOIN ciudad c ON c.ciudad_id = a.ciudad_origen_id "
            "LEFT JOIN pais pa ON pa.pais_id = c.pais_id WHERE a.artista_id = %s",
            artista_id,
        )
        if not filas:
            return None
        a = filas[0]
        generos = self._consultar(
            "SELECT g.nombre FROM artista_genero ag JOIN genero g ON g.genero_id = ag.genero_id "
            "WHERE ag.artista_id = %s ORDER BY g.nombre",
            artista_id,
        )
        discografia = self._consultar(
            "SELECT al.album_id, al.titulo, al.tipo, al.fecha_lanzamiento FROM album_artista aa "
            "JOIN album al ON al.album_id = aa.album_id WHERE aa.artista_id = %s "
            "ORDER BY al.fecha_lanzamiento, al.titulo",
            artista_id,
        )
        return FichaArtista(
            id=a["artista_id"],
            nombre=a["nombre"],
            tipo=a["tipo"],
            anio_formacion=a["anio_formacion"],
            anio_disolucion=a["anio_disolucion"],
            ciudad=a["ciudad"],
            pais=a["pais"],
            generos=[g["nombre"] for g in generos],
            arte=self.arte_de_artista(artista_id),
            discografia=[_resumen_album(f) for f in discografia],
            integrantes=self.historial_integrantes(a["nombre"]),
        )

    def ficha_persona(self, persona_id: int) -> FichaPersona | None:
        filas = self._consultar(
            f"SELECT p.persona_id, {NOMBRE_PERSONA} AS nombre, p.nombre_legal, "
            "p.fecha_nacimiento, p.fecha_fallecimiento, c.nombre AS ciudad, pa.nombre AS pais "
            "FROM persona p LEFT JOIN ciudad c ON c.ciudad_id = p.ciudad_nacimiento_id "
            "LEFT JOIN pais pa ON pa.pais_id = c.pais_id WHERE p.persona_id = %s",
            persona_id,
        )
        if not filas:
            return None
        p = filas[0]
        membresias = self._consultar(
            "SELECT a.artista_id, a.nombre AS artista, m.rol, m.fecha_inicio, m.fecha_fin "
            "FROM membresia m JOIN artista a ON a.artista_id = m.artista_id "
            "WHERE m.persona_id = %s ORDER BY m.fecha_inicio, a.nombre",
            persona_id,
        )
        return FichaPersona(
            id=p["persona_id"],
            nombre=p["nombre"],
            nombre_legal=p["nombre_legal"],
            fecha_nacimiento=p["fecha_nacimiento"],
            fecha_fallecimiento=p["fecha_fallecimiento"],
            ciudad=p["ciudad"],
            pais=p["pais"],
            membresias=[
                Membresia(
                    m["artista_id"], m["artista"], m["rol"], m["fecha_inicio"], m["fecha_fin"]
                )
                for m in membresias
            ],
        )

    def ficha_cancion(self, cancion_id: int) -> FichaCancion | None:
        filas = self._consultar(
            "SELECT cancion_id, titulo, duracion_seg FROM cancion WHERE cancion_id = %s", cancion_id
        )
        if not filas:
            return None
        c = filas[0]
        interpretes = self._consultar(
            "SELECT a.artista_id, a.nombre, ca.rol FROM credito_artista ca "
            "JOIN artista a ON a.artista_id = ca.artista_id WHERE ca.cancion_id = %s "
            "ORDER BY ca.rol, a.nombre",
            cancion_id,
        )
        creditos = self._consultar(
            f"SELECT p.persona_id, {NOMBRE_PERSONA} AS persona, cp.rol FROM credito_persona cp "
            "JOIN persona p ON p.persona_id = cp.persona_id WHERE cp.cancion_id = %s "
            "ORDER BY cp.rol, persona",
            cancion_id,
        )
        generos = self._consultar(
            "SELECT g.nombre FROM cancion_genero cg JOIN genero g ON g.genero_id = cg.genero_id "
            "WHERE cg.cancion_id = %s ORDER BY g.nombre",
            cancion_id,
        )
        albumes = self._consultar(
            "SELECT al.album_id, al.titulo, al.tipo, al.fecha_lanzamiento, ac.numero_disco, "
            "ac.numero_pista FROM album_cancion ac JOIN album al ON al.album_id = ac.album_id "
            "WHERE ac.cancion_id = %s ORDER BY al.fecha_lanzamiento",
            cancion_id,
        )
        return FichaCancion(
            id=c["cancion_id"],
            titulo=c["titulo"],
            duracion_seg=c["duracion_seg"],
            interpretes=[
                CreditoArtista(f["artista_id"], f["nombre"], f["rol"]) for f in interpretes
            ],
            creditos=[CreditoPersona(f["persona_id"], f["persona"], f["rol"]) for f in creditos],
            generos=[g["nombre"] for g in generos],
            albumes=[
                AparicionEnAlbum(
                    f["album_id"],
                    f["titulo"],
                    f["tipo"],
                    f["fecha_lanzamiento"],
                    f["numero_disco"],
                    f["numero_pista"],
                )
                for f in albumes
            ],
        )

    def ficha_genero(self, genero: str) -> FichaGenero | None:
        """El árbol del género y los artistas y álbumes del género o de sus subgéneros."""
        arbol = self.subgeneros(genero)
        if not arbol:
            return None
        ids = [nodo.id for nodo in arbol]
        marcadores = ", ".join(["%s"] * len(ids))
        artistas = self._consultar(
            "SELECT DISTINCT a.artista_id AS id, a.nombre FROM artista_genero ag "
            f"JOIN artista a ON a.artista_id = ag.artista_id WHERE ag.genero_id IN ({marcadores}) "
            "ORDER BY a.nombre",
            *ids,
        )
        albumes = self._consultar(
            "SELECT DISTINCT al.album_id, al.titulo, al.tipo, al.fecha_lanzamiento "
            "FROM album_genero ag JOIN album al ON al.album_id = ag.album_id "
            f"WHERE ag.genero_id IN ({marcadores}) ORDER BY al.fecha_lanzamiento, al.titulo",
            *ids,
        )
        return FichaGenero(
            nombre=arbol[0].nombre,
            arbol=arbol,
            artistas=[Referencia(f["id"], f["nombre"]) for f in artistas],
            albumes=[_resumen_album(f) for f in albumes],
        )
