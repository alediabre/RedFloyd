import pandas as pd
import re
import matplotlib.pyplot as plt
import squarify



diagnosis = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/diagnosis.csv.gz', compression='gzip')
patient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz', compression='gzip')
treatment = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/treatment.csv.gz', compression='gzip')



def normaliza_edad(p, normalize=None):
    def to_int(s,normalize=None):
        if s.__class__ == float: #si es un Nan
            return 0
        if (mo := re.match("^>(.*)", s)) != None: #Si es >89
            return int(90)
        else:
            n = int(s)
            if normalize!=None:
                return n - (n%normalize)
            else:
                return n

    p["age"] = p["age"].map(lambda s : to_int(s,normalize)) #Convierte la edad a int y en caso de normalize: las agrupa por años
    return p



def plot_by_age(p):
    patientgroups = p.drop_duplicates(subset=["uniquepid"]).groupby(["age"])

    ages = [name for name,_ in patientgroups]
    counts = [group.shape[0] for _,group in patientgroups]

    df = pd.DataFrame({'count': counts, 'ages':ages})
    
    squarify.plot(sizes=df['count'], label=df['ages'], alpha=.8)
    plt.axis('off')
    #plt.pie(df["count"], labels=df["ages"], colors=palette_color, autopct='%.0f%%')
    plt.show()


def __main__():
    patient = normaliza_edad(patient)
    plot_by_age(patient)