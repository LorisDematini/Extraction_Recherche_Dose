import json
import os
import sys
import tempfile

import streamlit as st

from extraction.docx_converter import convert_docx_folder
from extraction.pdf_reader import extract_study_tables_from_pdfs
from extraction.information_extractor import extract_information
from interface.file_uploader import render_file_uploader
from interface.results_display import render_results
from interface.exports import render_exports


def save_uploaded_files(uploaded_files, docx_folder, pdf_folder):
    """Enregistre les fichiers importés dans les dossiers temporaires adaptés."""
    docx_count = 0
    pdf_count = 0

    for uploaded_file in uploaded_files:
        filename = os.path.basename(uploaded_file.name.replace("\\", "/"))
        extension = os.path.splitext(filename)[1].lower()

        if extension == ".docx":
            destination = os.path.join(docx_folder, filename)
            with open(destination, "wb") as output:
                output.write(uploaded_file.getvalue())
            docx_count += 1

        elif extension == ".pdf":
            destination = os.path.join(pdf_folder, filename)
            with open(destination, "wb") as output:
                output.write(uploaded_file.getvalue())
            pdf_count += 1

    return docx_count, pdf_count


def run_extraction(uploaded_files):
    """Exécute toute la chaîne de traitement et retourne les résultats."""
    with tempfile.TemporaryDirectory() as temp_dir:
        docx_folder = os.path.join(temp_dir, "docx")
        pdf_folder = os.path.join(temp_dir, "pdf")

        os.makedirs(docx_folder, exist_ok=True)
        os.makedirs(pdf_folder, exist_ok=True)

        with st.spinner("Préparation des fichiers..."):
            docx_count, imported_pdf_count = save_uploaded_files(
                uploaded_files,
                docx_folder,
                pdf_folder,
            )

        if docx_count:
            with st.spinner(f"Conversion de {docx_count} fichiers DOCX en PDF..."):
                pythoncom = None

                # docx2pdf utilise COM sous Windows.
                if sys.platform == "win32":
                    import pythoncom
                    pythoncom.CoInitialize()

                try:
                    convert_docx_folder(docx_folder, pdf_folder)
                finally:
                    if pythoncom is not None:
                        pythoncom.CoUninitialize()

        pdf_files = [
            filename
            for filename in os.listdir(pdf_folder)
            if filename.lower().endswith(".pdf")
        ]

        if not pdf_files:
            raise RuntimeError(
                "Aucun PDF disponible. Vérifiez les fichiers importés "
                "et la conversion des DOCX."
            )

        st.info(
            f"{len(pdf_files)} PDF prêts pour l'extraction "
            f"({imported_pdf_count} PDF importés + PDF issus des DOCX)."
        )

        with st.spinner("Extraction des tableaux et des informations PDF..."):
            raw_data = extract_study_tables_from_pdfs(pdf_folder)

        with st.spinner("Identification des informations recherchées..."):
            filtered_data = extract_information(raw_data)

        return raw_data, filtered_data


def main():
    st.set_page_config(
        page_title="Recherche Dose",
        layout="wide",
    )

    st.title("Recherche Dose")
    st.write(
        "Extraction automatisée de données à partir de protocoles "
        "de recherche au format DOCX ou PDF."
    )
    st.divider()

    uploaded_files = render_file_uploader()

    if st.button(
        "Lancer l'extraction",
        type="primary",
        disabled=not uploaded_files,
    ):
        try:
            raw_data, filtered_data = run_extraction(uploaded_files)

            st.session_state["raw_data"] = raw_data
            st.session_state["filtered_data"] = filtered_data

            st.success("Extraction terminée !")

        except Exception as error:
            st.error(f"Une erreur est survenue : {error}")

    if "raw_data" in st.session_state and "filtered_data" in st.session_state:
        st.divider()
        render_results(
            st.session_state["raw_data"],
            st.session_state["filtered_data"],
        )
        render_exports(
            st.session_state["raw_data"],
            st.session_state["filtered_data"],
        )


if __name__ == "__main__":
    main()
