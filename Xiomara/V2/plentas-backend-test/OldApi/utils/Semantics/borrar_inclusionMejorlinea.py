from cmath import nan
import pandas as pd
import json
import numpy as np
import re

from nltk import sent_tokenize

def addMiniresponse(student_dict, hashed_id, valuep, values):        
    sentences=[]                        
    TokenizeAnswer = sent_tokenize(student_dict[hashed_id]["respuesta_completa"])
    for token in TokenizeAnswer:
        regex = '\\.'
        token = re.sub(regex , '', token)
        sentences.append(token)
    sentences_to_append = []
    minipreguntas_list_index = ["resp_m1","resp_m2","resp_m3","resp_m4"]
    for minirespuesta in minipreguntas_list_index:
        if student_dict[hashed_id][minirespuesta] == "":

            if valuep == "" and values == "":
                student_dict[hashed_id][minirespuesta] = ""
            
            else:
            
                sentences_to_append.append(valuep)

                a = re.split("\,|\.", values)
                for e in a:
                    #if not np.isnan(e):
                    print(e)
                    if not e == "nan":
                        sentences_to_append.append(e)

                sentences_to_append.sort()
                #sentences_to_append = list(set(sentences_to_append))
                print(sentences_to_append)
                print(id)

                for i in sentences_to_append:
                    student_dict[hashed_id][minirespuesta] = student_dict[hashed_id][minirespuesta] + sentences[int(i)-1] + ". "
            
            break


with open("utils/Semantics/Metodos_Filtrado_ScoreporMinipregunta.json", "r", encoding="utf8") as f:
    data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")

df = pd.read_excel(open('Jacobo/Metodos - analisis por minipregunta/identificación-mejor-linea.xlsx', 'rb'))
 

student_dict = dict()

for student in data[0][0].keys():
    student_dict[data[0][0][student]["hashed_id"]] = dict()

    student_dict[data[0][0][student]["hashed_id"]]["respuesta_completa"] = data[0][0][student]["respuesta_completa"]

    print(data[0][0][student]["respuesta_completa"])
   

    student_dict[data[0][0][student]["hashed_id"]]["m1_score"] = data[0][0][student]["m1_score"]
    student_dict[data[0][0][student]["hashed_id"]]["m2_score"] = data[0][0][student]["m2_score"]
    student_dict[data[0][0][student]["hashed_id"]]["m3_score"] = data[0][0][student]["m3_score"]
    student_dict[data[0][0][student]["hashed_id"]]["m4_score"] = data[0][0][student]["m4_score"]

    student_dict[data[0][0][student]["hashed_id"]]["resp_m1"] = data[0][0][student]["resp_m1"]
    student_dict[data[0][0][student]["hashed_id"]]["resp_m2"]= data[0][0][student]["resp_m2"]
    student_dict[data[0][0][student]["hashed_id"]]["resp_m3"] = data[0][0][student]["resp_m3"]
    student_dict[data[0][0][student]["hashed_id"]]["resp_m4"] = data[0][0][student]["resp_m4"]



for student in data[0][0].keys():
    #print(data[0][0][student]["hashed_id"])
    for id, luisp, luiss, elenap, elenas, nataliap, natalias in zip(df["Unnamed: 0"], df["Luis"], df["Unnamed: 3"], df["Elena"], df["Unnamed: 6"], df["Natalia"], df["Unnamed: 9"] ) :
        if id == data[0][0][student]["hashed_id"]:
            if not np.isnan(luisp):                
                if luisp == 0:
                    #print(print(id, luisp))
                    addMiniresponse(student_dict, id, "", "")
                else:
                    addMiniresponse(student_dict, id, str(luisp), str(luiss))
                    #print(str(luisp) + str(luiss))

            elif not np.isnan(elenap):
                if elenap == 0:
                    #print(id, elenap)
                    addMiniresponse(student_dict, id, "", "")
                else:
                    addMiniresponse(student_dict, id, str(elenap), str(elenas))

            elif not np.isnan(nataliap):
                if nataliap == 0:
                    #print(id,nataliap)
                    addMiniresponse(student_dict, id, "", "")
                else:
                    addMiniresponse(student_dict, id, str(nataliap), str(natalias))



json_object = json.dumps(student_dict, indent = 11, ensure_ascii=False) 
    # Writing output to a json file
with open("Metodos_Filtrado_ScoreporMinipregunta_Completo.json", "w", encoding="utf-8") as outfile:
    outfile.write(json_object)