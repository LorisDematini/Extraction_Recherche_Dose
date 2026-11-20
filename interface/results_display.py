
import streamlit as st

from processing.data_formatter import results_to_dataframe


def render_results(raw_data: dict, filtered_data: dict):
    """Affiche tous les résultats dans un tableau unique."""

    st.subheader("Résultats de l'extraction")

    dataframe = results_to_dataframe(filtered_data, raw_data)

    st.metric("Études extraites", len(dataframe))

    if not dataframe.empty:
        total_fields = len(dataframe.columns) - 1  # source_file
        found_fields = dataframe.drop(
            columns=["source_file"],
            errors="ignore"
        ).notna().sum().sum()

    st.dataframe(
        dataframe,
        use_container_width=True,
        height=600,
    )

    st.download_button(
        label="Télécharger les résultats (CSV)",
        data=dataframe.to_csv(index=True).encode("utf-8-sig"),
        file_name="resultats_extraction.csv",
        mime="text/csv",
    )
