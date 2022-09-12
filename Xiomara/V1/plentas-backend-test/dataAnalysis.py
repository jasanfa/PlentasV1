from cmath import nan
from distutils.log import set_threshold
from cv2 import threshold
import pandas as pd
from utils import clean_words
import re
import numpy as np
import pandas as pd
import json


def __getRevisorID(df, revisor =["Xiomara", "Javier"], machine_revisor = ["SM", "MD", "LG", "SM(similitud)", "MD(similitud)", "LG(similitud)","SM(umbral)", "MD(umbral)", "LG(umbral)"]):
    ids= dict()
    for col in df:
        #print(str(df[col][0]))
        if str(df[col][0]) in revisor or str(df[col][0]) in machine_revisor:
            ids[str(df[col][0])] = col

    return ids

    
def findLineswithFlag(df, flag = "NINGUNA", revisor =["Xiomara", "Javier"]):  
    flag_list = []
    test_revisors_flag = dict()
    indx=0
    revisors = __getRevisorID(df, revisor)

    names = []

    rest_list = []
    
    for person in revisor:
        #print(revisors[person])
        test_revisors_flag[person] = []
        names.append(person)
        for row in df[revisors[person]+2]:
            #print(row)
            if str(row).lower() == flag.lower():
                test_revisors_flag[person].append(indx)
            if str(row).lower() == flag.lower() and not indx in flag_list:
                #print(row, indx)
                flag_list.append(indx)
            else:
                rest_list.append(indx)
            indx+=1
        indx= 0

    
    if len(names) == 2:
        l1 = test_revisors_flag[names[0]]
        l2 = test_revisors_flag[names[1]]

        a= set(l1) & set(l2) 
        print(f"Coincidencias Ninguna {names[0]} y {names[1]}: {sorted(a)}.... {len(a)/len(flag_list)}")
     
    elif len(names) == 3:
        l1 = test_revisors_flag[names[0]]
        l2 = test_revisors_flag[names[1]]
        l3 = test_revisors_flag[names[2]]
        a= set(l1) & set(l2) 
        print(f"Coincidencias Ninguna {names[0]} y {names[1]}: {sorted(a)}.... {len(a)/len(flag_list)}")
        a= set(l1) & set(l3)
        print(f"Coincidencias Ninguna {names[0]} y {names[2]}: {sorted(a)}.... {len(a)/len(flag_list)}")
        a= set(l2) & set(l3)
        print(f"Coincidencias Ninguna {names[1]} y {names[2]}: {sorted(a)}.... {len(a)/len(flag_list)}")
        a= set(l1) & set(l2) & set(l3)
        print(f"Coincidencias Ninguna {names[0]}, {names[1]} y {names[2]}: {sorted(a)}.... {len(a)/len(flag_list)}")
    
    flag_list.sort()

    flag_list2 = getRowsfromID(df, flag_list)
    rest_list2 = getRowsfromID(df, rest_list)

    print(flag_list2.keys())

    #createCmpHistogram(flag_list[])

    df_Table = pd.DataFrame(flag_list2)
    df_Table.to_excel('OutputFiles/NingunaTable.xlsx', sheet_name='Ninguna')

    df_Table = pd.DataFrame(rest_list2)
    df_Table.to_excel('OutputFiles/RestTable.xlsx', sheet_name='Resto')
    
    return flag_list, revisors

def getRowsfromID(df, id_list):
    new_list = dict()
    indx = 0
    print(type(df))
    for col in df:
        new_list[col] = []
        for row in df[col]:
            #print(row)
            if indx in id_list:
                new_list[col].append(row)
            indx+=1
        indx=0
    return new_list

def createCmpHistogram(x1, x2, save_path):
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(15, 4))

    sns.distplot(a=x1, kde=True, ax=ax1)
    #sns.distplot(a=x2, ax=ax1)
    ax1.set_title('Histograma Flag')

    sns.distplot(a=x2, kde=True, ax=ax2)
    #sns.distplot(a=x2, ax=ax2)
    ax2.set_title('Histograma All except Flag')

    xmin = min(x1.min(), x2.min())
    xmax = max(x1.max(), x2.max())
    bins = np.linspace(xmin, xmax, 11)
    sns.distplot(a=x1, norm_hist=True, kde=True, ax=ax3)
    sns.distplot(a=x2, norm_hist=True, ax=ax3)
    ax3.set_title('Combinado')

    #plt.tight_layout()
    #plt.show()
    plt.savefig(save_path)

