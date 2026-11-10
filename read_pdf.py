
import os
import re
import logging
import unicodedata
import pdfplumber

from typing import Dict, List, Optional

logging.getLogger("pdfminer").setLevel(logging.ERROR)


def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


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


def is_summary_page(page_text: str, tables: List) -> bool:
    text = normalize_text(page_text)

    if not tables:
        return False

    return any(keyword in text for keyword in SUMMARY_KEYWORDS)


def is_next_section(page_text: str) -> bool:
    lines = page_text.splitlines()

    for line in lines[:15]:
        line = line.strip()

        if re.match(
            r"^(?:[2-9]|1[0-9])\s+[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ\s'’\-–:]+$",
            line
        ):
            return True

    return False


def clean_table(table: List) -> List[List[str]]:
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
                cell = re.sub(r"\s+", " ", cell).strip()
                cleaned_row.append(cell)

        if any(cleaned_row):
            cleaned.append(cleaned_row)

    return cleaned


def build_fields(rows: List[List[str]]) -> Dict[str, str]:
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


def find_acronym(fields: Dict[str, str]) -> Optional[str]:
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
            if value.strip():
                return value.strip().split()[0].strip(":;,. ")

    return None


def extract_first_page_text(page) -> str:
    text = page.extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()


def extract_study_tables_from_pdfs(pdf_folder: str) -> Dict:

    final_data = {}

    for file_name in os.listdir(pdf_folder):

        if not file_name.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(pdf_folder, file_name)

        try:
            with pdfplumber.open(file_path) as pdf:

                first_page_text = (
                    extract_first_page_text(pdf.pages[0])
                    if pdf.pages else ""
                )

                capture_mode = False
                extracted_rows = []

                for page_number, page in enumerate(pdf.pages, start=1):

                    page_text = page.extract_text() or ""
                    tables = page.extract_tables()

                    if not capture_mode:
                        if not is_summary_page(page_text, tables):
                            continue

                        capture_mode = True

                    else:
                        if is_next_section(page_text):
                            break

                    for table in tables:
                        cleaned_table = clean_table(table)

                        if cleaned_table:
                            extracted_rows.extend(cleaned_table)

                if not extracted_rows:
                    continue

                fields = build_fields(extracted_rows)
                acronym = find_acronym(fields)

                if not acronym:
                    acronym = os.path.splitext(file_name)[0]

                # Évite d'écraser une étude en cas d'acronyme identique
                study_id = acronym
                counter = 2

                while study_id in final_data:
                    study_id = f"{acronym}_{counter}"
                    counter += 1

                final_data[study_id] = {
                    "FirstPage": first_page_text,
                    "source_file": file_name,
                    **fields
                }

        except Exception as e:
            print(f"Erreur sur {file_name}: {e}")

    return final_data
