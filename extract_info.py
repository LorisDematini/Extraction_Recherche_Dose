
import re
import unicodedata


def normalize(text):
    """Normalise un texte pour faciliter la comparaison des intitulés."""

    text = str(text).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return text.strip()


def find_registration_number(first_page):
    """
    Recherche un numéro d'enregistrement au format :
    YYYY-NNNNNN-NN-NN ou YYYY-NNNNNN-NN.
    """

    if not first_page:
        return None

    pattern = r"\b\d{4}-\d{6}-\d{2}-\d{2}\b"
    pattern_2 = r"\b\d{4}-\d{6}-\d{2}\b"

    match = re.search(pattern, first_page)

    if match:
        return match.group(0)

    match = re.search(pattern_2, first_page)

    return match.group(0) if match else None


field_aliases = {

    "titre": [
        "titre",
        "titre complet",
        "title",
        "full title",
    ],

    "Acronyme": [
        "acronyme",
        "acronym",
        "Acronyme/référence",
        "Acronym/reference",
    ],

    "maladie": [
        "Population of study participants",
        "Population concernée",
        "Population of trial subjects",
    ],

    "investigateur_principal": [
        "investigateur",
        "investigator",
        "investigateur coordonnateur",
        "coordinating investigator",
    ],

    "numero_enregistrement": [],

    "traitement_recherche": [
        "traitement à l'essai",
        "traitements à l'essai",
        "Traitement(s) à l’essai",
        "traitement expérimental",
        "investigational treatment",
        "study treatment",
        "Investigational medicinal product(s)",
        "caInvestigational medicinal product(s)",
        "Investigation al medicinal product(s)",
        "Investigational medicinal product",
    ],
}


def find_value(fields, aliases):
    """
    Recherche une clé correspondant aux alias.
    Priorité aux correspondances exactes,
    puis aux correspondances partielles.
    """

    normalized_fields = {
        normalize(key): (key, value)
        for key, value in fields.items()
    }

    normalized_aliases = [
        normalize(alias) for alias in aliases
    ]

    # 1. Correspondance exacte
    for alias in normalized_aliases:
        if alias in normalized_fields:
            return normalized_fields[alias][1]

    # 2. Correspondance partielle
    for alias in normalized_aliases:
        for normalized_key, (original_key, value) in normalized_fields.items():
            if alias and alias in normalized_key:
                return value

    return None


def extract_information(data):
    """
    Reçoit les données extraites des PDF
    et retourne uniquement les champs recherchés.
    """

    results = {}

    for study_id, study_data in data.items():

        extracted = {}

        for field_name, aliases in field_aliases.items():

            if field_name == "numero_enregistrement":
                extracted[field_name] = find_registration_number(
                    study_data.get("FirstPage", "")
                )

            else:
                extracted[field_name] = find_value(
                    study_data,
                    aliases
                )

        results[study_id] = extracted

    return results
