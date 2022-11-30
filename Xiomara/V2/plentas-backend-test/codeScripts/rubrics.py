from asyncio.windows_events import NULL
import os
from matplotlib.font_manager import json_load
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import copy
import json
import re

import spacy
#nlp = spacy.load('es_core_news_sm')
#nlp = spacy.load('es_core_news_md')
nlp = spacy.load('es_core_news_lg')

from OldApi.utils.Semantics.SentenceTransformer2 import *
from codeScripts.utils import create_file_path
from codeScripts.rubricsOut import SemanticOutput


from codeScripts.kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo, saveKWInfo, loadKWInfo
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from codeScripts.utils import spelling_corrector, clean_words, sent_tokenize, mu_index, FHuertas_index, check_senteces_words, keyword_extractor,getNameFile



class Semantica2():
    def __init__(self, settings):
        #print(f'Aqui las funciones de semantica')
        if settings.BusquedaKW:
            try:
                os.mkdir('__appcache__')
            
                Pobs, Ptrans, LemmaDictionary = loadHMMInfo()

                KWfile_info = NLP_Questions(settings.answersDF_json,{},{}, LemmaDictionary)
                IdentifiedKW = NLP_Answers(settings.answersDF_json,KWfile_info.Synonyms(), KWfile_info.Antonyms(), KWfile_info.LemmatizedKeywords(), LemmaDictionary, Ptrans, Pobs, KWfile_info.Windows())

                self.file_feedback = IdentifiedKW.showFeedback()
                self.file_marks = IdentifiedKW.showMarks()
                self.file_feedbackDistrib = IdentifiedKW.showFeedbackDistribution()
                self.file_marksDistrib = IdentifiedKW.showKeywordsDistribution()

                
                saveKWInfo(getNameFile(settings.json_file_in), self.file_feedback, self.file_marks,self.file_feedbackDistrib, self.file_marksDistrib)
                
            except:
                self.file_marks, self.file_feedback, self.file_marksDistrib, self.file_feedbackDistrib = loadKWInfo(getNameFile(settings.json_file_in))
        else:
            print(f'\n\n Omitiendo busqueda de KW ..... \n\n')

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

    def Keywords(self):
        return self.file_feedback, self.file_marks,self.file_feedbackDistrib, self.file_marksDistrib

    def KeywordExtractor(self, respuesta_alumno):

        if self.settings.Features.lower() == "none":
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.settings.NMaxKeywords), 'es', int(self.settings.TVentana), float(self.settings.Deduplication_threshold), None)
        else:
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.settings.NMaxKeywords), 'es', int(self.settings.TVentana), float(self.settings.Deduplication_threshold), self.settings.Features)


        return stdnt_kw


        


"""
class Ortografia ():
    def __init__(self):
        #print(f'Aqui lo de ortografia')
        self.output = OrtographicOutput()
    
    def Analysis(self,settings, respuesta_alumno):
        nota_Orto = 0
        if respuesta_alumno == '':
            self.output.notaOrtografia.append(0)
        else:
            errores, mistakes = spelling_corrector(respuesta_alumno, settings.hunspell_aff, settings.hunspell_dic)
            if errores <= settings.FaltasSalvaguarda:
                self.output.notaOrtografia.append(settings.PesoOrtografia)
            else:

                try:
                    rel = settings.PesoOrtografia/settings.NMaxErrores 
                    nota_Orto = settings.PesoOrtografia - (errores - settings.FaltasSalvaguarda) * rel
                except:
                    nota_Orto = 0

                if nota_Orto < 0:
                    nota_Orto = 0

                self.output.notaOrtografia.append(nota_Orto)


class Sintaxis ():
    def __init__(self):
        #print(f'Aqui lo de sintaxis')
        self.output = SintacticOutput()

    def Analysis(self, settings, respuesta_alumno):
        if respuesta_alumno == '':
            self.output.leg_FH.append(0)
            self.output.leg_mu.append(0)
        else:
            sentencesLenght, wordsLenght, syll, letter_per_word = check_senteces_words(respuesta_alumno)
            #print(wordsLenght)
            FH, legibilidad_fh = FHuertas_index(sentencesLenght, wordsLenght, syll)
            mu, legibilidad_mu = mu_index(sentencesLenght, wordsLenght, letter_per_word)

            self.output.leg_FH.append(FH)
            self.output.leg_mu.append(mu)

            nota_Sintaxis = settings.PesoSntxis_FH * FH/100 + settings.PesoSntxis_Mu * mu/100        
        



    def saveResults(self, settings):
        self.output.saveLegibilityResults(settings)

"""

"""
                                            settings.student_dict["Semantica"]["Keyword profesor"] = settings.prof_keywords 
                            settings.student_dict["Semantica"]["Keywords alumno"] = self.file_marks[studentID]     
                    settings.student_dict["Semantica"]["Keywords alumno"] = self.file_marks[studentID]
                    settings.student_dict["Semantica"]["Justificación de esos keywords"] = self.file_feedback[studentID]
                            self.settings.student_dict["Semantica"]["Keywords alumno (auto)"] = stdnt_kw

                                settings.student_dict["Sintaxis"]["Frases utilizadas para responder a la pregunta"] = sentencesLenght
            settings.student_dict["Sintaxis"]["Palabras utilizadas para responder a la pregunta"] = wordsLenght
            settings.student_dict["Sintaxis"]["Index Fernandez Huerta"] = FH
            settings.student_dict["Sintaxis"]["Legibilidad F-H"] = legibilidad_fh
            settings.student_dict["Sintaxis"]["mu index"] = mu
            settings.student_dict["Sintaxis"]["Legibilidad Mu"] = legibilidad_mu
            settings.student_dict["Sintaxis"]["Nota en Sintaxis"] = nota_Sintaxis

                        settings.student_dict["Ortografia"]["Errores ortograficos"] = [errores, mistakes]
        settings.student_dict["Ortografia"]["Nota en Ortografía"] = nota_Orto
"""
