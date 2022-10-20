import pandas as pd
import json
from codeScripts.utils import getIDrange, splitResponse
#from codeScripts.tools import Ortografia, Sintaxis, Semantica, GetSettings
from codeScripts.tools import GetSettings
import copy
import re
import spacy

#from SentenceTransformer2 import *
#from SentenceTransformer_nminipregunta import *

from codeScripts.methodologyPlentas import *


class Plentas():

    def __init__(self, config, studentsData):
        self.spacy_sm = spacy.load('es_core_news_sm')
        self.settings = GetSettings(config, studentsData)
        self.methodology = PlentasMethodology(self.settings) 

    
    def __evaluateStudents__(self):
        self.sintactics = Sintaxis()
        self.ortography = Ortografia()
        self.semantics = Semantica(self.settings.BusquedaKW, self.settings)

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

                
        


    
    def evaluateData(self):
        output_json=[]
        #manual_flag to configure
        analysis_bert = 1
        
        #bert_save_path = 'Jacobo/Prueba3'
        modelsToTest = ['distiluse-base-multilingual-cased-v1']
        #'distiluse-base-multilingual-cased-v1'
        """
        modelsToTest = ['paraphrase-multilingual-MiniLM-L12-v2'
                ,'paraphrase-multilingual-mpnet-base-v2'
                ,'all-distilroberta-v1'
                ,'bert-base-multilingual-uncased'
                ,'dccuchile_bert-base-spanish-wwm-uncased'
              ]
        """
        epochsToTest = [50,100]
        #epochsToTest = [1]
        
        #self.settings.BertModels_glbl = SentTransf_test(modelsToTest, epochsToTest)
        
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
                        self.settings.notas = []

                                        
        else:
            output_json.append(self.__evaluateStudents__())
            """
            if self.settings.Sintaxis:
                self.sintactics.saveResults(self.settings)                   
            
            """
            if self.settings.Semantica:
                self.semantics.saveResults(self.settings)
                self.settings.notas = []


 
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        with open(self.settings.json_file_out, "w") as outfile:
            outfile.write(json_object)
        
        return json_object

    def setApiSettings(self, api_settings):
        #lectura de parametros de la api
        self.settings.setApiSettings(api_settings)

    def processApiData(self):
        AnalysisOfResponses = []
        IDs = getIDrange(self.settings.rango_ID, self.settings.answersDF)
        print(IDs)
        for id in IDs:
            studentID = self.settings.answersDF['hashed_id'][id]
            self.settings.student_dict["ID"] = studentID

            respuesta_alumno_raw = self.settings.answersDF['respuesta'][id].lower()
  

            #if self.settings.Sintaxis:
                #necesito nutrirle la respuesta
                #self.ortography.Analysis(self.settings, respuesta_alumno_raw)
            

            #if self.settings.Ortografia:
                #self.ortography.Analysis(self.settings, respuesta_alumno_raw)              

            if self.settings.Semantica:
                sentencesArr = splitResponse(respuesta_alumno_raw)
                spacy_eval = self.methodology.getSimilarity(sentencesArr, "spacy")
                #bert_eval = self.methodology.getSimilarity(sentencesArr, "bert")
                bert_eval = [0,0,0,0]

            AnalysisOfResponses.append({ id : {
                                                "ID": studentID,
                                                "NotaSpacy": spacy_eval[0],
                                                "NotaBert": bert_eval[0],
                                                "Feedback": "Hola1" }
                                    } )      
        

        print(len(AnalysisOfResponses))
        return AnalysisOfResponses
    

        