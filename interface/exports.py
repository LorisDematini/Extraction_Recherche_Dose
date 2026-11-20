
import json

import streamlit as st

from processing.data_formatter import results_to_dataframe


def render_exports(raw_data: dict, filtered_data: dict):
    """Affiche les exports JSON des résultats et des données brutes."""

    st.subheader("Export des résultats")

    dataframe = results_to_dataframe(filtered_data, raw_data)

    filtered_json = dataframe.to_json(
        orient="index",
        force_ascii=False,
        indent=4,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Télécharger les résultats (JSON)",
            data=filtered_json.encode("utf-8"),
            file_name="resultats_extraction.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        raw_json = json.dumps(
            raw_data,
            indent=4,
            ensure_ascii=False,
        )

        st.download_button(
            label="Télécharger les données brutes (JSON)",
            data=raw_json.encode("utf-8"),
            file_name="donnees_brutes.json",
            mime="application/json",
            use_container_width=True,
        )

    with st.expander("Consulter les données brutes extraites des PDF"):
        for study_id, study in raw_data.items():
            with st.expander(study_id):
                st.json(study)
