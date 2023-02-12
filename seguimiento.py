import pandas as pd
import numpy as np
import re
import seaborn as sns
import math
import matplotlib.pyplot as plt



diagnosis = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/diagnosis.csv.gz', compression='gzip')
patient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz', compression='gzip')
nursecare = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/nurseCare.csv.gz', compression='gzip')


###############################################################

def tipo_diagnostico(d,column):
        d[column] = d[column].split('|')[0]
        return d

diagnosis = diagnosis.astype({"diagnosisstring": str}) #Convierte la columna en tipo str
diagnosis = diagnosis.apply(lambda s : tipo_diagnostico(s,"diagnosisstring"), axis=1)




def nursecares_hour(tipo,care):
    global diagnosis
    global patient
    global nursecare

    def regex_filter(val):
        if val:
            if re.match(tipo,val)!=None:
                return True
            else:
                return False
        else:
            return False

    def parse_offset(d,column):
        d[column] = math.floor(d[column]/60)
        return d

    
    diagtype = diagnosis[diagnosis['diagnosisstring'].apply(regex_filter)] #solo con diagnostico tipo TYPE



    patdiag = pd.merge(diagtype, patient, on="patientunitstayid")
    patdiag = patdiag.loc[:,["uniquepid","patientunitstayid","patienthealthsystemstayid"]]
    patdiag = patdiag.drop_duplicates(subset=["uniquepid"])

    carepattype = pd.merge(patdiag, nursecare, on="patientunitstayid")
    carepattype = carepattype.loc[:,["uniquepid","patientunitstayid","patienthealthsystemstayid","cellattribute","cellattributevalue","nursecareoffset"]]
    carepattype = carepattype.apply(lambda s : parse_offset(s,"nursecareoffset"), axis=1) #offset de minutos a horas


    grouped = carepattype.groupby(["uniquepid","nursecareoffset"])
    registro = dict(zip(range(0,100,5),[0 for _ in range(0,100,5)]))

    for name,group in grouped:

        c = group["cellattribute"].value_counts()
        try: 
            num = c[care]

        except KeyError as e:
            num = 0
        
        h = name[1]
        h = h - (h%5)
        if h in registro.keys():
            temp = registro[h]
            registro[h] = temp + num

    df = pd.DataFrame(registro.items(), columns=['Horas', 'Valor'])
    t = pd.DataFrame([tipo for _ in range(0,100,5)], columns=['Diagnostico'])

    df = pd.concat([df,t], axis=1)
    return df



diagnosticos = diagnosis.diagnosisstring.unique()


df = pd.concat([nursecares_hour(d,"Hygiene/ADLs") for d in diagnosticos], axis=0)

df = df.pivot(index='Diagnostico', columns='Horas', values='Valor')
print(df)




sns.set_theme(style="whitegrid")

f,ax = plt.subplots(figsize=(9,6))
sns.heatmap(df, annot=True, fmt="d", linewidths=.5, ax=ax)
plt.show()