import pandas as pd
import polars as pl
import pyarrow
import numpy as np


def countFunctions(data, categories_systems):
    files = data.getClassified()
    categories_names = ["C_" + key for key in categories_systems if categories_systems[key]['selected']]
    systems_names = ["S_" + key + "_" + sys for key in categories_systems for sys in categories_systems[key]["systems"]]
    strains = [filename for filename in files]
    count = pd.DataFrame(0, index=np.arange(len(strains)), columns=["Strain"] + categories_names + systems_names)
    count["Strain"] = strains

    for strain_name in files:
        strain_data = files[strain_name]
        index = count.loc[count['Strain'] == strain_name].index

        for count_feature in count.columns[1:]:
            classified_feature = count_feature.replace("?", " ").split("_")
            if classified_feature[0] == "C":
                count.loc[(index, count_feature)] = len(
                    strain_data.filter(pl.col("Category").str.contains(classified_feature[1])))
            else:
                count.loc[(index, count_feature)] = len(
                    strain_data.filter((pl.col("Category").str.contains(classified_feature[1]))
                                       & (pl.col("System").str.contains(classified_feature[2]))))

    count = pl.from_pandas(count)
    return count.sort(['Strain'])

