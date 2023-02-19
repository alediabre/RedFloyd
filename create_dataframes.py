import pandas as pd
import medication as med
from pathlib import Path  


def normal_medication():
    medication = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/medication.csv.gz', compression='gzip')
    medication = med.standard_drugnames(medication)
    filepath = Path('./dataframes/standard_medication.csv.gz')
    medication.to_csv(filepath, compression='gzip') 


def __main__():
    print("Almacenamiento de dataframes modificados")
    #normal_medication()



