import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import copy
import json
import re

import spacy
nlp = spacy.load('es_core_news_sm')

from kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo, saveKWInfo, loadKWInfo
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from utils import spelling_corrector, clean_words, sent_tokenize, mu_index, FHuertas_index, check_senteces_words, keyword_extractor,getNameFile

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

class Semantica():
    def __init__(self, KwSearch, settings):
        print(f'Aqui las funciones de semantica')
        self.KwSearch = KwSearch

        if self.KwSearch:
            print(f'\n\n Buscando KW ..... \n\n')
            #Cargar/generar información de la búsqueda aumentada de palabras clave
            try:
                os.mkdir('__appcache__')
                Pobs, Ptrans, LemmaDictionary = loadHMMInfo()

                KWfile_info = NLP_Questions(settings.answersDF,{},{}, settings.LemmaDictionary)
                IdentifiedKW = NLP_Answers(settings.answersDF,KWfile_info.Synonyms(), KWfile_info.Antonyms(), KWfile_info.LemmatizedKeywords(), LemmaDictionary, Ptrans, Pobs, KWfile_info.Windows())

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

        if respuesta_alumno_raw == '':                
            for minipregunta in settings.indice_minipreguntas:
                self.output.nota_spacy = self.__createDict__(self.output.nota_spacy, studentID,minipregunta)
                self.output.nota_spacy_reducido = self.__createDict__(self.output.nota_spacy_reducido, studentID,minipregunta)
                self.output.nota_spacy_experimento = self.__createDict__(self.output.nota_spacy_experimento, studentID, minipregunta, 1)

                self.output.nota_spacy[studentID][minipregunta]= [0]
                self.output.nota_spacy_reducido[studentID][minipregunta]= [0]
                #self.output.nota_spacy_experimento[studentID][minipregunta] = dict()
                self.output.nota_spacy_experimento[studentID][minipregunta]["Nota"] = dict()

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
                if settings.similarity_type == 0:
                    self.output.nota_spacy = self.__createDict__(self.output.nota_spacy, studentID,minipregunta)
                    self.output.nota_spacy_reducido = self.__createDict__(self.output.nota_spacy_reducido, studentID,minipregunta)

                if settings.grpSntncsMde == 0:
                    if settings.similarity_type == 0:                        
                        similar = self.__SpacySimilarity__(respuesta_alumno_raw, minirespuesta)
                        self.output.nota_spacy[studentID][minipregunta].append(["All lines", student_keywords, similar])
                else:           
                
                    sentences=[]                        
                    TokenizeAnswer = sent_tokenize(respuesta_alumno)
                    for token in TokenizeAnswer:
                        regex = '\\.'
                        token = re.sub(regex , '', token)
                        sentences.append(token)

                    if settings.grpSntncsMde == 1:
                        self.output.nota_spacy_experimento = self.__createDict__(self.output.nota_spacy_experimento, studentID, minipregunta, 1)
                        for number in list(range(int(settings.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"]),int(settings.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Maximo"] + 1))): 
                            #print(f'\n\n\n\n{sentences}\n\n')
                            self.output.nota_spacy_experimento[studentID][minipregunta][number] = dict()
                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["MaxSimilitud"] = 0
                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Frase"] = ""
                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Lineas"] = ""

                            for s in range(len(sentences)):
                                try:
                                    respuesta_alumno, r_name = self.__Line2LineAnalysis__(sentences, s, number)
                                    if settings.kwExtractor:
                                        student_keywords = self.__KeywordExtractor__(settings, respuesta_alumno)
                                    if settings.similarity_type == 0:
                                        similar = self.__SpacySimilarity__(respuesta_alumno, minirespuesta)
                                        self.output.nota_spacy[studentID][minipregunta].append([r_name, student_keywords, similar])
                                        if similar > self.output.nota_spacy_experimento[studentID][minipregunta][number]["MaxSimilitud"]:
                                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["MaxSimilitud"] = similar
                                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Frase"] = respuesta_alumno
                                            self.output.nota_spacy_experimento[studentID][minipregunta][number]["Lineas"] = r_name

                                except:
                                    break
                                                            
                    else:
                        respuesta_alumno, r_name = self.__Set2LineAnalysis__(settings,sentences)
                        if settings.kwExtractor:
                            student_keywords = self.__KeywordExtractor__(settings, respuesta_alumno)
                        if settings.similarity_type == 0:
                            similar = self.__SpacySimilarity__(respuesta_alumno, minirespuesta)
                            self.output.nota_spacy[studentID][minipregunta].append([r_name, student_keywords, similar])
                
                print(f'\n\n{self.output.nota_spacy}{self.output.nota_spacy_reducido}{self.output.nota_spacy_experimento}')   
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
        return respuesta_alumno, r_name                  

    def __KeywordExtractor__(self, settings, respuesta_alumno):

        if settings.Features.lower() == "none":
            stdnt_kw = keyword_extractor(respuesta_alumno, int(settings.NMaxKeywords), 'es', int(settings.TVentana), float(settings.Deduplication_threshold), None)
        else:
            stdnt_kw = keyword_extractor(respuesta_alumno, int(settings.NMaxKeywords), 'es', int(settings.TVentana), float(settings.Deduplication_threshold), settings.Features)

        return stdnt_kw
 
    def __SpacySimilarity__(self, respuesta_alumno, respuesta_profesor):
        doc1 = nlp(respuesta_alumno)
        doc2 = nlp(respuesta_profesor)
        similar = round(doc1.similarity(doc2), 3)
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
                print(f'\n\n{self.output.nota_spacy}')
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

                notaSpacy = 0 


