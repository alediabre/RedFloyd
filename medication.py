import pandas as pd
import re
import math
import drugstandards as drugs


def standard_infusiondrugnames(df): #infusiondrug -> stdrugname, stinfusionrate

    def parse_drug(s):

        if s.count("(")==1:
            ss = s.split("(")
            r = ss[0].strip()
            medida = ss[1][:-1]
        elif s.count("(")==2:
            ss = s.split(")")[1].split("(")
            r = ss[0].strip()
            medida = ss[1][:-1]
        else:
            r = s
            medida = None

        return r,medida

    l = df["drugname"].apply(lambda s : parse_drug(s)).tolist()
    drugs = [i for i,_ in l]
    medidas = [j for _,j in l]
    drugrate = df["drugrate"].values.tolist()

    stdrugrate = []
    for i in range(len(drugrate)):
        m,drate = medidas[i],drugrate[i]
        if m == None:
            m = ""
        if drate == "ERROR":
            drate = float(0)
        else:    
            drate = float(drate)        
            if "mcg" in m:
                drate = drate/1000
            if "min" in m:
                drate = drate*60
        stdrugrate.append(drate)

    df["stdrugname"] = pd.Series(drugs)
    df["stdrugrate"] = pd.Series(stdrugrate)

    return df


def infusionstop (df):

    def calcula_fin(row):
        infr = float(row.infusionrate)
        vol = float(row.volumeoffluid)
        if math.isnan(infr) or math.isnan(vol) or infr==0:
            return row.infusionoffset
        else:
            n = math.floor((float(row.volumeoffluid) / infr)*60)
            return int(n) + row.infusionoffset
            
    df["infusionendoffset"] = df.apply(lambda row: calcula_fin(row), axis=1)
    return df

#-------------------------------------------------------------------------------------------------

def standard_drugnames(df, threshold=0.8): #medication -> standarddrugname

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
