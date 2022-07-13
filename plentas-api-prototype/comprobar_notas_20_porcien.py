import matplotlib.pyplot as plt
import seaborn as sb
import os 
import pandas
import re
import numpy as np

epoch_list = ["Score_1","Score_5","Score_10","Score_30","Score_50","Score_100"]

for file in os.listdir("Jacobo/Prueba3/Prueba_anterior/tests/Scores"):
    data = pandas.read_csv("Jacobo/Prueba3/Prueba_anterior/tests/Scores/"+file, delimiter=';', encoding="utf8",)
    hist_data = dict()
    hist_data[file] = dict()
    for epoch in epoch_list: 
        hist_data[file][epoch] = []
    rango = np.arange(0.1, 0.2, 0.02)
    print(rango)
    for epoch in epoch_list:
        for r in rango:         
            #intervalos = range(-10, 10)
            
            cnt_20_porcien = 0
            for m1, m2 in zip(data[epoch], data["Mark"]) :
                m1 = re.sub(',',  '.', m1) 
                m2 = re.sub(',',  '.', m2) 
                

                if abs(float(m1) - float(m2)) <= r:
                    cnt_20_porcien +=1

            hist_data[file][epoch].append(cnt_20_porcien)

        print(hist_data[file][epoch])
        plt.figure(figsize=(10,7))
        plt.plot(rango, hist_data[file][epoch], label = "Respuestas")

        plt.xlabel("Rango")
        plt.ylabel("Respuestas")
        plt.legend(loc=1)
        plt.title("Numero de respuestas por cada rango de error")
        #plt.show()
        plt.savefig("C:/Users/javier.sanz/OneDrive - UNIR/Desktop/PLENTAS_UNIR/TECNICO/APLICACION/App WEB/PLENTAS/plentas-api-prototype/Jacobo/Prueba3/Prueba_anterior/tests/Respuestas en rango/" + str(file) + str(epoch) + ".png")

        print(file + epoch + " -- " + str(cnt_20_porcien) + "/" + str(len(data[epoch]))+ "/n")


    


       