def getThreshold(df, flag_list, revisors_ids):
    save_flag_appernc = dict()
    flag_threshold= {"SM(similitud)": [], "MD(similitud)":[], "LG(similitud)":[]}

    models_simil = list(revisors_ids.keys())
    borrar = 0
    for flag_appeareance in flag_list:
        save_flag_appernc[flag_appeareance] = dict()        
        borrar+=1
        for revisor in revisors_ids.keys(): 
            #print(revisor)
            if revisor in models_simil[-6:-3]:
                #print(revisor)
                #print(df[revisors_ids[revisor]][flag_appeareance])
                
                if pd.isnull(df[revisors_ids[revisor]][flag_appeareance]):
                    continue
                else:
                    flag_threshold[revisor].append(float(re.split(' ', df[revisors_ids[revisor]][flag_appeareance])[0]))
         
            save_flag_appernc[flag_appeareance][revisor] = df[revisors_ids[revisor]][flag_appeareance]
            

    #print(flag_threshold)
    for i in flag_threshold.keys():
        #print(len(flag_threshold[i]))
        r = sum(flag_threshold[i])/len(flag_threshold[i])
        print(f"Media de similitud por respuesta del flag: {i}: {r}")

    return flag_threshold

        

        

        


def createTrueTable(df, revisors_ids):
    models_simil = list(revisors_ids.keys())
    #Do not consider similitud columns
    models_simil = models_simil[:-6] + models_simil[-3:]

    TrueFalseTable = dict()
    donequeue = []

    for revisor in models_simil:        
        for revisor2 in models_simil:
            if revisor != revisor2 and revisor2 not in donequeue:
                TrueFalseTable[revisor + " & " + revisor2] = []
                #print(df[revisors_ids[revisor][1:]])
                for result1, result2 in zip(df[revisors_ids[revisor]][2:],df[revisors_ids[revisor2]][2:]):
                    if pd.isnull(result1):
                        a = 0
                    else:
                        a = re.split(' |\,',result1)[0]
                    
                    if pd.isnull(result2):
                        b = 0
                    else:
                        b = re.split(' |\,',result2)[0]
                    
                   
                    if  a == b:
                        TrueFalseTable[revisor + " & " + revisor2].append("TRUE")
                    else:
                        TrueFalseTable[revisor + " & " + revisor2].append("FALSE")
                percentage = TrueFalseTable[revisor + " & " + revisor2].count("TRUE") / len(TrueFalseTable[revisor + " & " + revisor2])
                TrueFalseTable[revisor + " & " + revisor2].append(percentage)
        donequeue.append(revisor)
    

    df_Table = pd.DataFrame(TrueFalseTable)
    df_Table.to_excel('OutputFiles/TrueFalseTable.xlsx', sheet_name='TrueFalseTable')






if __name__ == '__main__':
    df = pd.read_csv('identificación-mejor-linea-met.csv', sep=';', header=None)
    #prueba, prueba2 = findLineswithFlag(df)
    prueba, prueba2 = findLineswithFlag(df, revisor =["Luis", "Elena", "Natalia"])
    print(prueba)
    print(prueba2)
    prueba3 =[]
    for i in range(len(df[0])):
        if i in prueba:
            continue
        else:
            if i !=0:
                prueba3.append(i)
    
    x1 = getThreshold(df, prueba, prueba2)
    x2 = getThreshold(df, prueba3, prueba2)

    print(x1)
    for i in x1.keys():
        createCmpHistogram(np.array(x1[i]), np.array(x2[i]), "OutputFiles/Hist"+ str(i))
    
    createTrueTable(df, prueba2)
"""
print(df)
for el in df:
    print(df[el])
    for row in df[el]:
        print(row)
    break
"""



