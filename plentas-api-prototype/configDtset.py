import pandas as pd
import json
import re
from hashids import Hashids

def isMetadataTier(tier):
    #devuelve true si el key contiene la palabra metadata
    vct_split = re.split("\.", tier)
    for indx in vct_split:
        if indx == "metadata":
            return True    
    return False

def createNewJsonFormat(df, data):
    hashids = Hashids(min_length=20)
    #Numero de variables disponibles
    len_df_cols = 0
    for col in df.columns:
        if df[col][0] == "id_examen":
            len_df_cols = 1
            break

    if len_df_cols:
        len_df_cols = len(df.columns) - 1 #la variable id_examen no interesa
    else:
        len_df_cols = len(df.columns)

    #Numero de variables de la plantilla a rellenar
    empty_rows = 0
    for key in data[0]:
        if not isMetadataTier(key):
            empty_rows+=1
    
    if len_df_cols == empty_rows: 
        dtset_out = dict()   
        for alumno, alumno_nmbr in zip(df[0], range(len(df[0]))):
            #La primera fila son los indices 
            if alumno_nmbr!= 0:
                dtset_out[alumno_nmbr] = dict()
                for key, key_nmbr in zip(data[0], range(len(data[0]))):
                    #si tiene la coletilla metadata copio la info tal cual
                    if isMetadataTier(key):
                        dtset_out[alumno_nmbr][key] = data[0][key]
                        decrmnt = 11
                    else:
                        #sino cojo la info del df cargado
                        if df[key_nmbr-decrmnt][0] == "id_examen":
                            #se reduce el decrmnt para saltar la columna id_examen
                            decrmnt = 10 

                        #se aplica el hash para anonimizar
                        if df[key_nmbr-decrmnt][0] == "nombre":                             
                            dtset_out[alumno_nmbr][key] = hashids.encode(alumno_nmbr)
                        else:                 
                            dtset_out[alumno_nmbr][key] = df[key_nmbr-decrmnt][alumno_nmbr]

        #Saving the json file
        #print(dtset_out) 
        dtste = []
        for i in dtset_out:
            dtste.append(dtset_out[i])

        """
        json_object = json.dumps(dtset_out, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("Ectel/Tecnología de computadores/plantillaCompleta.json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
        """
        json_object = json.dumps(dtste, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("Ectel/Tecnología de computadores/plantillaCompleta.json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)

        #eliminar manualmente los corchetes de inicio y final del documento

def createOldJsonFormat(df, data):
    #Para el articulo de ectel, crear el json con el mismo formato
    old_dtset_list=[]
    hashids = Hashids(min_length=20)
    old_dtset = dict()


    for alumno, alumno_nmbr in zip(df[0], range(len(df[0]))):
        if alumno_nmbr!= 0:
            old_dtset[alumno_nmbr] = dict()
            old_dtset[alumno_nmbr]["respuesta"] = ""
            old_dtset[alumno_nmbr]["metadata"] = dict()
            old_dtset[alumno_nmbr]["metadata"]["enunciado"] = ""
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"] = [	{
                                "minipregunta": "",
                                "minirespuesta": ""
                            },
                            {
                                "minipregunta": "",
                                "minirespuesta": ""
                            },
                            {
                                "minipregunta": "",
                                "minirespuesta": ""
                            }
                        ]
            old_dtset[alumno_nmbr]["metadata"]["keywords"]=[]
            old_dtset[alumno_nmbr]["hashed_id"] = ""
            old_dtset[alumno_nmbr]["nota"] = 0
            old_dtset[alumno_nmbr]["respuesta"] = df[2][alumno_nmbr]
            old_dtset[alumno_nmbr]["metadata"]["enunciado"] = data[0]["metadata.enunciado"]
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"][0]["minipregunta"] = data[0]["metadata.minipreguntas.1"]
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"][1]["minipregunta"] = data[0]["metadata.minipreguntas.2"]
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"][2]["minipregunta"] = data[0]["metadata.minipreguntas.3"]
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"][0]["minirespuesta"] = data[0]["metadata.minirespuestas.1"]
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"][1]["minirespuesta"] = data[0]["metadata.minirespuestas.2"]
            old_dtset[alumno_nmbr]["metadata"]["minipreguntas"][2]["minirespuesta"] = data[0]["metadata.minirespuestas.3"]
            for kw in re.split("\,",data[0]["metadata.keywords"]):
                old_dtset[alumno_nmbr]["metadata"]["keywords"].append(kw)

            old_dtset[alumno_nmbr]["hashed_id"] = hashids.encode(alumno_nmbr)
            old_dtset[alumno_nmbr]["nota"] = df[3][alumno_nmbr]


    for i in old_dtset:
        old_dtset_list.append(old_dtset[i])
    

    json_object = json.dumps(old_dtset_list, indent = 11, ensure_ascii= False) 
    # Writing output to a json file
    with open("Ectel/Tecnología de computadores/plantillaCompletaOld.json", "w", encoding="utf-8") as outfile:
        outfile.write(json_object)
    
    #eliminar los corchetes de forma manual

     


if __name__ == '__main__':    
    #datos de los estudiantes a complementar
    df = pd.read_csv('Ectel/Tecnología de computadores/TC-GII-dataset.csv', sep=';', header=None)
    #print(df)
    
    #plantilla del json a crear
    with open("Ectel/Tecnología de computadores/plantilla.json", "r", encoding="utf8") as f:
        data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")

    createNewJsonFormat(df, data)
    createOldJsonFormat(df, data)

    

    
                
        

