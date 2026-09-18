import sqlite3
from contextlib import contextmanager


class PartiesRepository:
    """
    Accès aux données brutes. En séance 1 on utilise sqlite3 directement ;
    en séance 2 cette classe sera portée vers SQLAlchemy SANS changer
    la signature de ses méthodes (donc sans impact sur le service ni le controller).
    """

    def __init__(self, db_path):
        self.db_path = db_path

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _build_filters(annee=None, serveur=None, jeu=None, file=None):
        """
        Construit la clause WHERE et les paramètres associés, de façon à ce
        que la liste, le total et les futures agrégations appliquent
        exactement les mêmes règles de filtrage.
        """
        clauses = []
        params = {}

        if annee is not None:
            clauses.append("strftime('%Y', p.debut) = :annee")
            params["annee"] = str(annee)

        if serveur is not None:
            clauses.append("s.code = :serveur")
            params["serveur"] = serveur

        if jeu is not None:
            clauses.append("j.nom = :jeu")
            params["jeu"] = jeu

        if file is not None:
            clauses.append("f.nom = :file")
            params["file"] = file

        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        return where_sql, params

    _BASE_FROM = """
        FROM parties p
        JOIN serveurs s ON s.id = p.serveur_id
        JOIN files f ON f.id = p.file_id
        JOIN jeux j ON j.id = f.jeu_id
    """

    _COLONNES_TRI = {
        "date": "p.debut",
        "attente": "p.attente_secondes",
    }

    def list_parties(self, annee=None, serveur=None, jeu=None, file=None,
                      tri="date", ordre="asc", limit=20, offset=0):
        where_sql, params = self._build_filters(annee, serveur, jeu, file)
        colonne_tri = self._COLONNES_TRI[tri]
        ordre_sql = "ASC" if ordre == "asc" else "DESC"

        query = f"""
            SELECT p.id, p.debut, p.attente_secondes, p.duree_minutes,
                   s.code AS serveur, j.nom AS jeu, f.nom AS file
            {self._BASE_FROM}
            {where_sql}
            ORDER BY {colonne_tri} {ordre_sql}
            LIMIT :limit OFFSET :offset
        """
        params["limit"] = limit
        params["offset"] = offset

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def count_parties(self, annee=None, serveur=None, jeu=None, file=None):
        where_sql, params = self._build_filters(annee, serveur, jeu, file)
        query = f"SELECT COUNT(*) AS total {self._BASE_FROM} {where_sql}"

        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()
            return row["total"]

    def get_referentiel(self):
        with self._connect() as conn:
            serveurs = [dict(r) for r in conn.execute(
                "SELECT id, code, nom, region FROM serveurs ORDER BY nom"
            ).fetchall()]
            jeux = [dict(r) for r in conn.execute(
                "SELECT id, nom FROM jeux ORDER BY nom"
            ).fetchall()]
            files = [dict(r) for r in conn.execute(
                "SELECT id, jeu_id, nom FROM files ORDER BY nom"
            ).fetchall()]
            annees_rows = conn.execute(
                "SELECT DISTINCT strftime('%Y', debut) AS annee FROM parties ORDER BY annee"
            ).fetchall()
            annees = [int(r["annee"]) for r in annees_rows if r["annee"] is not None]

            return {
                "serveurs": serveurs,
                "jeux": jeux,
                "files": files,
                "annees": annees,
            }
