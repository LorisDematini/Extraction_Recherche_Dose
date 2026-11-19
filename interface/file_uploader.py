import streamlit as st


def render_file_uploader():
    """Affiche le sélecteur de fichiers et retourne les fichiers utilisables."""
    uploaded_files = st.file_uploader(
        "Sélectionner un dossier avec des DOCX ou PDF",
        type=["docx", "pdf"],
        accept_multiple_files="directory",
    )

    files = [
        file
        for file in (uploaded_files or [])
        if not file.name.split("/")[-1].startswith(("~$", "."))
    ]

    if files:
        docx_count = sum(file.name.lower().endswith(".docx") for file in files)
        pdf_count = sum(file.name.lower().endswith(".pdf") for file in files)

        st.info(
            f"{len(files)} fichiers détectés : "
            f"{docx_count} DOCX et {pdf_count} PDF."
        )

        with st.expander("Voir les fichiers sélectionnés"):
            for file in files:
                st.write(file.name)

    return files
