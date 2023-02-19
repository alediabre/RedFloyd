import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import pairwise_logrank_test
from lifelines import CoxPHFitter
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from matplotlib_venn import venn2
import numpy as np
import math
import edades

apachepatient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/apachePatientResult.csv.gz', compression='gzip')
apachepredvar = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/apachePredVar.csv.gz', compression='gzip')
patient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz', compression='gzip')
medication = pd.read_csv('./dataframes/standard_medication.csv.gz', compression='gzip')
admissiondx = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/admissionDx.csv.gz', compression='gzip')


#Normaliza la edad y añade columna de imc y las de estado para las curvas de supervivencia
patient = edades.normaliza_edad(patient)
patient["imc"] = patient.apply(lambda row: row.admissionweight / math.pow(row.admissionheight/100,2), axis=1)
patient = patient[patient["admissionheight"]>80]

patient['estadofallecimientos'] = patient['unitdischargestatus'].apply(lambda x : 1 if x == 'Expired' else 0)
patient['estadoaltas'] = patient['unitdischargestatus'].apply(lambda x : 0 if x == 'Expired' else 1)

#Obtiene el diagnóstico de admisión del paciente por subtipo
def standardadmit(s):
    div = s.split('|Diagnosis|')[1].split('|')[0].strip()
    return div

admissiondx['standarddiagnosis'] = admissiondx['admitdxpath'].apply(lambda s : standardadmit(s) if '|All' in s else 'None')
admissiondx = admissiondx[admissiondx['standarddiagnosis']!='None']


#Une las tablas para añadir la información de apache y diagnostico de entrada
#df = patient.merge(apachepatient,on='patientunitstayid').merge(apachepredvar,on="patientunitstayid")
df = patient.merge(admissiondx, on='patientunitstayid')
#df = df[df["apacheversion"]=="IV"]
#df = df[df["predictedicumortality"]!=-1]


def cohorte(df, tipo):
    return df[df['standarddiagnosis']==tipo]

dfc = cohorte(df, 'Cardiovascular')


#Crea un diccionario con todos los medicamentos usados en cada estancia
med_per_unitstay = medication.merge(dfc, on='patientunitstayid')
#print(med_per_unitstay['standarddrugname'].value_counts().index.tolist()[:100])

dict_med_unit = {}
for n,m in med_per_unitstay.groupby('patientunitstayid'):
    values = set(m['standarddrugname'].values.tolist())
    dict_med_unit[n]=values


#Crea un diccionario con todos las estancias en las que se ha usado cada medicamento
dictvenn = {}
for n,m in med_per_unitstay.groupby('standarddrugname'):
    values = set(m['patientunitstayid'].values.tolist())
    dictvenn[n]=values


#PLOT VENN DIAGRAMS FOR MEDICAMENTS
lista_medicamentos = ['HYDROCHLOROTHIAZIDE','LISINOPRIL','AMLODIPINE']
conjuntos_by_stay = [set(dictvenn[med]) for med in lista_medicamentos]
venn3(subsets=conjuntos_by_stay, set_labels=lista_medicamentos)
plt.show()


#PLOT SURVIVAL CURVES
fig, ax = plt.subplots()

def plot_by_atr(df,atributo):
    for attr in dfc[atributo].unique():
        if str(attr) != 'nan':
            kmf = KaplanMeierFitter()
            dff = df[df[atributo]==attr]
            kmf.fit(dff['unitdischargeoffset'], dff['estadoaltas'], label=str(attr))
            kmf.plot(ax=ax, ci_show=False)


def plot_by_med(dfc,meds,dict_meds):
    frames = []
    for med in meds:
        kmf = KaplanMeierFitter()
        dff = dfc[dfc['patientunitstayid'].apply(lambda x: (x in dict_meds.keys()) and med in dict_meds[x])]
        dff.loc[:,['grupo']] = med
        frames.append(dff)
        kmf.fit(dff['unitdischargeoffset'], dff['estadoaltas'], label=str(med))
        kmf.plot(ax=ax, ci_show=False)
    
    concatenado = pd.concat(frames, ignore_index=True)
    results = pairwise_logrank_test(concatenado['unitdischargeoffset'],concatenado['grupo'],concatenado['estadoaltas'])
    print(results.summary)
    plt.title('Curvas de supervivencia')
    plt.xlabel('Tiempo (minutos)')
    plt.ylabel('Probabilidad de supervivencia')
    #plt.text(0.5, 0.5, results.p_value, fontsize=22)
    plt.legend()
    plt.show()


#Regresión de Cox
cph = CoxPHFitter()
cph.fit(dfc, duration_col='unitdischargeoffset', event_col='estadoaltas', formula='age_x + imc')
cph.print_summary()
cph.plot()
cph.print_covariate_summary()




plot_by_med(dfc,lista_medicamentos,dict_med_unit)



# Añadir etiquetas al gráfico
