import streamlit as st

from processing.data_formatter import results_to_dataframe


def render_results(raw_data: dict, filtered_data: dict):
    """Affiche les résultats filtrés dans un tableau Streamlit."""
    st.subheader("Résultats de l'extraction")
    st.metric("Études extraites", len(raw_data))

    dataframe = results_to_dataframe(filtered_data)

    st.dataframe(
        dataframe,
        use_container_width=True,
        height=500,
    )
