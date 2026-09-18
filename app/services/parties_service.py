class ValidationError(Exception):
    """Erreur de validation des paramètres de requête, portée jusqu'au controller."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


TRI_ACCEPTES = ["date", "attente"]
ORDRE_ACCEPTES = ["asc", "desc"]
LIMIT_MAX = 100


class PartiesService:
    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    def _valider_int(valeur, nom):
        if valeur is None:
            return None
        try:
            return int(valeur)
        except (TypeError, ValueError):
            raise ValidationError(f"Le paramètre '{nom}' doit être un entier valide.")

    def _valider_parametres(self, args):
        annee = self._valider_int(args.get("annee"), "annee")
        serveur = args.get("serveur")
        jeu = args.get("jeu")
        file = args.get("file")

        tri = args.get("tri", "date")
        if tri not in TRI_ACCEPTES:
            raise ValidationError(
                f"Paramètre 'tri' invalide : '{tri}'. Valeurs acceptées : {TRI_ACCEPTES}."
            )

        ordre = args.get("ordre", "asc")
        if ordre not in ORDRE_ACCEPTES:
            raise ValidationError(
                f"Paramètre 'ordre' invalide : '{ordre}'. Valeurs acceptées : {ORDRE_ACCEPTES}."
            )

        limit = self._valider_int(args.get("limit", 20), "limit")
        if limit <= 0 or limit > LIMIT_MAX:
            raise ValidationError(f"Le paramètre 'limit' doit être compris entre 1 et {LIMIT_MAX}.")

        offset = self._valider_int(args.get("offset", 0), "offset")
        if offset < 0:
            raise ValidationError("Le paramètre 'offset' doit être positif ou nul.")

        return {
            "annee": annee,
            "serveur": serveur,
            "jeu": jeu,
            "file": file,
            "tri": tri,
            "ordre": ordre,
            "limit": limit,
            "offset": offset,
        }

    def lister_parties(self, args):
        p = self._valider_parametres(args)

        data = self.repository.list_parties(
            annee=p["annee"], serveur=p["serveur"], jeu=p["jeu"], file=p["file"],
            tri=p["tri"], ordre=p["ordre"], limit=p["limit"], offset=p["offset"],
        )
        total = self.repository.count_parties(
            annee=p["annee"], serveur=p["serveur"], jeu=p["jeu"], file=p["file"],
        )

        return {
            "data": data,
            "total": total,
            "limit": p["limit"],
            "offset": p["offset"],
        }

    def referentiel(self):
        return self.repository.get_referentiel()
