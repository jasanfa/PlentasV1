from codeScripts.methodologyPlentas import *
from codeScripts.rubrics import Ortografia2, Sintaxis2, GenerateFeedback
from codeScripts.settings import GetSettings
from codeScripts.utils import getIDrange, splitResponse


class Plentas():

    def __init__(self, config, studentsData):

        self.settings = GetSettings(config, studentsData)
        #semantica
        self.semantic_methodology = PlentasMethodology(self.settings)
        #ortografia
        self.ortografia = Ortografia2(self.settings)
        #sintaxis
        self.sintaxis = Sintaxis2(self.settings)
         

    def setApiSettings(self, api_settings):
        #lectura de parametros de la api
        self.settings.setApiSettings(api_settings)

    def processApiData(self):


        if self.settings.PesoOrtografia == 0.0:
            self.settings.Ortografia = 0
        if self.settings.PesoSintaxis == 0.0:
            self.settings.Sintaxis = 0
        if self.settings.PesoSemantics == 0.0:
            self.settings.Semantica = 0

        AnalysisOfResponses = []
        IDs = getIDrange(self.settings.rango_ID, self.settings.answersDF)
        for id in IDs:
            studentID = self.settings.answersDF['hashed_id'][id]
            self.settings.studentID = studentID

            nota_rubrica_spacy = 0
            nota_rubrica_bert = 0

            respuesta_alumno_raw = self.settings.answersDF['respuesta'][id].lower()
            
 

            if self.settings.Sintaxis:
                #ponderacion dentro de la función
                nota_rubrica_sintaxis = self.sintaxis.Evaluation(respuesta_alumno_raw)
                nota_rubrica_spacy = nota_rubrica_spacy + nota_rubrica_sintaxis
                nota_rubrica_bert = nota_rubrica_bert + nota_rubrica_sintaxis
            else:
                nota_rubrica_sintaxis = 0
                
            
            if self.settings.Ortografia:
                #ponderacion dentro de la función
                nota_rubrica_ortografia = self.ortografia.Evaluation(respuesta_alumno_raw)

                nota_rubrica_spacy = nota_rubrica_spacy + nota_rubrica_ortografia
                nota_rubrica_bert = nota_rubrica_bert + nota_rubrica_ortografia
            else:
                nota_rubrica_ortografia = 0                
            
        
            if self.settings.Semantica:
                sentencesArr = splitResponse(respuesta_alumno_raw)

                spacy_eval = self.semantic_methodology.getSimilarity(sentencesArr, "spacy")
                bert_eval = self.semantic_methodology.getSimilarity(sentencesArr, "bert")

                print("BERT EVAL")
                print(bert_eval)

                spacy_eval_umbral = self.semantic_methodology.EvaluationMethod(studentID, "" if len(sentencesArr) == 1 and sentencesArr[0] == '' else sentencesArr, spacy_eval, "spacy")

                bert_eval_umbral = self.semantic_methodology.EvaluationMethod(studentID, "" if len(sentencesArr) == 1 and sentencesArr[0] == '' else sentencesArr, bert_eval, "bert")

                nota_rubrica_spacy = nota_rubrica_spacy + self.settings.PesoSemantics * spacy_eval_umbral
                nota_rubrica_bert = nota_rubrica_bert + self.settings.PesoSemantics * bert_eval_umbral
            else:
                spacy_eval_umbral = 0
                bert_eval_umbral = 0

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
        

        self.semantic_methodology.SemanticLevel.output.saveSimilarityResults(self.settings, "spacy")
        self.semantic_methodology.SemanticLevel.output.saveSimilarityResults(self.settings, "bert")
        if self.settings.Sintaxis:
            self.sintaxis.saveResults()
        if self.settings.Ortografia:
            self.ortografia.SaveMistakes()
        return AnalysisOfResponses
    

        