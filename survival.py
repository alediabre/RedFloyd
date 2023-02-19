import numpy as np
import pandas as pd
import math
import seaborn as sns
import matplotlib.pyplot as plt
import edades


apachepatient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/apachePatientResult.csv.gz', compression='gzip')
apachepredvar = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/apachePredVar.csv.gz', compression='gzip')
patient = pd.read_csv('./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz', compression='gzip')
medication = pd.read_csv('./dataframes/standard_medication.csv.gz', compression='gzip')


patient = edades.normaliza_edad(patient)
patient["imc"] = patient.apply(lambda row: row.admissionweight / math.pow(row.admissionheight/100,2), axis=1)
patient = patient[patient["admissionheight"]>80]

df = patient.merge(apachepatient,on='patientunitstayid').merge(apachepredvar,on="patientunitstayid")
df = df[df["apacheversion"]=="IV"]
df = df[df["predictedicumortality"]!=-1]

##########################################################################

'''
med_per_unitstay = medication.merge(df, on='patientunitstayid')
dict_med_unit = {}
for n,m in med_per_unitstay.groupby('patientunitstayid'):
    values = set(m['standarddrugname'].values.tolist())
    dict_med_unit[n]=values
    


#df = df.loc[:,["uniquepid","age_x","patientunitstayid","predictedicumortality","actualicumortality","unitdischargeoffset","visitnumber"]].sort_values(by=["uniquepid"])


sns.set(style="darkgrid")
 
# Grouped violinplot
sns.violinplot(x="age_x", y="imc", hue="diabetes", data=df, palette="Pastel1")
#sns.violinplot(x="diabetes", y="actualicumortality", data=df, palette="Pastel1")

plt.show()

#sns.boxplot( x=df["imc"], y=df["actualicumortality"] )
#plt.show()

#with pd.option_context('display.max_rows', None):
#    print(df[:600])
'''

'''
df['predictedicumortality']=df['predictedicumortality'].apply(lambda x : 100*x)

def media_params(visitnumber,param):
    return df.loc[df['visitnumber'] == visitnumber, param].mean()

visitnumber_values = [1,2,3]
parametros = ['age_x','imc','predictedicumortality']

data_dict = {'group':visitnumber_values}
data_dict.update({param:[media_params(d,param) for d in visitnumber_values] for param in parametros})

df = pd.DataFrame(data_dict)
 
# ------- PART 1: Create background
 
# number of variable
categories=list(df)[1:]
N = len(categories)
 
# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
angles = [n / float(N) * 2 * math.pi for n in range(N)]
angles += angles[:1]
 
# Initialise the spider plot
ax = plt.subplot(111, polar=True)
 
# If you want the first axis to be on top:
ax.set_theta_offset(math.pi / 2)
ax.set_theta_direction(-1)
 
# Draw one axe per variable + add labels
plt.xticks(angles[:-1], categories)
 
# Draw ylabels
ax.set_rlabel_position(0)
#plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
#plt.ylim(0,40)
 

# ------- PART 2: Add plots
 
# Plot each individual = each line of the data
# I don't make a loop, because plotting more than 3 groups makes the chart unreadable
 
# Ind1
values=df.loc[0].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="1")
ax.fill(angles, values, 'b', alpha=0.1)
 
# Ind2
values=df.loc[1].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="2")
ax.fill(angles, values, 'r', alpha=0.1)

# Ind3
values=df.loc[2].drop('group').values.flatten().tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label="3")
ax.fill(angles, values, 'g', alpha=0.1)
 
# Add legend
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

# Show the graph
plt.show()
'''