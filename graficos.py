import plotly.graph_objects as go
import numpy as np
import pandas as pd
from itertools import product



medication = pd.read_csv('./dataframes/standard_medication.csv.gz', compression='gzip')
patient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz', compression='gzip')
diagnosis = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/diagnosis.csv.gz', compression='gzip')
    

#SCALE = 30 #minutos que hay en cada intervalo de offset en el que se hace el conteo
#DRUGS = 5 #numero de medicaciones a mostrar (las mas repetidas)


#Recibe un dataframe de pacientes, un dataframe de diagnosticos y una cadena con el tipo de pacientes segun el diagnostico
#Devuelve un dataframe con los datos de las estancias de los pacientes con el tipo de diagnostico
def cohorte_tipo(patient,diagnosis,tipo,pacientes_unicos=False):
    
    diagnosis = diagnosis.astype({"diagnosisstring": str}) #Convierte la columna en tipo str
    diagnosis["diagnosisstring"] = diagnosis['diagnosisstring'].apply(lambda s : s.split('|')[0])

    def regex_filter(val):
            if val:
                if val == tipo:
                    return True
                else:
                    return False
            else:
                return False

    diagnosistipo = diagnosis[diagnosis['diagnosisstring'].apply(regex_filter)] #solo con diagnostico del tipo
    df = patient.merge(diagnosistipo,on='patientunitstayid')
    if pacientes_unicos == True:
        df = df.drop_duplicates(subset=["uniquepid"])
    return df

#------------------------------------------------------------------------------------------------

#Recibe un dataframe de medicacion, una cohorte (de pacientes o de estancias), la escala en minutos en la que se subdivide el tiempo, 
#un offset minimo y maximo de tiempo, y la lista de medicamentos a tener en cuenta
#Devuelve un dataframe con la medicación, el intervalo de tiempo, y la cuenta correspondiente de ese medicamento en ese intervalo para la cohorte
def tabla_medicamentos(medication, cohorte, scale, minoffset=None, maxoffset=None, drugnames=None):

    df = cohorte.merge(medication,on='patientunitstayid')
    df = df.loc[:,["uniquepid","patientunitstayid","standarddrugname","drugstartoffset","drugstopoffset"]]

    if maxoffset == None:
        maxoffset = df["drugstopoffset"].max()
    if minoffset == None:
        minoffset = df["drugstartoffset"].min()

    if drugnames == None:
        drugnames = df["standarddrugname"].unique().tolist()

    offsetlist = list(range(minoffset - (minoffset % scale) ,maxoffset + (maxoffset % scale), scale))

    combinations = [p for p in product(drugnames, offsetlist)]

    dru = pd.Series([d for d,_ in combinations])
    tmp = pd.Series([t for _,t in combinations])
    cnt = pd.Series([((df.standarddrugname == d) & (df.drugstartoffset <= t) & (df.drugstopoffset >= t)).sum() for d,t in combinations])

    df = pd.concat([dru,tmp,cnt], keys=["standarddrugname","offsetinterval","count"], axis=1)
    return df

#----------------------------------------------------------------------------------------------------

#Muestra graficamente el uso de un medicamento por una cohorte a lo largo de la estancia en UCI
#El parametro ndrugs indica el número de medicamentos a mostrar, y el parámetro absolute si los valores serán absolutos o relativos
def muestra_grafica_medicamentos(medication,cohorte,scale,ndrugs,minoffset=None,maxoffset=None,absolute=False):

    medication_cohorte = cohorte.merge(medication,on='patientunitstayid')
    medication_cohorte = medication_cohorte.loc[:,["uniquepid","patientunitstayid","standarddrugname","drugstartoffset","drugstopoffset"]]
    druglist = medication['standarddrugname'].value_counts()[:ndrugs].index.tolist()

    df = tabla_medicamentos(medication,cohorte,scale,minoffset,maxoffset,druglist)

    array_dict = {}
    for drug in druglist:
        array_dict[f'x_{drug}'] = df[df['standarddrugname']==drug]['offsetinterval']/60
        array_dict[f'y_{drug}'] = df[df['standarddrugname']==drug]['count']
        if absolute == False:
            array_dict[f'y_{drug}'] = (array_dict[f'y_{drug}'] - array_dict[f'y_{drug}'].min()) / (array_dict[f'y_{drug}'].max() - array_dict[f'y_{drug}'].min()) # we normalize the array (min max normalization)
        else:
            array_dict[f'y_{drug}'] = array_dict[f'y_{drug}']


    fig = go.Figure()
    for index, drug in enumerate(druglist):
        fig.add_trace(go.Scatter(
                                x=[minoffset/60, maxoffset/60], y=np.full(2, len(druglist)-index),
                                mode='lines',
                                line_color='white'))
        
        fig.add_trace(go.Scatter(
                                x=array_dict[f'x_{drug}'],
                                y=array_dict[f'y_{drug}'] + (len(druglist)-index) + 0,
                                fill='tonexty',
                                name=f'{drug}'))
        
        # plotly.graph_objects' way of adding text to a figure
        fig.add_annotation(
                            x=minoffset/60,
                            y=len(druglist)-index,
                            text=f'{drug}',
                            showarrow=False,
                            yshift=10)
    # here you can modify the figure and the legend titles
    fig.update_layout(
                    title='Uso de medicamentos en pacientes',
                    showlegend=False,
                    xaxis=dict(title='Horas transcurridas en UCI'),
                    yaxis=dict(showticklabels=False) # that way you hide the y axis ticks labels
                    )
    return fig


cohorte = cohorte_tipo(patient,diagnosis,"cardiovascular")
figura = muestra_grafica_medicamentos(medication, cohorte, 60, 5, -2000, 15000)

figura.show()

#with pd.option_context('display.max_rows', None):
#    print(df[:600])