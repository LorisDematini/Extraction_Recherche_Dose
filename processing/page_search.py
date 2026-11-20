
import unicodedata

from config.keywords import KEYWORDS


def normalize_for_search(text: str):
    """Normalise le texte en conservant les positions originales."""

    normalized = []
    positions = []

    for index, char in enumerate(text):
        char = char.casefold()
        char = unicodedata.normalize("NFKD", char)

        char = "".join(
            c for c in char
            if not unicodedata.combining(c)
        )

        char = char.replace("’", "'").replace("‘", "'")
        char = char.replace("–", "-").replace("—", "-")

        for normalized_char in char:
            normalized.append(normalized_char)
            positions.append(index)

    return "".join(normalized), positions


def search_in_pages(
    study_data: dict,
    keywords: dict = None,
    context_size: int = 40,
) -> dict:
    """
    Recherche la première occurrence de chaque groupe de mots-clés
    dans toutes les pages d'une étude.

    Retourne un extrait avec le contexte avant et après.
    """

    if keywords is None:
        keywords = KEYWORDS

    results = {}

    pages = study_data.get("pages", {})

    # On garantit l'ordre chronologique des pages.
    for field, field_keywords in keywords.items():

        found = False

        for page_number in sorted(pages, key=lambda x: int(x)):
            page_text = pages[page_number]

            if not page_text:
                continue

            normalized_text, positions = normalize_for_search(page_text)

            # On recherche toutes les formulations du champ
            # et on conserve celle qui apparaît la première.
            occurrences = []

            for keyword in field_keywords:

                if not keyword:
                    continue

                normalized_keyword, _ = normalize_for_search(keyword)

                if not normalized_keyword:
                    continue

                position = normalized_text.find(normalized_keyword)

                if position == -1:
                    continue

                original_start = positions[position]
                original_end = positions[
                    position + len(normalized_keyword) - 1
                ] + 1

                occurrences.append({
                    "position": position,
                    "start": original_start,
                    "end": original_end,
                    "keyword": keyword,
                })

            if not occurrences:
                continue

            # Première occurrence rencontrée sur cette page.
            match = min(occurrences, key=lambda x: x["position"])

            start = max(0, match["start"] - context_size)
            end = min(
                len(page_text),
                match["end"] + context_size,
            )

            context = page_text[start:end]

            results[field] = {
                "value": context,
                "keyword": match["keyword"],
                "page": page_number,
                "context": context,
            }

            found = True
            break

    return results
