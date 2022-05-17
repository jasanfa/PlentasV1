import matplotlib.pyplot as plot
import seaborn as sb
import os 
import pandas
import re

epoch_list = ["Score_1","Score_5","Score_10","Score_30","Score_50","Score_100"]

for file in os.listdir("Jacobo/Prueba3/tests/Scores"):
    data = pandas.read_csv("Jacobo/Prueba3/tests/Scores/"+file, delimiter=';', encoding="utf8",)
    hist_data = []
    for epoch in epoch_list: 
        #intervalos = range(-10, 10)
        for m1, m2 in zip(data[epoch], data["Mark"]) :
            m1 = re.sub(',',  '.', m1) 
            m2 = re.sub(',',  '.', m2) 
            hist_data.append(float(m1) - float(m2))
        
        sb.displot(hist_data, color='#F2AB6D', kde=True) #creamos el gráfico en Seaborn

        #configuramos en Matplotlib
        #plot.xticks(intervalos)
        plot.ylabel('Frecuencia')
        plot.xlabel('Error')
        plot.title('Histograma de error '+ file + " " + epoch)
        #plot.show()
        plot.savefig('Jacobo/Prueba3/tests/Histograms/Histograma de error '+ file + " " + epoch + ".png")
        

       


