
import os
import docx2pdf


def convert_docx_folder(input_folder: str, output_folder: str):
    """
    Convertit tous les fichiers DOCX d'un dossier en PDF.
    Retourne le nombre de fichiers convertis.
    """

    os.makedirs(output_folder, exist_ok=True)

    docx_files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".docx") and not f.startswith("~$")
    ]

    if not docx_files:
        return 0

    docx2pdf.convert(input_folder, output_folder)

    pdf_files = [
        f for f in os.listdir(output_folder)
        if f.lower().endswith(".pdf")
    ]

    return len(pdf_files)