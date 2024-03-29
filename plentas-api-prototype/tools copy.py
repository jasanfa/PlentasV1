import os
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

import sys
sys.path.append("utils/Semantics/")

from SentenceTransformer2 import *


from kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo, saveKWInfo, loadKWInfo
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from utils import spelling_corrector, clean_words, sent_tokenize, mu_index, FHuertas_index, check_senteces_words, keyword_extractor,getNameFile, returnValue

class GetSettings():
    def __init__(self, settings_file):

        #lectura del fichero de configuracion
        self.__getConfigSettings(settings_file)
        #lectura del fichero de preguntas/respuestas
        self.__getData(self.json_file_in)


    def __getConfigSettings(self, df):        

        self.configDf = df

        self.json_file_in = df["ruta_fichero_entrada"]
        self.json_file_out = df["ruta_fichero_salida"]
        self.hunspell_aff = df["ruta_hunspell"]["aff"]
        self.hunspell_dic = df["ruta_hunspell"]["dic"]

        if df["Parametros_Analisis"]["estudiantes"]["Todos"]:
            self.rango_ID = "All"
        else:
            self.rango_ID = df["Parametros_Analisis"]["estudiantes"]["ID_rango"]

        
        self.Ortografia = df["Parametros_Analisis"]["Ortografia"]["Activado"]
        self.NMaxErrores = df["Parametros_Rubrica"]["Ortografia"]["NMaxErrores"]

        self.Sintaxis = df["Parametros_Analisis"]["Sintaxis"]["Activado"]
        self.NMaxFrases = df["Parametros_Rubrica"]["Sintaxis"]["NMaxFrases"]
        self.NMaxPalabras= df["Parametros_Rubrica"]["Sintaxis"]["NMaxPalabras"]
        self.MinFH= df["Parametros_Rubrica"]["Sintaxis"]["FH"]["MinFH"]
        self.MinLegibilidadFH= df["Parametros_Rubrica"]["Sintaxis"]["FH"]["MinLegibilidadFH"]
        self.MinMu= df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["MinMu"]
        self.MinLegibilidadMu= df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["MinLegibilidadMu"]
    
        self.Semantica = df["Parametros_Analisis"]["Semantica"]["Activado"]

        if int(df["Parametros_Analisis"]["Semantica"]["frases"]["Todos"]) == 1:
            self.grpSntncsMde = 0
        elif int(df["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"])>0:
            self.grpSntncsMde = 1
        else:
            self.grpSntncsMde = 2

        #print(f'+++++++++ Estoy poniendo grpSntncsMde con valor de {self.grpSntncsMde} +++++++++')

        self.NMaxKeywords= df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["NMaxKeywords"]
        self.TVentana= df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["TVentana"]
        self.Deduplication_threshold = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["Deduplication_threshold"]
        self.Features = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["Features"]
        self.BusquedaKW = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Busqueda"]["Activado"]

        self.MinSpacySimilar= df["Parametros_Rubrica"]["Semantica"]["Similitud"]["MinSpacySimilar"]

        self.FaltasSalvaguarda= df["Parametros_Rubrica"]["Ortografia"]["FaltasSalvaguarda"]

        self.PesoOrtografia = df["Parametros_Rubrica"]["Ortografia"]["Peso"]

        self.PesoSntxis_FH = df["Parametros_Rubrica"]["Sintaxis"]["FH"]["Peso"]
        self.PesoSntxis_Mu = df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["Peso"]

        self.PesoSmntca_KW = df["Parametros_Rubrica"]["Semantica"]["Keywords"]["Peso"]
        self.PesoSmntca_Similitud = df["Parametros_Rubrica"]["Semantica"]["Similitud"]["Peso"]

        self.kwExtractor = 1
        self.similarity_type = 0
        self.notas = []
        self.nota_prof = 0
        self.student_dict = { 'ID': None,
                'Ortografia': {              
                        'Errores ortograficos': None, 'Nota en Ortografía': None},
                'Sintaxis': {
                    'Frases utilizadas para responder a la pregunta': None,
                    'Palabras utilizadas para responder a la pregunta': None,
                    'Index Fernandez Huerta': None, 'Legibilidad F-H': None,
                    'mu index': None, 'Legibilidad Mu': None,'Nota en Sintaxis': None},
                'Semantica':{
                    'Keywords alumno (auto)': None,'Keywords alumno': None, 'Keyword profesor': None, 'Justificación de esos keywords': None, 'Nota en Semantica': None, 'Nota profesor': None}}
        #self.LofRespThreshold = 0.615
        self.LofRespThreshold = 0.875
               
        

    def __getData(self, json_file):

        #json_file = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/biConNotaAnon.json' 
        with open(json_file, "r", encoding="utf8") as f:
            data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")
    
        self.answersDF = pd.DataFrame(data)
        self.answersDF_json = copy.deepcopy(data)

        self.id_number = 0
        
        self.minipreguntas = []
        self.minirespuestas = []
        self.indice_minipreguntas = []
        self.respuesta_prof = ""

        self.enunciado = self.answersDF['metadata'][0]['enunciado']
        self.prof_keywords = self.answersDF['metadata'][0]['keywords']

        
        try:
            i=0
            while True:
            #for i in range(4):
                self.minirespuestas.append(self.answersDF['metadata'][0]['minipreguntas'][i]['minirespuesta'])
                self.minipreguntas.append(self.answersDF['metadata'][0]['minipreguntas'][i]['minipregunta'])

                self.indice_minipreguntas.append("minipregunta" + str(i))              

                if i == 0:        
                    self.respuesta_prof = self.respuesta_prof + self.minirespuestas[i] 
                else:
                    self.respuesta_prof = self.respuesta_prof + ' ' + self.minirespuestas[i] 
                
                i+=1
        except:
            self.indice_minipreguntas.append("respuesta_completa")

        self.minirespuestas.append(self.respuesta_prof) 

        info_profesor = []
        for minipregunta, minirespuesta in zip(self.minipreguntas, self.minirespuestas):
            info_profesor.append([minipregunta,minirespuesta])

        json_object = json.dumps(info_profesor, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OutputFiles/MinirespuestasProfesor.json", "w") as outfile:
            outfile.write(json_object)         

class Semantica():
    def __init__(self, KwSearch, settings):
        #print(f'Aqui las funciones de semantica')
        self.KwSearch = KwSearch
        self.modelsToTest = ['distiluse-base-multilingual-cased-v1'
                ,'paraphrase-multilingual-MiniLM-L12-v2'
                ,'paraphrase-multilingual-mpnet-base-v2'
                ,'all-distilroberta-v1'
                ,'bert-base-multilingual-uncased'
                ,'dccuchile_bert-base-spanish-wwm-uncased'
              ]
        self.epochsToTest = [1,5,10,30,50,100]
        self.bert_save_path = 'Jacobo/Prueba3'
        self.BertModels = SentTransf_test(self.modelsToTest, self.epochsToTest, save_path = self.bert_save_path)

        if self.KwSearch:
            #print(f'\n\n Buscando KW ..... \n\n')
            #Cargar/generar información de la búsqueda aumentada de palabras clave
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


    def Keywords(self):
        return self.file_feedback, self.file_marks,self.file_feedbackDistrib, self.file_marksDistrib

    def Analysis(self,settings, studentID, respuesta_alumno_raw):
        for model in self.modelsToTest:
            for epoch in self.epochsToTest:
        settings.student_dict["Semantica"]["Keyword profesor"] = settings.prof_keywords        

        if respuesta_alumno_raw == '':                
            for minipregunta in settings.indice_minipreguntas:
                self.output.nota_spacy = self.__createDict__(self.output.nota_spacy, studentID,minipregunta)
                self.output.nota_spacy_reducido = self.__createDict__(self.output.nota_spacy_reducido, studentID,minipregunta)
                self.output.nota_spacy_experimento = self.__createDict__(self.output.nota_spacy_experimento, studentID, minipregunta, 1)
                
                
                if minipregunta != "respuesta_completa":
                    self.output.identifyLineofResponse_toexcel.append([minipregunta, ""])


                self.output.nota_spacy[studentID][minipregunta]= [0]
                self.output.nota_spacy_reducido[studentID][minipregunta]= [0]
                #self.output.nota_spacy_experimento[studentID][minipregunta] = dict()
                self.output.nota_spacy_experimento[studentID][minipregunta]["Nota"] = dict()

                settings.answersDF_json[settings.id_number]["respuesta"] = "Respuesta en blanco"                                

                for umbralL, umbralH in zip(self.output.min_umbral, self.output.max_umbral):
                    self.output.nota_spacy_experimento[studentID][minipregunta]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = 0

            for umbralL, umbralH in zip(self.output.min_umbral, self.output.max_umbral):
                self.output.notas_calculadas['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                self.output.plot_loge['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                self.output.plot_mse['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                self.output.plot_resta['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)

        else:
            #print(f'studentID alumno: {studentID}\n')
            regex = '\\\n'
            respuesta_alumno = re.sub(regex , ' ', respuesta_alumno_raw)
            respuesta_alumno = respuesta_alumno.lower()
                    
            for minirespuesta, minipregunta in zip(settings.minirespuestas, settings.indice_minipreguntas):
                if settings.kwExtractor:
                    student_keywords = self.__KeywordExtractor__(settings, respuesta_alumno_raw)
                    settings.student_dict["Semantica"]["Keywords alumno"] = self.file_marks[studentID]
                    settings.student_dict["Semantica"]["Justificación de esos keywords"] = self.file_feedback[studentID]
                    

                if settings.similarity_type == 0:
                    self.output.nota_spacy = self.__createDict__(self.output.nota_spacy, studentID,minipregunta)
                    self.output.nota_spacy_reducido = self.__createDict__(self.output.nota_spacy_reducido, studentID,minipregunta)
                    self.output.nota_spacy_experimento = self.__createDict__(self.output.nota_spacy_experimento, studentID, minipregunta, 1)

                    self.output.identifyLineofResponse = self.__createDict__(self.output.identifyLineofResponse, studentID, minipregunta, 1)

                    

                if settings.grpSntncsMde == 0:
                    if settings.similarity_type == 0:                        
                        #similar = self.__SpacySimilarity__(respuesta_alumno_raw, minirespuesta)
                        similar = self.BertModels()
                        self.output.nota_spacy[studentID][minipregunta].append(["All lines", student_keywords, similar])

                        self.output.nota_spacy_experimento[studentID][minipregunta]["MaxSimilitud"] = similar
                        self.output.nota_spacy_experimento[studentID][minipregunta]["Frase"] = respuesta_alumno
                        self.output.nota_spacy_experimento[studentID][minipregunta]["Lineas"] = "All lines"

                        settings.answersDF_json[settings.id_number]["respuesta"] = "Para obtener la respuesta fragmentada, seleccione un modo de agrupación de frases distinto al 0"
                else:           
                
                    sentences=[]                        
                    TokenizeAnswer = sent_tokenize(respuesta_alumno)
                    for token in TokenizeAnswer:
                        regex = '\\.'
                        token = re.sub(regex , '', token)
                        sentences.append(token)
                   
                    settings.answersDF_json[settings.id_number]["respuesta"] = dict()
                    for sentence, line in zip(sentences, range(len(sentences))):
                        settings.answersDF_json[settings.id_number]["respuesta"][line + 1] = sentence


                    if settings.grpSntncsMde == 1:
                        #self.output.nota_spacy_experimento = self.__createDict__(self.output.nota_spacy_experimento, studentID, minipregunta, 1)
                        for number in list(range(int(settings.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"]),int(settings.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Maximo"] + 1))): 
                            #print(f'\n\n\n\n{sentences}\n\n')
                            self.output.nota_spacy_experimento[studentID][minipregunta][number] = dict()
                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["MaxSimilitud"] = 0
                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Frase"] = ""
                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Lineas"] = ""


                            idx = 1
                            #print(f'{number}')
                            for s in range(len(sentences)):                                
                                try:
                                    r_alumno, r_name = self.__Line2LineAnalysis__(sentences, s, number)
                                    
                                    if settings.kwExtractor:
                                        student_keywords = self.__KeywordExtractor__(settings, r_alumno)
                                        settings.student_dict["Semantica"]["Keywords alumno"] = self.file_marks[studentID]
                                    if settings.similarity_type == 0:
                                        similar = self.__SpacySimilarity__(r_alumno, minirespuesta)
                                        self.output.nota_spacy[studentID][minipregunta].append([r_name, student_keywords, similar])
                                        if similar > self.output.nota_spacy_experimento[studentID][minipregunta][number]["MaxSimilitud"]:

                                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["MaxSimilitud"] = similar
                                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Frase"] = r_alumno
                                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Lineas"] = r_name
                                        #Ejecutar solo para una línea para determinar si el algoritmo identifica la respuesta correctamente
                                        if number == 1:
                                            self.output.identifyLineofResponse[studentID][minipregunta][str(idx)] = dict()
                                            self.output.identifyLineofResponse[studentID][minipregunta][str(idx)]["Similitud"] = similar
                                            self.output.identifyLineofResponse[studentID][minipregunta][str(idx)]["Frase"] = r_alumno
                                            self.output.identifyLineofResponse[studentID][minipregunta][str(idx)]["Lineas"] = r_name
                            
                                            idx+=1                                           
                                        

                                except:
                                    break
                                                            
                    else:
                        r_alumno, r_name = self.__Set2LineAnalysis__(settings,sentences)
                        if settings.kwExtractor:
                            student_keywords = self.__KeywordExtractor__(settings, r_alumno)
                            settings.student_dict["Semantica"]["Keywords alumno"] = self.file_marks[studentID]
                        if settings.similarity_type == 0:
                            similar = self.__SpacySimilarity__(r_alumno, minirespuesta)
                            self.output.nota_spacy[studentID][minipregunta].append([r_name, student_keywords, similar])
                            self.output.nota_spacy_experimento[studentID][minipregunta]["MaxSimilitud"] = similar
                            self.output.nota_spacy_experimento[studentID][minipregunta]["Frase"] = r_alumno
                            self.output.nota_spacy_experimento[studentID][minipregunta]["Lineas"] = r_name
                
                #print(f'\n\n{self.output.nota_spacy}{self.output.nota_spacy_reducido}{self.output.nota_spacy_experimento}')   
            self.EvaluationMethod(settings,studentID)
    def saveResults(self, settings):
        self.output.saveSimilarityResults(settings)
   
    def __createDict__(self, nota_spacy:dict(), studentID, minipregunta, type = 0):
        if studentID not in nota_spacy.keys():
            nota_spacy[studentID] = dict()
        if type == 0:
            nota_spacy[studentID][minipregunta]= []
        else:
            nota_spacy[studentID][minipregunta]= dict()
        return nota_spacy

    def __Line2LineAnalysis__(self, sentences, s, number):    
        #print(f'{s} {number} {len(sentences)}')
        new_respuesta = ""                                   
        breaking_variable = sentences[s+number-1]
        for line in sentences[s:s+number]:
            new_respuesta= new_respuesta + line + '. '
            
        respuesta_alumno = new_respuesta.lower()
        #print(f'+++++++++++++++++++++++++++++++++++++++++++++++')
        #print(f'Esto es lo que quiero\n {respuesta_alumno}')
        #respuesta_alumno = respuesta_alumno.lower()       

        if number == 1:
            r_name = "Line " + str(s+1)
            
        else:                                                
            r_name = "Lines " + str(s+1) + " - " + str(s+number)

        return respuesta_alumno, r_name

    def __Set2LineAnalysis__(self, settings, sentences):
        specific_sentence = []
        for l in settings.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Set"].split():
            for number in clean_words(l):
                specific_sentence.append(number)
                #print(f'{number}')

        #print(f'{specific_sentence}\n')
        r_name = "Lines "
        new_respuesta = ""
        sntncs_lmt_up = 0
        sntncs_lmt_dwn = 0
        #specific_sentence.reverse()

        for line in specific_sentence:
            #print(f'{sentences}')
            
            if int(line)>= len(sentences):
                if not sntncs_lmt_up:
                    n_line = len(sentences)
                    new_respuesta= new_respuesta + sentences[n_line-1] + '. '
                    r_name = r_name + str(n_line) + " - "
                    sntncs_lmt_up = 1
            
            elif int(line)<= 1:
                if not sntncs_lmt_dwn:
                    new_respuesta= new_respuesta + sentences[0] + '. '
                    r_name = r_name + str(1) + " - "
                    sntncs_lmt_dwn = 1
            
            else:
                new_respuesta= new_respuesta + sentences[int(line)-1] + '. '
                r_name = r_name + line + " - "

        r_name = r_name[:-3]

        """
        for line in specific_sentence:
            if int(line)>len(sentences) and not sntncs_lmt:
                if str(len(sentences)) in specific_sentence:
                    break
                else:                                    
                    line = len(sentences)
                    sntncs_lmt = 1
                    new_respuesta= new_respuesta + sentences[int(line)-1] + '. '
                    r_name = r_name + str(int(line)) + " "
                    break

            else:
                if r_name != "Lines ":
                    print(f'Hola\n')
                    r_name = r_name + "- "

            new_respuesta= new_respuesta + sentences[int(line)-1] + '. '
            r_name = r_name + str(int(line)) + " "
        """

        respuesta_alumno = new_respuesta.lower()
        #print(f'{sentences}\n\n')
        print(f'{r_name}\n')

        return respuesta_alumno, r_name                  

    def __KeywordExtractor__(self, settings, respuesta_alumno):

        if settings.Features.lower() == "none":
            stdnt_kw = keyword_extractor(respuesta_alumno, int(settings.NMaxKeywords), 'es', int(settings.TVentana), float(settings.Deduplication_threshold), None)
        else:
            stdnt_kw = keyword_extractor(respuesta_alumno, int(settings.NMaxKeywords), 'es', int(settings.TVentana), float(settings.Deduplication_threshold), settings.Features)

        settings.student_dict["Semantica"]["Keywords alumno (auto)"] = stdnt_kw

        return stdnt_kw
 
    def __SpacySimilarity__(self, respuesta_alumno, respuesta_profesor):
        
        doc1 = nlp(respuesta_alumno)
        doc2 = nlp(respuesta_profesor)

        """
        frase1 = "El gobierno del dato es una forma de obtener datos de forma ineficiente"
        frase2 = "El gobierno del dato es una forma de obtener datos de forma eficiente"
        doc1 = nlp(frase1)
        doc2 = nlp(frase2)

        #print(f'\nRespuesta del alumno: \n{doc1.text}\n{doc1.vector}')
        #print(f'\n\n Respuesta del profesor: \n{doc2.text}\n{doc2.vector}')
        print(f'\nRespuesta del alumno: \n{doc1.text}\n{doc1.vector}')
        print(f'\n\n Respuesta del profesor: \n{doc2.text}\n{doc2.vector}')
        similar = round(doc1.similarity(doc2), 3)
        print(f'\nSimilar: {similar}\n')

        frase1 = "Me estoy extendiendo a proposito, no tengo ni idea de que poner ya que esto es una prueba. El gobierno del dato es una forma de obtener datos de forma eficiente pero a veces me expreso de esta manera para enmascarar falta de conocimiento y otras veces simplemente me extiendo porque es lo que quiero. "
        frase2 = "El gobierno del dato es una forma de obtener datos de forma eficiente"
        doc1 = nlp(frase1)
        doc2 = nlp(frase2)

        #print(f'\nRespuesta del alumno: \n{doc1.text}\n{doc1.vector}')
        #print(f'\n\n Respuesta del profesor: \n{doc2.text}\n{doc2.vector}')
        print(f'\nRespuesta del alumno: \n{doc1.text}\n{doc1.vector}')
        print(f'\n\n Respuesta del profesor: \n{doc2.text}\n{doc2.vector}')

        """
        similar = round(doc1.similarity(doc2), 3)
        #print(f'\nSimilar: {similar}\n')
        return similar
    
    def EvaluationMethod(self,settings, studentID):

        #print(f'{semantica_output}')
        #print(f'{notas}\n\n\n{nota_spacy}\n\n\n{len(notas)} \n\n\n{len(nota_spacy)}')
        #notaSpacy = statistics.mean(nota_spacy)

        if settings.similarity_type == 0:        
            notaSpacy = 0
            esSuperior = 0
            esIntermedio = 0        
            self.output.nota_spacy_experimento[studentID]["Nota"] = dict()

            for umbralL, umbralH in zip(self.output.min_umbral, self.output.max_umbral):
                self.output.nota_spacy_experimento[studentID]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = 0
                #print(f'\n\n{self.output.nota_spacy}')
                for pregunta in self.output.nota_spacy[studentID]:
                    if pregunta != "respuesta_completa":
                        self.output.nota_spacy_reducido[studentID][pregunta] = []

                        for info in self.output.nota_spacy[studentID][pregunta]:
                            #print(f'{info[2]}\n\n')
                            try:
                                if info[2] >= umbralL:
                                    if info[2] <= umbralH:
                                        self.output.nota_spacy_reducido[studentID][pregunta].append(info)
                                        if not esSuperior:
                                            esIntermedio = 1
                                    else:
                                        esIntermedio = 0
                                        esSuperior = 1
                                                                
                            except:
                                continue

                    if esSuperior: 
                        notaSpacy +=1
                    elif esIntermedio:
                        notaSpacy += 0.5

                    esSuperior = 0
                    esIntermedio = 0

                self.output.nota_spacy_experimento[studentID]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = notaSpacy/4

                self.output.notas_calculadas['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(notaSpacy/4)

                self.output.plot_loge['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(round(mean_squared_log_error([settings.nota_prof], [notaSpacy/4]), 4))

                self.output.plot_mse['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(round(mean_squared_error([settings.nota_prof], [notaSpacy/4]), 4))

                self.output.plot_resta['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(round(settings.nota_prof - (notaSpacy/4), 4))

                nota_Semantica = settings.PesoSmntca_Similitud * notaSpacy/4 + settings.PesoSmntca_KW * float(re.sub("Nota: ","",self.file_marks[studentID][1]))

                settings.student_dict["Semantica"]["Nota en Semantica"] = nota_Semantica

                notaSpacy = 0

            aux = copy.deepcopy(self.output.identifyLineofResponse)
            for minipregunta in settings.indice_minipreguntas:
                for indx in aux[studentID][minipregunta].keys():
                    print(f'{self.output.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]}{self.output.nota_spacy_experimento[studentID][minipregunta][1]["MaxSimilitud"]}{abs(self.output.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"] - self.output.nota_spacy_experimento[studentID][minipregunta][1]["MaxSimilitud"])}\n\n')
                    if abs(self.output.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"] - self.output.nota_spacy_experimento[studentID][minipregunta][1]["MaxSimilitud"]) > 0.075:
                        del self.output.identifyLineofResponse[studentID][minipregunta][indx]
                
            #Getting the number of the guess
            for minipregunta in settings.indice_minipreguntas:
                if minipregunta != "respuesta_completa":
                    max_n = -999999
                    indx_queue = 0
                    queue = []
                    highlightedrows = ""
                    highlightedmarks = ""

                    for iter in self.output.identifyLineofResponse[studentID][minipregunta].keys():
                        for indx in self.output.identifyLineofResponse[studentID][minipregunta].keys():
                            if self.output.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"] > max_n and not indx in queue and self.output.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]>settings.LofRespThreshold:
                                max_n = self.output.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]
                                indx_queue = indx
                        queue.append(indx_queue)
                        highlightedrows = highlightedrows + str(indx_queue) + " "
                        highlightedmarks = highlightedmarks + str(max_n) + " "
                        max_n = -999999
                        indx_queue = 0

                    self.output.identifyLineofResponse_toexcel.append([minipregunta, highlightedrows, highlightedmarks])
                    print(f'{minipregunta}\n{highlightedrows}')
                    highlightedrows = ""
                    highlightedmarks = ""
                    queue = []
                    

 


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
            settings.student_dict["Ortografia"]["Errores ortograficos"] = [errores, mistakes]
        settings.student_dict["Ortografia"]["Nota en Ortografía"] = nota_Orto

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
        
            settings.student_dict["Sintaxis"]["Frases utilizadas para responder a la pregunta"] = sentencesLenght
            settings.student_dict["Sintaxis"]["Palabras utilizadas para responder a la pregunta"] = wordsLenght
            settings.student_dict["Sintaxis"]["Index Fernandez Huerta"] = FH
            settings.student_dict["Sintaxis"]["Legibilidad F-H"] = legibilidad_fh
            settings.student_dict["Sintaxis"]["mu index"] = mu
            settings.student_dict["Sintaxis"]["Legibilidad Mu"] = legibilidad_mu
            settings.student_dict["Sintaxis"]["Nota en Sintaxis"] = nota_Sintaxis


    def saveResults(self, settings):
        self.output.saveLegibilityResults(settings)

class SemanticOutput():
    def __init__(self, settings):
        self.nota_spacy = dict()
        self.nota_spacy_reducido = dict()
        self.nota_spacy_experimento = dict()

        self.identifyLineofResponse = dict()
        self.identifyLineofResponse_toexcel = []


        self.mse = []
        self.loge = []

        self.notas_calculadas = dict()

        self.min_umbral = []
        self.max_umbral = []
        r= settings.MinSpacySimilar.split(",")

        #self.notas_calculadas["studentID"] = []
        for i in r:
            c_w= clean_words(i)
            self.min_umbral.append(float(c_w[0]+'.'+c_w[1]))
            self.max_umbral.append(float(c_w[2]+'.'+c_w[3]))
            self.notas_calculadas['Umbral ' + c_w[0]+'.'+c_w[1] + ' - ' + c_w[2]+'.'+c_w[3]] = []

        self.plot_mse = copy.deepcopy(self.notas_calculadas)
        self.plot_loge = copy.deepcopy(self.notas_calculadas)
        self.plot_resta = copy.deepcopy(self.notas_calculadas)


        #print(f'\n\n Umbrales spacy: {self.min_umbral}{self.max_umbral}\n\n')

    def plotExperimento(self,notas, y, save_file = "Img_MSERealvsCalculatedMarks.png", labelx = "Student studentID", labely = "MSE", title = "MSE Real vs Calculated Marks"):
        
        try:
            os.mkdir('Images')
        except:
            try:
                os.mkdir('Images/ImagenesExperimento2')
            except:    
                pass
        
        #print(f'AAAAAAAAAAAAAAAA{y}')
        x = []
        for i in range(len(notas)):
            x.append(i)
        #print(f'AAAAAdddAAAAAAAAAAA{x}')
        #print(f'AATengo esto{notas}')
        plt.figure(figsize=(15,7))
        plt.plot(x, notas, label = "Calculated Marks", color = (0.1,0.1,0.1))
        if len(y) >1:
            plt.plot(x, y, '--',label = "Real marks", color = (0.5,0.5,0.5))

        plt.xlabel(labelx)
        plt.ylabel(labely)
        plt.legend(loc=1)
        plt.title(title)
        plt.xticks(rotation=-45)
        plt.grid()
        plt.savefig("Images/ImagenesExperimento2/"+save_file)
        plt.cla()

    def plotExperimento2(self, save_file, df):

        try:
            os.mkdir('Images')
        except:
            try:
                os.mkdir('Images/ImagenesExperimento')
            except:    
                pass

        real_marks_category = list(set(df["Nota Real"]))
        real_marks_category.sort()

        for col_name in df.columns:
            cmpMarks_list=[]
            
            for j in real_marks_category:
                if round(float(j),3) >= 0:
                    for i in range(len(df[col_name])):  
                        if round(float(df["Nota Real"][i]),3) == round(float(j),3):
                            cmpMarks_list.append([df[col_name][i],df["Nota Real"][i]])

            cmpMarks_list = np.array(cmpMarks_list)
            #print(f'{cmpMarks_list}\n\n')
            #print(f'aa{cmpMarks_list[:, 0].astype(np.float32)}')
            plt.scatter(cmpMarks_list[:, 1].astype(np.float32), cmpMarks_list[:, 0].astype(np.float32), edgecolors=(0, 0, 0), alpha = 0.4)
            plt.plot([0.0, 1.0], [0.0, 1.0],
            'k--', color = 'black', lw=2)
            plt.title('Valor predicho vs valor real' + str(col_name), fontsize = 10, fontweight = "bold")
            plt.xlabel("Real")
            plt.ylabel("Predicción")
            plt.savefig("Images/ImagenesExperimento/"+ str(col_name)+save_file)
            plt.cla()
            #plt.show()
            del cmpMarks_list

    def plotExperimento3(self, save_file, x):
        try:
            os.mkdir('Images')
        except:
            try:
                os.mkdir('Images/ImagenesExperimento3')
            except:    
                pass

        ax= sns.histplot(
                data    = x,
                stat    = "count",
                kde     = True,
                color = "black"
            )
        ax.set(xlabel='Deviation', ylabel='Count')

        figure = ax.get_figure()    
        figure.savefig("Images/ImagenesExperimento3/"+save_file)
        del figure
        ax.cla()


    def saveSimilarityResults(self, settings):
        df2 = pd.DataFrame()
        df2["Nota Real"] = settings.notas
        self.loge.append(0)
        self.mse.append(0)

        
        for intervalo_umbral in self.notas_calculadas:
            #print(f'{intervalo_umbral}')
            if intervalo_umbral == "ID":
                continue
            else:
                #print(f'BBBBBBBBBBBB{self.notas_calculadas[intervalo_umbral]}')
                self.plotExperimento(self.notas_calculadas[intervalo_umbral],settings.notas, str(intervalo_umbral)+'.png')
                df2[str(intervalo_umbral)] = self.notas_calculadas[intervalo_umbral]
                self.loge.append(round(mean_squared_log_error(settings.notas, self.notas_calculadas[intervalo_umbral]), 4))
                self.mse.append(round(mean_squared_error(settings.notas, self.notas_calculadas[intervalo_umbral]), 4))

                self.plotExperimento3(str(intervalo_umbral) + 'MSE.png', self.plot_mse[intervalo_umbral])
                self.plotExperimento3(str(intervalo_umbral) + 'LOGE.png', self.plot_loge[intervalo_umbral])

                self.plotExperimento3(str(intervalo_umbral) + 'Diferencia.png', self.plot_resta[intervalo_umbral])

                self.plotExperimento(self.plot_mse[intervalo_umbral], [], str(intervalo_umbral) + 'plotMSE.png')
                self.plotExperimento(self.plot_loge[intervalo_umbral], [], str(intervalo_umbral) + 'plotLOGE.png')
        
        
        self.plotExperimento2("Ejemplo.png", df2)

        df2.loc[len(settings.notas) + 1]= self.mse
        df2.loc[len(settings.notas) + 2]= self.loge


        try:
            os.mkdir('OutputFiles')
        except:
            pass

        # Serializing json 
        json_object = json.dumps(self.nota_spacy, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OutputFiles/AnalisisSemantico.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.nota_spacy_reducido, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OutputFiles/AnalisisSemanticoReducido.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.nota_spacy_experimento, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OutputFiles/ExperimentoSemantica.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.identifyLineofResponse, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OutputFiles/ExperimentoIdentificarLineaRespuesta.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(settings.answersDF_json, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OutputFiles/OriginalRespuestaSeparada.json", "w") as outfile:
            outfile.write(json_object)

        df_lineasIdentificadas = pd.DataFrame(self.identifyLineofResponse_toexcel)
        df_lineasIdentificadas.to_excel('OutputFiles/LineaRespuesta2.xlsx', sheet_name='lineas')

        df3 = pd.DataFrame.from_dict(self.nota_spacy_experimento, orient='index')
        df3.to_excel('OutputFiles/ExperimentoSemantica2.xlsx', sheet_name='notas')

        df2.to_excel('OutputFiles/NotasExperiment.xlsx', sheet_name='notas')

class SintacticOutput():
    def __init__(self):
        self.leg_FH =[]
        self.leg_mu = []

    def saveLegibilityResults(self, settings):

        try:
            os.mkdir('Images')
        except:
            try:
                os.mkdir('Images/Sintaxis')
            except:    
                pass

            x = []
            for i in range(len(settings.notas)):
                x.append(i)

            plt.figure(figsize=(15,7))
            plt.plot(x, self.leg_FH, label = "FH", color = (0.1,0.1,0.1))
            plt.plot(x, self.leg_mu, label = "mu", color = (0.5,0.5,0.5))
            plt.plot(x, np.multiply(settings.notas, 100), '--', label = "Real marks", color = (1,0,0))
            plt.xlabel("Student ID")
            plt.ylabel("Valor (0-100)")
            plt.legend(loc=1)
            plt.title("FH vs mu")
            plt.xticks(rotation=-45)
            plt.grid()
            plt.savefig("Images/Sintaxis/Img_FHvsMu.png")   
 
class OrtographicOutput():
    def __init__(self):
        self.notaOrtografia = []
 
 
 
#METEEEER
#nota_Semantica = self.PesoSmntca_Similitud * notaSpacy/4 + self.PesoSmntca_KW * float(re.sub("Nota: ","",self.file_marks[studentID][1]))              
