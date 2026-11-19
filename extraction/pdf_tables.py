from typing import Dict, List

from processing.normalization import normalize_text


def clean_table(table: List) -> List[List[str]]:
    """Nettoie les cellules d'un tableau extrait par pdfplumber."""
    cleaned = []

    for row in table:
        if not row:
            continue

        cleaned_row = []

        for cell in row:
            if cell is None:
                cleaned_row.append("")
            else:
                cell = str(cell)
                cell = " ".join(cell.split()).strip()
                cleaned_row.append(cell)

        if any(cleaned_row):
            cleaned.append(cleaned_row)

    return cleaned


def build_fields(rows: List[List[str]]) -> Dict[str, str]:
    """Reconstitue les paires intitulé/valeur à partir des lignes des tableaux."""
    fields = {}
    current_key = None

    for row in rows:
        key = row[0].strip() if row else ""

        value = " ".join(
            cell.strip()
            for cell in row[1:]
            if cell and cell.strip()
        )

        if key and value:
            current_key = key

            if current_key in fields:
                fields[current_key] += " " + value
            else:
                fields[current_key] = value

        elif not key and value and current_key:
            fields[current_key] += " " + value

    return fields


def find_acronym(fields: Dict[str, str]):
    """Recherche un acronyme dans les intitulés reconstruits."""
    acronym_keywords = [
        "acronyme",
        "acronym",
        "abbreviated title",
        "abbreviated name",
        "study code",
        "study reference",
    ]

    for key, value in fields.items():
        normalized_key = normalize_text(key)

        if any(keyword in normalized_key for keyword in acronym_keywords):
            if value and value.strip():
                return value.strip().split()[0].strip(":;,. ")

    return None
