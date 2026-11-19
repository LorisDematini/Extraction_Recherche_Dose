import re

from config.fields import FIELD_ALIASES
from processing.normalization import normalize


def find_registration_number(first_page: str):
    """
    Recherche un numéro au format YYYY-NNNNNN-NN-NN
    ou YYYY-NNNNNN-NN sur la première page.
    """
    if not first_page:
        return None

    patterns = [
        r"\b\d{4}-\d{6}-\d{2}-\d{2}\b",
        r"\b\d{4}-\d{6}-\d{2}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, first_page)
        if match:
            return match.group(0)

    return None


def find_value(fields: dict, aliases: list):
    """Recherche une clé par correspondance exacte, puis partielle."""
    normalized_fields = {
        normalize(key): value
        for key, value in fields.items()
    }
    normalized_aliases = [normalize(alias) for alias in aliases]

    # Priorité aux correspondances exactes.
    for alias in normalized_aliases:
        if alias in normalized_fields:
            return normalized_fields[alias]

    # Puis recherche des alias contenus dans les intitulés.
    for alias in normalized_aliases:
        for normalized_key, value in normalized_fields.items():
            if alias and alias in normalized_key:
                return value

    return None


def extract_information(data: dict) -> dict:
    """Ne conserve que les champs définis dans config/fields.py."""
    results = {}

    for study_id, study_data in data.items():
        extracted = {}

        for field_name, aliases in FIELD_ALIASES.items():
            if field_name == "numero_enregistrement":
                extracted[field_name] = find_registration_number(
                    study_data.get("FirstPage", "")
                )
            else:
                extracted[field_name] = find_value(study_data, aliases)

        results[study_id] = extracted

    return results
