
import re

from config.fields import FIELD_ALIASES
from processing.normalization import normalize
from processing.page_search import search_in_pages


def find_registration_number(first_page: str):
    """Recherche le numéro d'enregistrement sur la première page."""

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

    normalized_aliases = [
        normalize(alias)
        for alias in aliases
    ]

    for alias in normalized_aliases:
        if alias in normalized_fields:
            return normalized_fields[alias]

    for alias in normalized_aliases:
        for normalized_key, value in normalized_fields.items():
            if alias and alias in normalized_key:
                return value

    return None


def extract_information(data: dict) -> dict:
    """
    Exécute indépendamment les deux extractions :

    - FIELD_ALIASES : recherche dans les tableaux.
    - KEYWORDS : recherche dans toutes les pages.
    """

    results = {}

    for study_id, study_data in data.items():

        # 1. Extraction depuis les tableaux du résumé
        summary_fields = study_data.get("summary_fields", {})

        table_results = {}

        for field_name, aliases in FIELD_ALIASES.items():

            if field_name == "numero_enregistrement":
                pages = study_data.get("pages", {})
                first_page = pages.get(1, pages.get("1", ""))

                table_results[field_name] = find_registration_number(
                    first_page
                )
            else:
                table_results[field_name] = find_value(
                    summary_fields,
                    aliases,
                )

        # 2. Extraction depuis toutes les pages
        page_results = search_in_pages(
            study_data,
            context_size=40,
        )

        # 3. Conservation séparée des deux résultats
        results[study_id] = {
            "table_results": table_results,
            "page_results": page_results,
        }

    return results
