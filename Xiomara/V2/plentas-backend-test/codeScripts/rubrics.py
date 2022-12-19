import os
import spacy
#nlp = spacy.load('es_core_news_sm')
#nlp = spacy.load('es_core_news_md')
#nlp = spacy.load('es_core_news_lg')

from OldApi.utils.Semantics.SentenceTransformer2 import *
from codeScripts.rubricsOut import SemanticOutput, OrtographicOutput, SintacticOutput
from codeScripts.kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo, saveKWInfo, loadKWInfo
from codeScripts.utils import spelling_corrector, mu_index, FHuertas_index, check_senteces_words, save_json,create_file_path, keyword_extractor,getNameFile


class Semantica2():
    """
    This class allows to compute the semantic level of the rubric
    """
    def __init__(self, settings):        

        self.output = SemanticOutput(settings)
        self.spacy_model = spacy.load('es_core_news_sm')
        self.settings = settings
    
    def computeSimilarity(self,sentences1,sentences2,similarityMethod):
        """
        This function applies a defined method to obtain the similarity between two sentences
        Inputs:
            -sentences1: First set of sentences to compare
            -sentences2: Second set of sentences to compare
            -similarityMethod: The inherited similarity method selected in getSimilarity
        Outputs:
            -similar: The similarity score
        """
        if similarityMethod.lower() == "spacy":
            r1 = self.spacy_model(sentences1)
            r2 = self.spacy_model(sentences2)
            similar = round(r1.similarity(r2), 3)
        else:
            similar = self.settings.BertModels_glbl.similarity(self.settings.model_path, sentences1, sentences2)[0][0].item()
        
        return similar

    
    #funciones para la extraccion/generacion de kw
    """
    def Keywords(self):
        return self.file_feedback, self.file_marks,self.file_feedbackDistrib, self.file_marksDistrib

    def KeywordExtractor(self, respuesta_alumno):

        if self.settings.Features.lower() == "none":
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.settings.NMaxKeywords), 'es', int(self.settings.TVentana), float(self.settings.Deduplication_threshold), None)
        else:
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.settings.NMaxKeywords), 'es', int(self.settings.TVentana), float(self.settings.Deduplication_threshold), self.settings.Features)


        return stdnt_kw
    """

class Ortografia2 ():
    """
    This class allows to compute the ortographic level of the rubric
    """
    def __init__(self, settings):
        self.output = OrtographicOutput()
        self.settings = settings
    
    def Evaluation(self, respuesta_alumno):
        exceptions = ["excel", "jupyter", "notebook", "html", "pdf", "zip", "url", "google", "colab", "https", "com", "drive", "viterbi", "gmail", "cc", "morfosint�ctico", "ipynb", "txt" "python", "microsoft", "xlsx"]

        nota_Orto = 0
        if respuesta_alumno == "":
            self.output.number_mistakes.append(0)
        else:
            errores, mistakes = spelling_corrector(respuesta_alumno, self.settings.hunspell_aff, self.settings.hunspell_dic)
            for mistake in mistakes:
                if mistake not in exceptions:
                    if mistake not in self.output.mistakes:
                        self.output.mistakes.append(mistake)
                else:
                    errores-=1
                    
            self.output.number_mistakes.append(errores)
            if errores <= self.settings.FaltasSalvaguarda:
                nota_Orto = self.settings.PesoOrtografia
            else:

                try:
                    rel = self.settings.PesoOrtografia/self.settings.NMaxErrores 
                    nota_Orto = self.settings.PesoOrtografia - (errores - self.settings.FaltasSalvaguarda) * rel
                except:
                    nota_Orto = 0

                if nota_Orto < 0:
                    nota_Orto = 0

        return nota_Orto

    def SaveMistakes(self):
        save_json(create_file_path('RecopiledMistakes.json', doctype= 2),self.output.mistakes, False)
        save_json(create_file_path('NumberMistakes.json', doctype= 2),self.output.number_mistakes, False)

