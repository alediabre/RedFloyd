library(ggplot2)
library(ggthemes) # es un paquete que extiende a gpplot2
library(dplyr)
library(readr)
library(stringr)

read_csv("./eicu-collaborative-research-database-demo-2.0.1/patient.csv.gz") -> pacientes
read_csv("./eicu-collaborative-research-database-demo-2.0.1/treatment.csv.gz") -> tratamientos


t <- tratamientos %>% 
  group_by(treatmentstring) %>%
  summarise(n = n()) %>%
  mutate(Freq = n/sum(n),
         treatmenttype = str_extract(treatmentstring, ".*|")
         )


