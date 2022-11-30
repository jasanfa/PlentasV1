from distutils import filelist
from distutils.filelist import FileList
import json
from datasets import load_dataset
from sklearn.model_selection import train_test_split
import pandas as pd
import os

from json import encoder

from utils import save_json, load_json

#variables que tengo que hacer parametrizables:
fileList = "utils/Semantics/Dataset_train_BERT.json"

path_dataset= "Jacobo/Metodos - analisis por minipregunta/"


#los parámetros de SentTransf_train

def getJsonInfo(fileName):
    #subject_fileDataset = {'train': load_json(fileName)}
    subject_dataset = {}
    samples = []
    subject_info = load_json(fileName)
    nmbr_minipreguntas = 0
    for id in subject_info[0].keys():
        for part_of_rubric in subject_info[0][id].keys():
            #print(subject_info[0][id])
            #break
            if part_of_rubric == "m" + str(nmbr_minipreguntas+1):
                nmbr_minipreguntas+=1
        break
    
    for id in subject_info[0].keys():
        hashed_id = id
        mark, responseStudent, responseTeacher = [],[],[]      
        for i in range(nmbr_minipreguntas):
            mark.append(subject_info[0][id]["m"+ str(i+1)+ "_score"])
            responseStudent.append(subject_info[0][id]["resp_m"+ str(i+1)])
            responseTeacher.append(subject_info[0][id]["m"+ str(i+1)])

        ie = {'responseTeacher': responseTeacher,
        'responseStudent': responseStudent,
        'mark': mark,
        'hashed_id': hashed_id
        }

        samples.append(ie)

    return samples
    
    print(nmbr_minipreguntas)
    """
        m = minipreguntas_list.index(minipregunta)

    for i in range (0,len(subject_fileDataset["train"])): #len(subject1)
        hashed_id = subject_fileDataset["train"][i]['hashed_id']
        #mark = subject_fileDataset["train"][i]['nota']
        responseStudent = subject_fileDataset["train"][i]['respuesta']
        
        responseTeacher = subject_fileDataset["train"][i]['metadata']['minipreguntas'][m]['minirespuesta']

        mark = 
        
        ie = {'responseTeacher': responseTeacher,
            'responseStudent': responseStudent,
            'mark': mark,
            'hashed_id': hashed_id
            }

        samples.append(ie)

    return samples
    """

a = getJsonInfo(fileList)
print(a)