class Sintaxis2():
    def __init__(self, settings):
        self.output = SintacticOutput()
        self.settings = settings

    def Evaluation(self, respuesta_alumno):
        if respuesta_alumno == '':
            self.output.leg_FH.append(0)
            self.output.leg_mu.append(0)
            return 0
        else:
            sentencesLenght, wordsLenght, syll, letter_per_word = check_senteces_words(respuesta_alumno)
            FH, _ = FHuertas_index(sentencesLenght, wordsLenght, syll)
            mu, _ = mu_index(sentencesLenght, wordsLenght, letter_per_word)

            self.output.leg_FH.append(FH)
            self.output.leg_mu.append(mu)
            
            nota_Sintaxis = (self.settings.PesoSintaxis/2) * FH/80 + (self.settings.PesoSintaxis/2) * mu/60
            if nota_Sintaxis > self.settings.PesoSintaxis:
                nota_Sintaxis = self.settings.PesoSintaxis

            return nota_Sintaxis       
        



    def saveResults(self):
        self.output.saveLegibilityResults()

def GenerateFeedback(settings, respuesta, OrtoMark, SintMark, SemanMarkSpacy, SemanMarkBert):
    print("Niveles2:", settings.Semantica,settings.Sintaxis, settings.Ortografia )
    feedback = ""
    if respuesta == "":
        feedback = feedback + "Respuesta en blanco"
    else:
        if settings.Ortografia:
            feedback = feedback + "\nNivel ortográfico: \n"
            if OrtoMark == 0:
                feedback = feedback + "El estudiante cometió demasiadas faltas de ortografía, por ese motivo, la nota asignada en este apartado de la rúbrica fue 0. \n"
            elif OrtoMark < settings.PesoOrtografia/2:
                feedback = feedback + "El estudiante cometió muchas faltas de ortografía, lo cual le penalizó en la nota. \n"
            elif OrtoMark < settings.PesoOrtografia:
                feedback = feedback + "El estudiante cometió  bastantes faltas de ortografía, lo cual no le permitió obtener la máxima puntuación en este apartado de la rúbrica. \n"
            else:
                feedback = feedback + "El estudiante redactó con buena ortografía su respuesta. \n"

        if settings.Sintaxis:
            feedback = feedback + "\nNivel sintáctico: \n"
            if SintMark == 0:
                feedback = feedback + "La cohesión de ideas del alumno era muy pobre. \n"
            elif SintMark < settings.PesoSintaxis/2:
                feedback = feedback + "El estudiante debería mejorar la forma en la que expresa sus conocimientos \n"
            elif SintMark < settings.PesoSintaxis:
                feedback = feedback + "La forma de expresar las ideas fue buena, pero podría ser mejorable \n"
            else:
                feedback = feedback + "La cohesión de ideas del estudiante fue buena \n"

        if settings.Semantica:
            feedback = feedback + "\nNivel semántico, primer modelo: \n"
            if SemanMarkSpacy == 0:
                feedback = feedback + "El estudiante no responde a ninguna de las minipreguntas \n"
            elif SemanMarkSpacy < settings.PesoSemantics/2:
                feedback = feedback + "El estudiante cita algunos conceptos requeridos, pero el nivel demostrado en general no es suficiente para aprobar \n"
            elif SemanMarkSpacy < settings.PesoSemantics:
                feedback = feedback + "El estudiante debería matizar algunos conceptos de mejor manera para mejorar su calificación, pero el nivel de conocimiento demostrado es suficiente \n"
            else:
                feedback = feedback + "El estudiante contestó de forma sobresaliente \n"

            feedback = feedback + "\nNivel semántico, segundo modelo: \n"
            if SemanMarkBert == 0:
                feedback = feedback + "El estudiante no responde a ninguna de las minipreguntas \n"
            elif SemanMarkBert < settings.PesoSemantics/2:
                feedback = feedback + "El estudiante cita algunos conceptos requeridos, pero el nivel demostrado en general no es suficiente para aprobar \n"
            elif SemanMarkBert < settings.PesoSemantics:
                feedback = feedback + "El estudiante debería matizar algunos conceptos de mejor manera para mejorar su calificación, pero el nivel de conocimiento demostrado es suficiente \n"
            else:
                feedback = feedback + "El estudiante contestó de forma sobresaliente \n"

            feedback = feedback + "\n\nPor favor, si observa alguna diferencia significativa entre la calificación de ambos modelos, entre a valorar la nota del estudiante. "



    return feedback
