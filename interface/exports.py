import json

import streamlit as st


def render_exports(raw_data: dict, filtered_data: dict):
    """Affiche les boutons de téléchargement des résultats JSON."""
    st.subheader("Export des résultats")

    filtered_json = json.dumps(
        filtered_data,
        indent=4,
        ensure_ascii=False,
    )

    st.download_button(
        label="Télécharger le JSON filtré",
        data=filtered_json,
        file_name="filtered_result.json",
        mime="application/json",
        type="primary",
    )

    with st.expander("Consulter les données brutes extraites des PDF"):
        raw_json = json.dumps(
            raw_data,
            indent=4,
            ensure_ascii=False,
        )

        st.download_button(
            label="Télécharger le JSON brut",
            data=raw_json,
            file_name="result.json",
            mime="application/json",
        )

        for study_id, study in raw_data.items():
            with st.expander(study_id):
                st.json(study)