class Ortografia ():
    def __init__(self):
        print(f'Aqui lo de ortografia')
        self.output = OrtographicOutput()
    
    def Analysis(self,settings, respuesta_alumno):
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
        print(f'Aqui lo de sintaxis')
        self.output = SintacticOutput()

    def Analysis(self, respuesta_alumno):
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

    def saveResults(self, settings):
        self.output.saveLegibilityResults(settings)

class SemanticOutput():
    def __init__(self, settings):
        self.nota_spacy = dict()
        self.nota_spacy_reducido = dict()
        self.nota_spacy_experimento = dict()

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


        print(f'\n\n Umbrales spacy: {self.min_umbral}{self.max_umbral}\n\n')

    def plotExperimento(self,notas, y, save_file = "Img_MSERealvsCalculatedMarks.png", labelx = "Student studentID", labely = "MSE", title = "MSE Real vs Calculated Marks"):
        
        try:
            os.mkdir('__ImagenesExperimento2')
        except:
            pass
        
        print(f'AAAAAAAAAAAAAAAA{y}')
        x = []
        for i in range(len(notas)):
            x.append(i)
        print(f'AAAAAdddAAAAAAAAAAA{x}')
        print(f'AATengo esto{notas}')
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
        plt.savefig("__ImagenesExperimento2/"+save_file)
        plt.cla()

    def plotExperimento2(self, save_file, df):

        try:
            os.mkdir('__ImagenesExperimento')
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
            print(f'{cmpMarks_list}\n\n')
            print(f'aa{cmpMarks_list[:, 0].astype(np.float32)}')
            plt.scatter(cmpMarks_list[:, 1].astype(np.float32), cmpMarks_list[:, 0].astype(np.float32), edgecolors=(0, 0, 0), alpha = 0.4)
            plt.plot([0.0, 1.0], [0.0, 1.0],
            'k--', color = 'black', lw=2)
            plt.title('Valor predicho vs valor real' + str(col_name), fontsize = 10, fontweight = "bold")
            plt.xlabel("Real")
            plt.ylabel("Predicción")
            plt.savefig("__ImagenesExperimento/"+ str(col_name)+save_file)
            plt.cla()
            #plt.show()
            del cmpMarks_list

    def plotExperimento3(self, save_file, x):
        try:
            os.mkdir('__ImagenesExperimento3')
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
        figure.savefig("__ImagenesExperimento3/"+save_file)
        del figure
        ax.cla()


    def saveSimilarityResults(self, settings):
        df2 = pd.DataFrame()
        df2["Nota Real"] = settings.notas
        self.loge.append(0)
        self.mse.append(0)


        
        for intervalo_umbral in self.notas_calculadas:
            print(f'{intervalo_umbral}')
            if intervalo_umbral == "ID":
                continue
            else:
                print(f'BBBBBBBBBBBB{self.notas_calculadas[intervalo_umbral]}')
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

        # Serializing json 
        json_object = json.dumps(self.nota_spacy, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("AnalisisSemantico.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.nota_spacy_reducido, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("AnalisisSemanticoReducido.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.nota_spacy_experimento, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("ExperimentoSemantica.json", "w") as outfile:
            outfile.write(json_object)

        df2.to_excel('NotasExperiment.xlsx', sheet_name='notas')

class SintacticOutput():
    def __init__(self):
        self.leg_FH =[]
        self.leg_mu = []

    def saveLegibilityResults(self, settings):
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
            plt.savefig("Img_FHvsMu.png")   
 
class OrtographicOutput():
    def __init__(self):
        self.notaOrtografia = []
 
 
 
#METEEEER
#nota_Semantica = self.PesoSmntca_Similitud * notaSpacy/4 + self.PesoSmntca_KW * float(re.sub("Nota: ","",self.file_marks[studentID][1]))              

