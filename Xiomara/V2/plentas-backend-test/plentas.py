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
from codeScripts.rubrics import Ortografia2, Sintaxis2, GenerateFeedback


class Plentas():

    def __init__(self, config, studentsData):
        self.spacy_sm = spacy.load('es_core_news_sm')
        self.settings = GetSettings(config, studentsData)
        #semantica
        self.semantic_methodology = PlentasMethodology(self.settings)
        #ortografia
        self.ortografia = Ortografia2(self.settings)
        #sintaxis
        self.sintaxis = Sintaxis2(self.settings)
         

    
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

    def processApiData(self, isRawExperiment = 0):
        self.settings.isRawExperiment = isRawExperiment
        AnalysisOfResponses = []
        IDs = getIDrange(self.settings.rango_ID, self.settings.answersDF)
        print(IDs)
        for id in IDs:
            studentID = self.settings.answersDF['hashed_id'][id]
            self.settings.student_dict["ID"] = studentID
            self.settings.studentID = studentID

            nota_rubrica_spacy = 0
            nota_rubrica_bert = 0

            respuesta_alumno_raw = self.settings.answersDF['respuesta'][id].lower()
            
            if isRawExperiment:
                try:
                    mark_to_float = re.sub(',', '.', self.settings.answersDF['nota'][id])
                except:
                    mark_to_float = self.settings.answersDF['nota'][id]
                self.settings.nota_prof = float(mark_to_float)            
                self.settings.notas.append(self.settings.nota_prof)
  

            if self.settings.Sintaxis:
                nota_rubrica_sintaxis = self.sintaxis.Evaluation(respuesta_alumno_raw) * self.settings.PesoSintaxis
                nota_rubrica_spacy = nota_rubrica_spacy + nota_rubrica_sintaxis
                nota_rubrica_bert = nota_rubrica_bert + nota_rubrica_sintaxis
            

            if self.settings.Ortografia:
                #ponderacion dentro de la función
                nota_rubrica_ortografia = self.ortografia.Evaluation(respuesta_alumno_raw)

                nota_rubrica_spacy = nota_rubrica_spacy + nota_rubrica_ortografia
                nota_rubrica_bert = nota_rubrica_bert + nota_rubrica_ortografia
                
            
        
            if self.settings.Semantica:
                sentencesArr = splitResponse(respuesta_alumno_raw)
                spacy_eval = self.semantic_methodology.getSimilarity(sentencesArr, "spacy")
                bert_eval = self.semantic_methodology.getSimilarity(sentencesArr, "bert")
                #bert_eval = [0,0,0,0]

                
                spacy_eval_umbral = self.semantic_methodology.EvaluationMethod(studentID, "" if len(sentencesArr) > 1 and sentencesArr[0] != '' else sentencesArr, spacy_eval)

                bert_eval_umbral = self.semantic_methodology.EvaluationMethod(studentID, "" if len(sentencesArr) > 1 and sentencesArr[0] != '' else sentencesArr, bert_eval)

                nota_rubrica_spacy = nota_rubrica_spacy + self.settings.PesoSemantics * spacy_eval_umbral
                nota_rubrica_bert = nota_rubrica_bert + self.settings.PesoSemantics * bert_eval_umbral

            
            feedback = GenerateFeedback(self.settings, respuesta_alumno_raw,nota_rubrica_ortografia, nota_rubrica_sintaxis, spacy_eval_umbral * self.settings.PesoSemantics, bert_eval_umbral * self.settings.PesoSemantics)
                

                

            AnalysisOfResponses.append({ id : {
                                                "ID": studentID,
                                                "NotaSpacy": round(nota_rubrica_spacy,2),
                                                "NotaBert": round(nota_rubrica_bert,2),
                                                "NotaSemanticaSpacy": round(spacy_eval_umbral * self.settings.PesoSemantics,2),
                                                "NotaSemanticaBert": round(bert_eval_umbral * self.settings.PesoSemantics,2),
                                                "NotaSintaxisSpacy": round(nota_rubrica_sintaxis,2),
                                                "NotaSintaxisBert": round(nota_rubrica_sintaxis,2),
                                                "NotaOrtografiaSpacy": round(nota_rubrica_ortografia,2),
                                                "NotaOrtografiaBert": round(nota_rubrica_ortografia,2),
                                                "Feedback": feedback }
                                    } )      
        

        print(len(AnalysisOfResponses))
        self.semantic_methodology.SemanticLevel.output.saveSimilarityResults(self.settings, "spacy")
        return AnalysisOfResponses
    

        