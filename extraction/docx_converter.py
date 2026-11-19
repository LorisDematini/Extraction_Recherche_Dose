import os

import docx2pdf


def convert_docx_folder(input_folder: str, output_folder: str) -> int:
    """Convertit les DOCX d'un dossier en PDF et retourne le nombre de PDF produits."""
    os.makedirs(output_folder, exist_ok=True)

    docx_files = [
        filename
        for filename in os.listdir(input_folder)
        if filename.lower().endswith(".docx")
        and not filename.startswith("~$")
    ]

    if not docx_files:
        return 0

    docx2pdf.convert(input_folder, output_folder)

    return sum(
        filename.lower().endswith(".pdf")
        for filename in os.listdir(output_folder)
    )
