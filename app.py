
import os
import json
import tempfile
import streamlit as st
import pandas as pd

import docx_to_pdf
import read_pdf
import extract_info


st.set_page_config(
    page_title="Recherche Dose",
    page_icon="📚",
    layout="wide"
)

st.title("Recherche Dose")
st.write(
    "Extraction automatisée de données à partir "
    "de protocoles de recherche au format DOCX."
)

st.divider()


st.subheader("1. Sélection des fichiers")

docx_folder = st.text_input(
    "Chemin du dossier contenant les fichiers DOCX :"
)

if docx_folder:

    if not os.path.isdir(docx_folder):
        st.error("Le dossier indiqué n'existe pas.")

    else:
        docx_files = [
            f for f in os.listdir(docx_folder)
            if f.lower().endswith(".docx")
            and not f.startswith("~$")
        ]

        st.info(f"{len(docx_files)} fichiers DOCX détectés.")

        if not docx_files:
            st.warning("Aucun fichier DOCX trouvé.")



if st.button(
    "Lancer l'extraction",
    type="primary",
    disabled=not docx_folder or not os.path.isdir(docx_folder)
):

    if not docx_files:
        st.warning("Aucun fichier à traiter.")

    else:

        try:
            with st.spinner("Conversion des fichiers DOCX en PDF..."):

                with tempfile.TemporaryDirectory() as temp_dir:

                    pdf_folder = os.path.join(temp_dir, "pdf")
                    os.makedirs(pdf_folder, exist_ok=True)

                    # 1. DOCX -> PDF
                    docx_to_pdf.convert_docx_folder(
                        docx_folder,
                        pdf_folder
                    )

                    pdf_files = [
                        f for f in os.listdir(pdf_folder)
                        if f.lower().endswith(".pdf")
                    ]

                    if not pdf_files:
                        st.error(
                            "Aucun PDF généré. "
                            "Vérifiez que Microsoft Word est installé."
                        )
                        st.stop()

                    st.success(
                        f"{len(pdf_files)} fichiers PDF générés."
                    )

                    # 2. Extraction des tableaux et FirstPage
                    with st.spinner("Extraction des données PDF..."):

                        raw_data = (
                            read_pdf.extract_study_tables_from_pdfs(
                                pdf_folder
                            )
                        )

                    # 3. Extraction des champs normalisés
                    with st.spinner("Identification des informations..."):

                        filtered_data = (
                            extract_info.extract_information(raw_data)
                        )

                    # Conservation des résultats après le dossier temporaire
                    st.session_state["raw_data"] = raw_data
                    st.session_state["filtered_data"] = filtered_data

            st.success("Extraction terminée !")

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")


if "filtered_data" in st.session_state:

    raw_data = st.session_state["raw_data"]
    filtered_data = st.session_state["filtered_data"]

    st.divider()
    st.subheader("2. Résultats de l'extraction")

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

###JSON

    st.subheader("3. Export des résultats")

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
