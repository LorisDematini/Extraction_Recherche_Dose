import re
import unicodedata


def normalize(text) -> str:
    """Normalise un intitulé pour faciliter la comparaison des clés et alias."""
    text = str(text).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def normalize_text(text) -> str:
    """Normalise le texte extrait des pages PDF."""
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()
