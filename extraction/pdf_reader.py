
import logging
import os
import re
from typing import Dict

import pdfplumber

from extraction.pdf_tables import build_fields, clean_table, find_acronym
from processing.normalization import normalize_text

logging.getLogger("pdfminer").setLevel(logging.ERROR)


SUMMARY_KEYWORDS = [
    "resume synoptique",
    "resume de l'etude",
    "resume de l'essai",
    "resume du protocole",
    "summary",
    "study summary",
    "trial summary",
    "study synopsis",
    "synopsis",
    "protocol summary",
    "resume",
]


def is_summary_page(page_text: str, tables: list) -> bool:
    """Indique si une page semble contenir le résumé tabulaire du protocole."""
    text = normalize_text(page_text)

    if not tables:
        return False

    return any(keyword in text for keyword in SUMMARY_KEYWORDS)


def is_next_section(page_text: str) -> bool:
    """Détecte le début d'une section numérotée après le résumé."""
    lines = page_text.splitlines()

    for line in lines[:15]:
        line = line.strip()

        if re.match(
            r"^(?:[2-9]|1[0-9])\s+[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ\s'’\-–:]+$",
            line,
        ):
            return True

    return False


def extract_page_text(page) -> str:
    """Extrait le texte d'une page sur une seule ligne."""
    text = page.extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()


def extract_all_pages(pdf) -> Dict[int, str]:
    """Extrait toutes les pages du PDF individuellement."""
    pages = {}

    for page_number, page in enumerate(pdf.pages, start=1):
        pages[page_number] = extract_page_text(page)

    return pages


def extract_study_tables_from_pdfs(pdf_folder: str) -> Dict:
    """
    Parcourt les PDF, récupère le texte de toutes les pages
    et reconstruit les champs du résumé du protocole.
    """
    final_data = {}

    for file_name in os.listdir(pdf_folder):
        if not file_name.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_folder, file_name)

        try:
            with pdfplumber.open(file_path) as pdf:

                # 1. Extraction du texte de toutes les pages
                pages = extract_all_pages(pdf)

                # 2. Recherche du résumé et extraction des tableaux
                capture_mode = False
                extracted_rows = []

                for page_number, page in enumerate(pdf.pages, start=1):

                    page_text = pages[page_number]
                    tables = page.extract_tables()

                    if not capture_mode:
                        if not is_summary_page(page_text, tables):
                            continue

                        capture_mode = True

                    elif is_next_section(page_text):
                        break

                    for table in tables:
                        cleaned_table = clean_table(table)

                        if cleaned_table:
                            extracted_rows.extend(cleaned_table)

                if not extracted_rows:
                    logging.warning(
                        "Aucun tableau de résumé détecté dans %s",
                        file_name,
                    )
                    continue

                # 3. Reconstruction des champs du résumé
                fields = build_fields(extracted_rows)
                acronym = find_acronym(fields)

                if not acronym:
                    acronym = os.path.splitext(file_name)[0]

                # 4. Gestion des acronymes identiques
                study_id = acronym
                counter = 2

                while study_id in final_data:
                    study_id = f"{acronym}_{counter}"
                    counter += 1

                # 5. Conservation des données
                final_data[study_id] = {
                    "source_file": file_name,
                    "pages": pages,
                    "summary_fields": fields,
                }

        except Exception:
            logging.exception(
                "Erreur pendant la lecture du fichier %s",
                file_name,
            )

    return final_data
