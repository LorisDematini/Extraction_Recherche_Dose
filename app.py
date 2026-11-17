
import os
import json
import tempfile
import streamlit as st
import pandas as pd

import docx_to_pdf
import read_pdf
import extract_info

import sys

# Initialisation COM uniquement sous Windows
if sys.platform == "win32":
    import pythoncom
else:
    pythoncom = None


st.set_page_config(
    page_title="Recherche Dose",
    layout="wide"
)

st.title("Recherche Dose")
st.write(
    "Extraction automatisée de données à partir "
    "de protocoles de recherche au format DOCX."
)

st.divider()


# ==================================================
# 1. SÉLECTION DES FICHIERS
# ==================================================


docx_files = st.file_uploader(
    "Sélectionner un dossier avec des DOCX ou PDF",
    type=["docx", "pdf"],
    accept_multiple_files="directory"
)

for f in docx_files or []:
    print(f.name.split("/")[-1])

files = [
    f for f in (docx_files or [])
    if not f.name.split("/")[-1].startswith("~$") and not f.name.split("/")[-1].startswith(".")
]

if files:
    n_docx = sum(f.name.lower().endswith(".docx") for f in files)
    n_pdf = sum(f.name.lower().endswith(".pdf") for f in files)

    st.info(
        f"{len(files)} fichiers détectés : "
        f"{n_docx} DOCX et {n_pdf} PDF."
    )

    with st.expander("Voir les fichiers sélectionnés"):
        for f in files:
            st.write(f.name)


# ==================================================
# 2. LANCEMENT DE L'EXTRACTION
# ==================================================

if st.button(
    "Lancer l'extraction",
    type="primary",
    disabled=not files
):

    try:

        with tempfile.TemporaryDirectory() as temp_dir:

            docx_folder = os.path.join(temp_dir, "docx")
            pdf_folder = os.path.join(temp_dir, "pdf")

            os.makedirs(docx_folder, exist_ok=True)
            os.makedirs(pdf_folder, exist_ok=True)

            # ------------------------------------------
            # 1. Enregistrement et séparation des fichiers
            # ------------------------------------------

            docx_count = 0
            pdf_count = 0

            with st.spinner("Préparation des fichiers..."):

                for uploaded_file in files:

                    filename = os.path.basename(
                        uploaded_file.name.replace("\\", "/")
                    )

                    extension = os.path.splitext(filename)[1].lower()

                    if extension == ".docx":

                        filepath = os.path.join(
                            docx_folder,
                            filename
                        )

                        with open(filepath, "wb") as f:
                            f.write(uploaded_file.getvalue())

                        docx_count += 1

                    elif extension == ".pdf":

                        filepath = os.path.join(
                            pdf_folder,
                            filename
                        )

                        with open(filepath, "wb") as f:
                            f.write(uploaded_file.getvalue())

                        pdf_count += 1

            # ------------------------------------------
            # 2. Conversion DOCX -> PDF uniquement
            # ------------------------------------------

            
            if docx_count > 0:

                with st.spinner(
                    f"Conversion de {docx_count} fichiers DOCX en PDF..."
                ):

                    # MAC WINDOWS
                    if sys.platform == "win32":
                        pythoncom.CoInitialize()

                    try:
                        docx_to_pdf.convert_docx_folder(
                            docx_folder,
                            pdf_folder
                        )

                    finally:
                        if sys.platform == "win32":
                            pythoncom.CoUninitialize()

            # ------------------------------------------
            # 3. Vérification des PDF
            # ------------------------------------------

            pdf_files = [
                f for f in os.listdir(pdf_folder)
                if f.lower().endswith(".pdf")
            ]

            if not pdf_files:
                st.error("Aucun fichier PDF disponible pour l'extraction.")
                st.stop()

            st.success(
                f"{len(pdf_files)} PDF disponibles pour l'extraction "
                f"({pdf_count} PDF importés + PDF issus des DOCX)."
            )

            # ------------------------------------------
            # 4. Extraction des tableaux et FirstPage
            # ------------------------------------------

            with st.spinner("Extraction des données PDF..."):

                raw_data = (
                    read_pdf.extract_study_tables_from_pdfs(
                        pdf_folder
                    )
                )

            # ------------------------------------------
            # 5. Extraction des champs normalisés
            # ------------------------------------------

            with st.spinner("Identification des informations..."):

                filtered_data = (
                    extract_info.extract_information(raw_data)
                )

            # ------------------------------------------
            # 6. Conservation des résultats
            # ------------------------------------------

            st.session_state["raw_data"] = raw_data
            st.session_state["filtered_data"] = filtered_data

        st.success("Extraction terminée !")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")



# ==================================================
# 3. AFFICHAGE DES RÉSULTATS
# ==================================================

if "filtered_data" in st.session_state:

    raw_data = st.session_state["raw_data"]
    filtered_data = st.session_state["filtered_data"]

    st.divider()
    st.subheader("Résultats de l'extraction")

    st.metric("Études extraites", len(raw_data))

    # Tableau des résultats
    df = pd.DataFrame.from_dict(
        filtered_data,
        orient="index"
    )

    df.index.name = "study_id"

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )


    # ==================================================
    # EXPORT DES RÉSULTATS
    # ==================================================

    st.subheader("Export des résultats")

    json_output = json.dumps(
        filtered_data,
        indent=4,
        ensure_ascii=False
    )

    st.download_button(
        label="Télécharger le JSON filtré",
        data=json_output,
        file_name="filtered_result.json",
        mime="application/json",
        type="primary"
    )


    with st.expander("Consulter les données brutes extraites des PDF"):

        st.download_button(
            label="Télécharger le JSON brut",
            data=json.dumps(
                raw_data,
                indent=4,
                ensure_ascii=False
            ),
            file_name="result.json",
            mime="application/json"
        )

        for study_id, study in raw_data.items():

            with st.expander(study_id):
                st.json(study)
