import pandas as pd
import numpy as np
import re
import seaborn as sns
import matplotlib.pyplot as plt
import drugstandards as drugs



medication = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/medication.csv.gz', compression='gzip')


medication=medication[:200]


def standard_drugnames(df, threshold=0.8):

    def abrevia_drug(s):
        if s.__class__ == float:
            return ""
        else:
            ss = s.split(" ")
            ls = [s for s in ss if re.match("[A-Z]{5,}", s)!=None]
            return " ".join(ls)

    l = [abrevia_drug(s) for s in df["drugname"].values.tolist()]
    lista = drugs.standardize(l, thresh = threshold)
    df["standarddrugname"] = pd.Series(lista)

    return df


m = standard_drugnames(medication)
print(m.loc[:,["drugname","standarddrugname"]])
