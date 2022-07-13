import pandas as pd
import json
from utils import getIDrange
from tools import Ortografia, Sintaxis, Semantica, GetSettings
import copy
import re

#from SentenceTransformer2 import *
from SentenceTransformer_nminipregunta import *


class Plentas():

    def __init__(self, config):
        self.settings = GetSettings(config)
        self.sintactics = Sintaxis()
        self.ortography = Ortografia()
        self.semantics = Semantica(self.settings.BusquedaKW, self.settings)  

    
    def __evaluateStudents__(self):
        IDs = getIDrange(self.settings.rango_ID, self.settings.answersDF)
        for id in IDs:
            studentID = self.settings.answersDF['hashed_id'][id]
            self.settings.student_dict["ID"] = studentID

            respuesta_alumno_raw = self.settings.answersDF['respuesta'][id].lower()

            
            try:
                mark_to_float = re.sub(',', '.', self.settings.answersDF['nota'][id])
            except:
                mark_to_float = self.settings.answersDF['nota'][id]

            self.settings.nota_prof = float(mark_to_float)
            
            self.settings.student_dict["Semantica"]["Nota profesor"] = self.settings.nota_prof

            self.settings.notas.append(self.settings.nota_prof)

            #print(f'{studentID}, {respuesta_alumno_raw}')       

            if self.settings.Sintaxis:
                self.sintactics.Analysis(self.settings, respuesta_alumno_raw)                

            if self.settings.Ortografia:
                self.ortography.Analysis(self.settings, respuesta_alumno_raw)              

            if self.settings.Semantica:
                self.semantics.Analysis(self.settings,studentID, respuesta_alumno_raw)

            
        return copy.deepcopy(self.settings.student_dict)

                
        


    
    def processData(self):
        output_json=[]
        #manual_flag to configure
        analysis_bert = 1
        
        #bert_save_path = 'Jacobo/Prueba3'
        modelsToTest = ['distiluse-base-multilingual-cased-v1'
                ,'paraphrase-multilingual-MiniLM-L12-v2'
                ,'paraphrase-multilingual-mpnet-base-v2'
                ,'all-distilroberta-v1'
                ,'bert-base-multilingual-uncased'
                ,'dccuchile_bert-base-spanish-wwm-uncased'
              ]
        epochsToTest = [5,10,30,50,100]
        #epochsToTest = [1]
        self.settings.BertModels_glbl = SentTransf_test(modelsToTest, epochsToTest)
        
        if analysis_bert:
            for model_name in modelsToTest:
                for epoch in epochsToTest:
                    self.settings.model_path = "Jacobo/Prueba3/Prueba_anterior/Model_" + model_name + "/" + str(epoch) + "_Epochs"
                    self.settings.modelr = model_name
                    self.settings.epochr = epoch

                    output_json.append(self.__evaluateStudents__())
                    """
                    if self.settings.Sintaxis:
                        self.sintactics.saveResults(self.settings)                   
                    """
                    if self.settings.Semantica:
                        self.semantics.saveResults(self.settings)
                                        
        else:
            output_json.append(self.__evaluateStudents__())
            """
            if self.settings.Sintaxis:
                self.sintactics.saveResults(self.settings)                   
            
            """
            if self.settings.Semantica:
                self.semantics.saveResults(self.settings)
            

 
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        with open(self.settings.json_file_out, "w") as outfile:
            outfile.write(json_object)
        
        return json_object
        
        