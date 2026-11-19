import pandas as pd


def results_to_dataframe(filtered_data: dict) -> pd.DataFrame:
    """Transforme les résultats filtrés en DataFrame indexé par étude."""
    dataframe = pd.DataFrame.from_dict(filtered_data, orient="index")
    dataframe.index.name = "study_id"
    return dataframe
