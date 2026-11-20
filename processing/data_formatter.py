
import pandas as pd

from config.keywords import KEYWORDS


def results_to_dataframe(filtered_data: dict, raw_data: dict = None) -> pd.DataFrame:
    """Fusionne les résultats des tableaux et des recherches dans les pages."""

    rows = []

    for study_id, study_results in filtered_data.items():

        table_results = study_results.get("table_results", {})
        page_results = study_results.get("page_results", {})

        row = {
            "study_id": study_id,
            "source_file": (
                raw_data.get(study_id, {}).get("source_file")
                if raw_data else None
            ),
        }

        # Résultats issus des tableaux du résumé
        row.update(table_results)

        # Résultats issus des recherches par mots-clés dans les pages
        for field_name in KEYWORDS:
            result = page_results.get(field_name, {})
            row[field_name] = result.get("value")

        rows.append(row)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).set_index("study_id")
