import pandas as pd
import numpy as np

diagnosis = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/diagnosis.csv.gz', compression='gzip')
admission = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/admissionDx.csv.gz', compression='gzip')
patient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz', compression='gzip')

#nrows=100
#nrows=100

#a = data.sort_values(by="patientunitstayid")
#a = data.describe()
#a = data["age"]
#a = data.iloc[0]
#a = data.iloc[:,0:2]
#a = data.loc[:,["patientunitstayid", "patienthealthsystemstayid"]]
#a = data[data["patientunitstayid"]<200000]
#a = data[data["age"].isin(["30", "31"])]

def resume_diagnostico(d,column):
    d[column] = d[column].split('|')[0]
    return d

diagnosis = diagnosis.astype({"diagnosisstring": str}) #Convierte la columna en tipo str
frameDiag = diagnosis.apply(lambda s : resume_diagnostico(s,"diagnosisstring"), axis=1)
#frameDiag = diagnosis.loc[:,"diagnosisstring"]
print(frameDiag)

result = pd.merge(patient, frameDiag, on="patientunitstayid")

result = result.loc[0:40,["uniquepid","patientunitstayid","patienthealthsystemstayid","diagnosisstring","diagnosisoffset"]].sort_values(by="uniquepid")
print(result)


#admission = admission.astype({"admitdxname": str})
#frameAdm = admission.loc[:,"admitdxname"]





#vc = frameDiag.value_counts()
#print(vc)

