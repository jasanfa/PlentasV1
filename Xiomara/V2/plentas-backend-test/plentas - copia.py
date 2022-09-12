import pandas as pd
import re
import json
from sklearn.metrics import mean_squared_error, mean_squared_log_error
import numpy as np
import os
import statistics
import matplotlib.pyplot as plt

import copy

import spacy
nlp = spacy.load('es_core_news_sm')

from utils import silabizer, spelling_corrector, clean_words, sent_tokenize, word_categorization, mu_index, FHuertas_index, check_senteces_words, keyword_extractor,getNameFile
from kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo, saveKWInfo, loadKWInfo

from tools import plotExperimento2, plotExperimento, plotExperimento3, Semantica


class Plentas():
    
    def __init__(self, settings_file):

        #lectura del fichero de configuracion
        self.__getConfigSettings(settings_file)
        #lectura del fichero de preguntas/respuestas
        self.__getData(self.__json_file_in)

        prueba_elim = Semantica()

        if self.BusquedaKW:
            print(f'\n\n Buscando KW ..... \n\n')
            #Cargar/generar información de la búsqueda aumentada de palabras clave
            try:
                os.mkdir('__appcache__')
                Pobs, Ptrans, LemmaDictionary = loadHMMInfo()

                KWfile_info = NLP_Questions(self.answersDF,{},{}, self.LemmaDictionary)
                IdentifiedKW = NLP_Answers(self.answersDF,KWfile_info.Synonyms(), KWfile_info.Antonyms(), KWfile_info.LemmatizedKeywords(), LemmaDictionary, Ptrans, Pobs, KWfile_info.Windows())

                self.file_feedback = IdentifiedKW.showFeedback()
                self.file_marks = IdentifiedKW.showMarks()
                self.file_feedbackDistrib = IdentifiedKW.showFeedbackDistribution()
                self.file_marksDistrib = IdentifiedKW.showKeywordsDistribution()

                saveKWInfo(getNameFile(self.__json_file_in), self.file_feedback, self.file_marks,self.file_feedbackDistrib, self.file_marksDistrib)
                
            except:
                self.file_marks, self.file_feedback, self.file_marksDistrib, self.file_feedbackDistrib = loadKWInfo(getNameFile(self.__json_file_in))
        else:
            print(f'\n\n Omitiendo busqueda de KW ..... \n\n')          


   
    def __getConfigSettings(self, df):        

        self.configDf = df

        self.__json_file_in = df["ruta_fichero_entrada"]
        self.__json_file_out = df["ruta_fichero_salida"]
        self.__hunspell_aff = df["ruta_hunspell"]["aff"]
        self.__hunspell_dic = df["ruta_hunspell"]["dic"]

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
            self.setFrases = 0
        elif int(df["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"])>0:
            self.setFrases = 1
        else:
            self.setFrases = 2

        #print(f'+++++++++ Estoy poniendo setfrases con valor de {self.setFrases} +++++++++')

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

        self.notas_calculadas = dict()
        self.min_umbral = []
        self.max_umbral = []
        r= self.MinSpacySimilar.split(",")

        #self.notas_calculadas["ID"] = []
        for i in r:
            c_w= clean_words(i)
            self.min_umbral.append(float(c_w[0]+'.'+c_w[1]))
            self.max_umbral.append(float(c_w[2]+'.'+c_w[3]))
            self.notas_calculadas['Umbral ' + c_w[0]+'.'+c_w[1] + ' - ' + c_w[2]+'.'+c_w[3]] = []

        
        
        self.plot_mse = copy.deepcopy(self.notas_calculadas)
        self.plot_loge = copy.deepcopy(self.notas_calculadas)
        self.plot_resta = copy.deepcopy(self.notas_calculadas)

        print(f'\n\n Umbrales spacy: {self.min_umbral}{self.max_umbral}\n\n')  
        



    def __getData(self, json_file):

        #json_file = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/biConNotaAnon.json' 
        with open(json_file, "r", encoding="utf8") as f:
            data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")

        self.answersDF = data        
        df = pd.DataFrame(data)
        self.minipreguntas = []
        self.minirespuestas = []
        self.indice_minipreguntas = []
        self.respuesta_prof = ""

        self.enunciado = df['metadata'][0]['enunciado']
        self.prof_keywords = df['metadata'][0]['keywords']

        try:
            i=0
            while True:
            #for i in range(4):
                self.minirespuestas.append(df['metadata'][0]['minipreguntas'][i]['minirespuesta'])
                self.minipreguntas.append(df['metadata'][0]['minipreguntas'][i]['minipregunta'])

                self.indice_minipreguntas.append("minipregunta" + str(i))              

                if i == 0:        
                    self.respuesta_prof = self.respuesta_prof + self.minirespuestas[i] 
                else:
                    self.respuesta_prof = self.respuesta_prof + ' ' + self.minirespuestas[i] 
                
                i+=1
        except:
            self.indice_minipreguntas.append("respuesta_completa")

        self.minirespuestas.append(self.respuesta_prof)           



    def __ApplySemanticFunctions(self, respuesta_alumno, respuesta_profesor):
        if self.Features.lower() == "none":
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.NMaxKeywords), 'es', int(self.TVentana), float(self.Deduplication_threshold), None)
        else:
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.NMaxKeywords), 'es', int(self.TVentana), float(self.Deduplication_threshold), self.Features)

        doc1 = nlp(respuesta_alumno)
        doc2 = nlp(respuesta_profesor)
        similar = round(doc1.similarity(doc2), 3)

        return [stdnt_kw, similar]


    def processData(self):
        output_json=[]
        nota_spacy= dict()
        nota_spacy_reducido = dict()

        nota_spacy_experimento = dict()
        mse = []
        loge = []
            
        notas=[]

        leg_FH =[]
        leg_mu = []
        df = self.answersDF
        df = pd.DataFrame(df)
        #rango = list(range(0,4)) + list(range(6,9))
        #print(f'{rango}')
        #print(f'{df["respuesta"][0:4, 6:9]}')
        
        if self.rango_ID == "All":
            IDs = list(range(len(df['hashed_id'])))
        else:
            rango = []
            r= self.rango_ID.split(",")
            for i in r:
                c_w= clean_words(i)
                if len(c_w) == 2:
                    rango= rango + list(range(int(c_w[0]),int(c_w[1]) + 1))
                elif len(c_w) == 1:
                    rango= rango + list(range(int(c_w[0]),int(c_w[0]) +1))
            IDs = rango  

        for id in IDs:
            ID = df['hashed_id'][id]
            respuesta_alumno_raw = df['respuesta'][id] 
            nota_prof = df['nota'][id]
            notas.append(nota_prof)

            #self.notas_calculadas["ID"].append(ID)
            

            nota_spacy[ID] = dict()
            nota_spacy_reducido[ID] = dict()

            nota_spacy_experimento[ID] = dict()

            if respuesta_alumno_raw == '':
                
                for minipregunta in self.indice_minipreguntas:
                    nota_spacy[ID][minipregunta]= [0]
                    nota_spacy_reducido[ID][minipregunta]= [0]
                    nota_spacy_experimento[ID][minipregunta] = dict()
                    nota_spacy_experimento[ID][minipregunta]["Nota"] = dict()

                    for umbralL, umbralH in zip(self.min_umbral, self.max_umbral):
                        nota_spacy_experimento[ID][minipregunta]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = 0

                for umbralL, umbralH in zip(self.min_umbral, self.max_umbral):
                    self.notas_calculadas['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                    self.plot_loge['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                    self.plot_mse['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                    self.plot_resta['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0)
                        

                
                #print('El alumno no ha contestado a la pregunta')                
 
                leg_FH.append(0)
                leg_mu.append(0)


                
                #err = round(mean_squared_error([nota_prof], [0]), 4)
                #mse.append(err)


                        

                student_dict = { 'ID': ID, 'Errores ortograficos': None,
                                'Frases utilizadas para responder a la pregunta': None,
                                'Palabras utilizadas para responder a la pregunta': None,
                                'Index Fernandez Huerta': None, 'Legibilidad F-H': None,
                                'mu index': None, 'Legibilidad Mu': None,
                                'Keywords alumno': None, 'Keyword profesor': None,
                            'Spacy similarity': None, 'Nota profesor': nota_prof}            
            else:
                
                #print(f'ID alumno: {ID}\n')
                regex = '\\\n'
                respuesta_alumno = re.sub(regex , ' ', respuesta_alumno_raw)
                respuesta_alumno = respuesta_alumno.lower()

                if self.Ortografia:
                    errores, mistakes = spelling_corrector(respuesta_alumno, self.__hunspell_aff, self.__hunspell_dic)
                    if errores <= self.FaltasSalvaguarda:
                        nota_Ortografia = self.PesoOrtografia
                    else:

                        try:
                            rel = self.PesoOrtografia/self.NMaxErrores 
                            nota_Ortografia = self.PesoOrtografia - (errores - self.FaltasSalvaguarda) * rel
                        except:
                            nota_Ortografia = 0

                        if nota_Ortografia < 0:
                            nota_Ortografia = 0

                if self.Sintaxis:
                    sentencesLenght, wordsLenght, syll, letter_per_word = check_senteces_words(respuesta_alumno)
                    #print(wordsLenght)
                    FH, legibilidad_fh = FHuertas_index(sentencesLenght, wordsLenght, syll)
                    mu, legibilidad_mu = mu_index(sentencesLenght, wordsLenght, letter_per_word)

                    leg_FH.append(FH)
                    leg_mu.append(mu)

                if self.Semantica:

                    for minirespuesta, minipregunta in zip(self.minirespuestas, self.indice_minipreguntas):

                        nota_spacy[ID][minipregunta]= []
                        nota_spacy_reducido[ID][minipregunta]= []
                        #nota_spacy_experimento[ID][minipregunta]= []
             
 
                        if self.setFrases == 0:
                            student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno_raw, minirespuesta)

                            nota_spacy[ID][minipregunta].append(["All lines", student_keywords, similar])

                        else:           
                        
                            sentences=[]                        
                            TokenizeAnswer = sent_tokenize(respuesta_alumno)
                            for token in TokenizeAnswer:
                                regex = '\\.'
                                token = re.sub(regex , '', token)
                                sentences.append(token)

                            if self.setFrases == 1:
                                nota_spacy_experimento[ID][minipregunta] = dict()
                                
                                for number in list(range(int(self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"]),int(self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Maximo"] + 1))):
                                    
                                    #print(f'\n\n\n\n{sentences}\n\n')
                                    nota_spacy_experimento[ID][minipregunta][number] = dict()
                                    nota_spacy_experimento[ID][minipregunta][number]["MaxSimilitud"] = 0
                                    nota_spacy_experimento[ID][minipregunta][number]["Frase"] = ""
                                    nota_spacy_experimento[ID][minipregunta][number]["Lineas"] = ""


                                    for s in range(len(sentences)):
                                        #print(f'{s} {number} {len(sentences)}')
                                        new_respuesta = ""

                                        try:                                       
                                            breaking_variable = sentences[s+number-1]
                                            for line in sentences[s:s+number]:
                                                new_respuesta= new_respuesta + line + '. '
                                                
                                            respuesta_alumno = new_respuesta.lower()
                                            #print(f'+++++++++++++++++++++++++++++++++++++++++++++++')
                                            #print(f'Esto es lo que quiero\n {respuesta_alumno}')
                                            respuesta_alumno = respuesta_alumno.lower()
                                            student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno, minirespuesta)

                                            if number == 1:
                                                r_name = "Line " + str(s+1)
                                                
                                            else:                                                
                                                r_name = "Lines " + str(s+1) + " - " + str(s+number)

                                            nota_spacy[ID][minipregunta].append([r_name, student_keywords, similar])

                                            if similar > nota_spacy_experimento[ID][minipregunta][number]["MaxSimilitud"]:
                                                nota_spacy_experimento[ID][minipregunta][number]["MaxSimilitud"] = similar
                                                nota_spacy_experimento[ID][minipregunta][number]["Frase"] = respuesta_alumno
                                                nota_spacy_experimento[ID][minipregunta][number]["Lineas"] = r_name

                                        except:
                                            break
                                                                            
                            else:

                                specific_sentence = []
                                for l in self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Set"].split():
                                    for number in clean_words(l):
                                        specific_sentence.append(number)
                                        #print(f'{number}')

                                #print(f'{len(specific_sentence)}')
                                r_name = "Lines "
                                new_respuesta = ""
                                sntncs_lmt = 0
                                #specific_sentence.reverse()
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
                                            r_name = r_name + "- "

                                    new_respuesta= new_respuesta + sentences[int(line)-1] + '. '
                                    r_name = r_name + str(int(line)) + " "

                                respuesta_alumno = new_respuesta.lower()
                                #print(f'{sentences}\n\n')
                                #print(f'{respuesta_alumno}')
                                student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno, minirespuesta)

                                nota_spacy[ID][minipregunta].append([r_name, student_keywords, similar])


                #print(f'{semantica_output}')
                #print(f'{notas}\n\n\n{nota_spacy}\n\n\n{len(notas)} \n\n\n{len(nota_spacy)}')

                #notaSpacy = statistics.mean(nota_spacy)
                
                notaSpacy = 0
                esSuperior = 0
                esIntermedio = 0



                
                nota_spacy_experimento[ID][minipregunta]["Nota"] = dict()

                for umbralL, umbralH in zip(self.min_umbral, self.max_umbral):
                    nota_spacy_experimento[ID][minipregunta]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = 0
                    

                    for pregunta in nota_spacy[ID]:
                        if pregunta != "respuesta_completa":
                            nota_spacy_reducido[ID][pregunta] = []

                            #nota_spacy_experimento[ID][minipregunta]["Nota"][] = ""
                            
                            for info in nota_spacy[ID][pregunta]:
                                #print(f'{info[2]}\n\n')
                                try:
                                    if info[2] >= umbralL:
                                        if info[2] <= umbralH:
                                            nota_spacy_reducido[ID][pregunta].append(info)
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

                    nota_spacy_experimento[ID][minipregunta]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = notaSpacy/4

                    self.notas_calculadas['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(notaSpacy/4)

                    self.plot_loge['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(round(mean_squared_log_error([nota_prof], [notaSpacy/4]), 4))

                    self.plot_mse['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(round(mean_squared_error([nota_prof], [notaSpacy/4]), 4))

                    self.plot_resta['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(round(nota_prof - (notaSpacy/4), 4))


                    notaSpacy = 0

                
                """
                self.notas_calculadas.append(notaSpacy/4)
                err = round(mean_squared_error([nota_prof], [notaSpacy/4]), 4)
                #print(f'error {err} nota {nota_prof} notaspacy{notaSpacy/4} \n') 
                #print(f'Error cuadrático medio entre la nota del profesor y la obtenida con spacy: {err*100}%')
                mse.append(err)

                """


                """""
                if len(semantica_output)>1:
                    nota_spacy.append(semantica_output[len(semantica_output)-1][2])
                    similar = semantica_output[len(semantica_output)-1][2]
                    student_keywords = semantica_output[len(semantica_output)-1][1]
                else:
                    nota_spacy.append(semantica_output[0][2])
                    similar = semantica_output[0][2]
                    student_keywords = semantica_output[0][1]
                
                """""

                #print(f'\nKeywords Alumno: {student_keywords}')
                #print(f'Keywords Profesor: {self.prof_keywords}\n')
                #print(f'spaCy similarity: {similar}')
                #print(f'Nota del profesor: {nota_prof}')
                #print('\n-----------------------------------------------------------------------------------------\n')
                
                nota_Semantica = self.PesoSmntca_Similitud * notaSpacy/4 + self.PesoSmntca_KW * float(re.sub("Nota: ","",self.file_marks[ID][1]))

                nota_Sintaxis = self.PesoSntxis_FH * FH/100 + self.PesoSntxis_Mu * mu/100
                
                #print(f'AAAAAAAAAAA\n\n{self.IdentifiedKW.showMarks()}\n\n')
                """
                student_dict = { 'ID': ID, 'Errores ortograficos': [errores, mistakes], 'Nota en Ortografía': nota_Ortografia,
                                'Frases utilizadas para responder a la pregunta': sentencesLenght,
                                'Palabras utilizadas para responder a la pregunta': wordsLenght,
                                'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                                'mu index': mu, 'Legibilidad Mu': legibilidad_mu,'Nota en Sintaxis': nota_Sintaxis,
                                'Análisis por frase': nota_spacy_reducido[ID],'Keywords alumno': self.file_marks[ID], 'Keyword profesor': self.prof_keywords, 'Justificación de esos keywords': self.file_feedback[ID], 'Nota en Semantica': nota_Semantica, 'Nota profesor': nota_prof}
                """
                student_dict = { 'ID': ID,
                'Ortografia': {              
                        'Errores ortograficos': [errores, mistakes], 'Nota en Ortografía': nota_Ortografia},
                'Sintaxis': {
                    'Frases utilizadas para responder a la pregunta': sentencesLenght,
                    'Palabras utilizadas para responder a la pregunta': wordsLenght,
                    'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                    'mu index': mu, 'Legibilidad Mu': legibilidad_mu,'Nota en Sintaxis': nota_Sintaxis},
                'Semantica':{
                    'Keywords alumno (auto)': None,'Keywords alumno': self.file_marks[ID], 'Keyword profesor': self.prof_keywords, 'Justificación de esos keywords': self.file_feedback[ID], 'Nota en Semantica': nota_Semantica, 'Nota profesor': nota_prof}}

                #nota_spacy_reducido[ID]
                output_json.append(student_dict)
                #nota_spacy = []
                #notas = []
                # notas

                

        print(f'\n\n{self.notas_calculadas}\n\n') 
        for el in self.notas_calculadas:
            print(f'\n\n Notas calculadas: {len(self.notas_calculadas[el])}')

        print(f'Notas spacy reducido:{len(nota_spacy_reducido)} Notas spacy experimento: {len(nota_spacy_experimento)} Notas spacy: {len(nota_spacy)} Notas reales: {len(notas)} \n\n')

        #import pandas as pd

        df2 = pd.DataFrame()

        df2["Nota Real"] = notas
        loge.append(0)
        mse.append(0)

        
        for intervalo_umbral in self.notas_calculadas:
            print(f'{intervalo_umbral}')
            if intervalo_umbral == "ID":
                continue
            else:
                plotExperimento(self.notas_calculadas[intervalo_umbral], notas, str(intervalo_umbral)+'.png')
                df2[str(intervalo_umbral)] = self.notas_calculadas[intervalo_umbral]
                loge.append(round(mean_squared_log_error(notas, self.notas_calculadas[intervalo_umbral]), 4))
                mse.append(round(mean_squared_error(notas, self.notas_calculadas[intervalo_umbral]), 4))

                plotExperimento3(str(intervalo_umbral) + 'MSE.png', self.plot_mse[intervalo_umbral])
                plotExperimento3(str(intervalo_umbral) + 'LOGE.png', self.plot_loge[intervalo_umbral])

                plotExperimento3(str(intervalo_umbral) + 'Diferencia.png', self.plot_resta[intervalo_umbral])

                plotExperimento(self.plot_mse[intervalo_umbral], [], str(intervalo_umbral) + 'plotMSE.png')
                plotExperimento(self.plot_loge[intervalo_umbral], [], str(intervalo_umbral) + 'plotLOGE.png')
    
        
        
        plotExperimento2("Ejemplo.png", df2)

        df2.loc[len(notas) + 1]= mse
        df2.loc[len(notas) + 2]= loge




        if self.Sintaxis:
            x = []
            for i in range(len(notas)):
                x.append(i)

            plt.figure(figsize=(15,7))
            plt.plot(x, leg_FH, label = "FH", color = (0.1,0.1,0.1))
            plt.plot(x, leg_mu, label = "mu", color = (0.5,0.5,0.5))
            plt.plot(x, np.multiply(notas, 100), '--', label = "Real marks", color = (1,0,0))
            plt.xlabel("Student ID")
            plt.ylabel("Valor (0-100)")
            plt.legend(loc=1)
            plt.title("FH vs mu")
            plt.xticks(rotation=-45)
            plt.grid()
            plt.savefig("Img_FHvsMu.png")           

        if self.Semantica:
            """
            loge = round(mean_squared_log_error(notas, self.notas_calculadas), 4)
            print(f'\n\n\n\nEl log error entre las notas reales y las calculadas es de: {loge}\n')
            mse_error = round(mean_squared_error(notas, self.notas_calculadas), 4)
            print(f'El log error entre las notas reales y las calculadas es de: {mse_error}\n\n\n\n')
            x = []
            for i in range(len(notas)):
                x.append(i)

            plt.figure(figsize=(15,7))
            plt.plot(x, self.notas_calculadas, label = "Calculated Marks", color = (0.1,0.1,0.1))
            plt.plot(x, notas, '--', label = "Real marks", color = (0.5,0.5,0.5))
            plt.xlabel("Student ID")
            plt.ylabel("Calification (0-1)")
            plt.legend(loc=1)
            plt.title("Real vs Calculated Marks")
            plt.xticks(rotation=-45)
            plt.grid()
            plt.savefig("Img_RealvsCalculatedMarks.png")


            x = []
            for i in range(len(notas)):
                x.append(i)

            plt.figure(figsize=(15,7))
            plt.plot(x, mse, label = "Mean Squared Error", color = (0.1,0.1,0.1))
            plt.xlabel("Student ID")
            plt.ylabel("MSE")
            plt.legend(loc=1)
            plt.title("MSE Real vs Calculated Marks")
            plt.xticks(rotation=-45)
            plt.grid()
            plt.savefig("Img_MSERealvsCalculatedMarks.png")

            """  

            # Serializing json 
            json_object = json.dumps(nota_spacy, indent = 11, ensure_ascii= False) 
            # Writing output to a json file
            with open("AnalisisSemantico.json", "w") as outfile:
                outfile.write(json_object)

            json_object = json.dumps(nota_spacy_reducido, indent = 11, ensure_ascii= False) 
            # Writing output to a json file
            with open("AnalisisSemanticoReducido.json", "w") as outfile:
                outfile.write(json_object)

            json_object = json.dumps(nota_spacy_experimento, indent = 11, ensure_ascii= False) 
            # Writing output to a json file
            with open("ExperimentoSemantica.json", "w") as outfile:
                outfile.write(json_object)

 
            df2.to_excel('NotasExperiment.xlsx', sheet_name='notas')
            

        # Serializing json 
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open(self.__json_file_out, "w") as outfile:
            outfile.write(json_object)
        
        return json_object

        