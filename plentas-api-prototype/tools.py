import os
#import matplotlib as plt
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt


def plotExperimento(notas, y, save_file = "Img_MSERealvsCalculatedMarks.png", labelx = "Student ID", labely = "MSE", title = "MSE Real vs Calculated Marks"):
    try:
        os.mkdir('__ImagenesExperimento2')
    except:
        pass

    x = []
    for i in range(len(notas)):
        x.append(i)

    plt.figure(figsize=(15,7))
    plt.plot(x, notas, label = "Calculated Marks", color = (0.1,0.1,0.1))
    if len(y) >1:
        plt.plot(x, y, '--',label = "Real marks", color = (0.5,0.5,0.5))

    plt.xlabel(labelx)
    plt.ylabel(labely)
    plt.legend(loc=1)
    plt.title(title)
    plt.xticks(rotation=-45)
    plt.grid()
    plt.savefig("__ImagenesExperimento2/"+save_file)
    plt.cla()


"""
def plotExperimento(notas, y, save_file = "Img_MSERealvsCalculatedMarks.png", labelx = "Student ID", labely = "MSE", title = "MSE Real vs Calculated Marks"):
    try:
        os.mkdir('__ImagenesExperimento')
        x = []
        for i in range(len(notas)):
            x.append(i)

        plt.figure(figsize=(15,7))
        plt.plot(x, y, color = (0.1,0.1,0.1))
        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.legend(loc=1)
        plt.title(title)
        plt.xticks(rotation=-45)
        plt.grid()
        plt.savefig("__ImagenesExperimento/"+save_file)
    except:
        x = []
        for i in range(len(notas)):
            x.append(i)

        plt.figure(figsize=(15,7))
        plt.plot(x, y, color = (0.1,0.1,0.1))
        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.legend(loc=1)
        plt.title(title)
        plt.xticks(rotation=-45)
        plt.grid()
        plt.savefig("__ImagenesExperimento/"+save_file)
"""
def plotExperimento2(save_file, df):

    try:
        os.mkdir('__ImagenesExperimento')
    except:
        pass

    real_marks_category = list(set(df["Nota Real"]))
    real_marks_category.sort()

    for col_name in df.columns:
        cmpMarks_list=[]
        
        for j in real_marks_category:
            if round(float(j),3) >= 0:
                for i in range(len(df[col_name])):  
                    if round(float(df["Nota Real"][i]),3) == round(float(j),3):
                        cmpMarks_list.append([df[col_name][i],df["Nota Real"][i]])

        cmpMarks_list = np.array(cmpMarks_list)
        print(f'{cmpMarks_list}\n\n')
        print(f'aa{cmpMarks_list[:, 0].astype(np.float32)}')
        plt.scatter(cmpMarks_list[:, 1].astype(np.float32), cmpMarks_list[:, 0].astype(np.float32), edgecolors=(0, 0, 0), alpha = 0.4)
        plt.plot([0.0, 1.0], [0.0, 1.0],
        'k--', color = 'black', lw=2)
        plt.title('Valor predicho vs valor real' + str(col_name), fontsize = 10, fontweight = "bold")
        plt.xlabel("Real")
        plt.ylabel("Predicción")
        plt.savefig("__ImagenesExperimento/"+ str(col_name)+save_file)
        plt.cla()
        #plt.show()
        del cmpMarks_list

def plotExperimento3(save_file, x):
    try:
        os.mkdir('__ImagenesExperimento3')
    except:
        pass

    ax= sns.histplot(
            data    = x,
            stat    = "count",
            kde     = True,
            color = "black"
        )
    ax.set(xlabel='Deviation', ylabel='Count')

    figure = ax.get_figure()    
    figure.savefig("__ImagenesExperimento3/"+save_file)
    del figure
    ax.cla()
