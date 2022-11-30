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


from codeScripts.kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo, saveKWInfo, loadKWInfo
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from codeScripts.utils import spelling_corrector, clean_words, sent_tokenize, mu_index, FHuertas_index, check_senteces_words, keyword_extractor,getNameFile

class SemanticOutput():
    def __init__(self, settings):
        self.nota_spacy = dict()
        self.nota_spacy_experimento = dict()

        self.identifyLineofResponse = dict()
        self.identifyLineofResponse_toexcel = []


        self.mse = []
        self.loge = []

        self.notas_calculadas = dict()

        self.min_umbral = []
        self.max_umbral = []
        r= settings.UmbralesSimilitud.split(",")

        #self.notas_calculadas["studentID"] = []
        for i in r:
            c_w= clean_words(i)
            self.min_umbral.append(float(c_w[0]+'.'+c_w[1]))
            self.max_umbral.append(float(c_w[2]+'.'+c_w[3]))
            self.notas_calculadas['Umbral ' + c_w[0]+'.'+c_w[1] + ' - ' + c_w[2]+'.'+c_w[3]] = []

        self.plot_mse = copy.deepcopy(self.notas_calculadas)
        self.plot_loge = copy.deepcopy(self.notas_calculadas)
        self.plot_resta = copy.deepcopy(self.notas_calculadas)

        #variables taken from the settings
        self.answersDF_json2 = dict()
        self.grpSntncsMde = settings.grpSntncsMde
        self.indiceMinipreguntas = settings.indice_minipreguntas

        #print(f'\n\n Umbrales spacy: {self.min_umbral}{self.max_umbral}\n\n')
    
        self.indx = 1

    def initInforms(self, studentID, minipregunta):
        #identificar donde está la respuesta por minipreguta
        self.identifyLineofResponse = self.__createDict__(self.identifyLineofResponse, studentID, minipregunta, 1)

        #almacenar notas del evaluation process
        #self.nota_spacy_experimento = self.__createDict__(self.nota_spacy_experimento, studentID, similarity_type, 1)
        

        self.nota_spacy_experimento[studentID] = dict()
        
        #Almacenar similitudes por minipregunta
        self.nota_spacy = self.__createDict__(self.nota_spacy, studentID, minipregunta)

        #separar y almacenar una a una las lineas de la respuesta
        self.answersDF_json2[studentID] = dict()
        self.answersDF_json2[studentID]["respuesta"] = dict()


    def updateInforms(self, studentID, umbralL, umbralH, calculatedMark, response = ""):
        

        #self.nota_spacy_experimento[studentID]["Nota"]['Umbral ' + str(umbralL) + ' - ' + str(umbralH)] = 0 if response == "" else calculatedMark/4

        
        self.notas_calculadas['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0 if response == "" else calculatedMark/4)
        self.plot_loge['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0 if response == "" else round(mean_squared_log_error([self.settings.nota_prof], [calculatedMark/4]), 4))
        self.plot_mse['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0 if response == "" else round(mean_squared_error([self.settings.nota_prof], [calculatedMark/4]), 4))
        self.plot_resta['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0 if response == "" else round(self.settings.nota_prof - (calculatedMark/4), 4))

        
        #nota_Semantica = settings.PesoSmntca_Similitud * notaSpacy/4 + settings.PesoSmntca_KW * float(re.sub("Nota: ","",self.file_marks[studentID][1]))

        #settings.student_dict["Semantica"]["Nota en Semantica"] = nota_Semantica

        for minipregunta in self.indiceMinipreguntas:
            aux = copy.deepcopy(self.identifyLineofResponse)
            for indx in aux[studentID][minipregunta].keys():
                if abs(self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"] - self.nota_spacy_experimento[studentID]["1"]["MaxSimilitud"]) > 0.075:
                    del self.identifyLineofResponse[studentID][minipregunta][indx]

            
            #Getting the number of the guess
            if response == "":
                self.identifyLineofResponse_toexcel.append([minipregunta, ""])
            else:
                max_n = -999999
                indx_queue = 0
                queue = []
                highlightedrows = ""
                highlightedmarks = ""

                for iter in self.identifyLineofResponse[studentID][minipregunta].keys():
                    for indx in self.identifyLineofResponse[studentID][minipregunta].keys():
                        if self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"] > max_n and not indx in queue and self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]>self.settings.LofRespThreshold:
                            max_n = self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]
                            indx_queue = indx
                    queue.append(indx_queue)
                    highlightedrows = highlightedrows + str(indx_queue) + " "
                    highlightedmarks = highlightedmarks + str(max_n) + " "
                    max_n = -999999
                    indx_queue = 0

                self.identifyLineofResponse_toexcel.append([minipregunta, highlightedrows, highlightedmarks])
                #print(f'{minipregunta}\n{highlightedrows}')
                highlightedrows = ""
                highlightedmarks = ""
                queue = []

    def updateInformsBucle(self, studentID, minipregunta, response, response_label, numberOfSentences, similarity, isMaxSimil):

        if numberOfSentences == 1:
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)] = dict()
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)]["Similitud"] = similarity
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)]["Frase"] = response
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)]["Lineas"] = response_label

            self.answersDF_json2[studentID]["respuesta"][self.indx] = response
            self.indx+=1
        else:
            self.indx = 1

        if isMaxSimil:
            self.nota_spacy_experimento[studentID][str(numberOfSentences)] = dict()
            self.nota_spacy_experimento[studentID][str(numberOfSentences)]["MaxSimilitud"] = similarity
            self.nota_spacy_experimento[studentID][str(numberOfSentences)]["Frase"] = response
            self.nota_spacy_experimento[studentID][str(numberOfSentences)]["Lineas"] = response_label

        self.nota_spacy[studentID][minipregunta].append([response, None, None] if response == "" else [response, similarity, response_label])


    def __createDict__(self, nota_spacy:dict(), studentID, minipregunta, type = 0):
        if studentID not in nota_spacy.keys():
            nota_spacy[studentID] = dict()
        if type == 0:
            nota_spacy[studentID][minipregunta]= []
        else:
            nota_spacy[studentID][minipregunta]= dict()
        return nota_spacy

    def plotMSE(self,notas, y, save_file = "Img_MSERealvsCalculatedMarks.png", labelx = "Student studentID", labely = "MSE", title = "MSE Real vs Calculated Marks"):
        

        x = []
        for i in range(len(notas)):
            x.append(i)

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
        plt.savefig(create_file_path(save_file,3))
        plt.cla()

    def plotRealVsCalculatedMark(self, save_file, df, xlabel = "Real", ylabel = "Predicción", title = 'Valor predicho vs valor real'):

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
            plt.scatter(cmpMarks_list[:, 1].astype(np.float32), cmpMarks_list[:, 0].astype(np.float32), edgecolors=(0, 0, 0), alpha = 0.4)
            plt.plot([0.0, 1.0], [0.0, 1.0],
            'k--', color = 'black', lw=2)
            plt.title(title + str(col_name), fontsize = 10, fontweight = "bold")
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.savefig(create_file_path(str(col_name)+save_file,3))
            plt.cla()
            del cmpMarks_list

    def plotHistogram(self, save_file, x):
        ax= sns.histplot(
                data    = x,
                stat    = "count",
                kde     = True,
                color = "black"
            )
        ax.set(xlabel='Deviation', ylabel='Count')

        figure = ax.get_figure()    
        figure.savefig(create_file_path(save_file,3))
        del figure
        ax.cla()

    def saveSimilarityResults(self, settings, similarity_type):
        savePrefix = "Spacy - " if similarity_type == "spacy" else str(settings.modelr) + str(settings.epochr) + " - "
        
        #previous name - "AnalisisSemantico.json"
        save_json(create_file_path(savePrefix + "SimilitudPorConjunto.json",2), self.nota_spacy)
        save_json(create_file_path(savePrefix + "MaxSimilitudPorConjunto.json",2), self.nota_spacy_experimento)
        save_json(create_file_path(savePrefix + "LineaRespuesta.json",2), self.identifyLineofResponse)
        save_json(create_file_path(savePrefix + "RespuestaSeparadaPorFrases.json",2), self.answersDF_json2)
        
        #self.identifyLineofResponse_toexcel
        
        Notasdf = pd.DataFrame()
        for intervaloUmbral in self.notas_calculadas:
            Notasdf[intervaloUmbral] = self.notas_calculadas[intervaloUmbral]
        Notasdf.to_excel(create_file_path(savePrefix +'NotasCalculadas.xlsx',2), sheet_name='notas')


        if settings.isRawExperiment:
            CmpMarksdf = pd.DataFrame()
            CmpMarksdf["Nota Real"] = settings.notas
            self.loge.append(0)
            self.mse.append(0)

            
            for intervalo_umbral in self.notas_calculadas:
                if intervalo_umbral == "ID":
                    continue
                else:
                    self.plotMSE(self.notas_calculadas[intervalo_umbral],settings.notas, str(intervalo_umbral)+'.png')

                    CmpMarksdf[str(intervalo_umbral)] = self.notas_calculadas[intervalo_umbral]
                    self.loge.append(round(mean_squared_log_error(settings.notas[:len(self.notas_calculadas[intervalo_umbral])], self.notas_calculadas[intervalo_umbral]), 4))
                    self.mse.append(round(mean_squared_error(settings.notas[:len(self.notas_calculadas[intervalo_umbral])], self.notas_calculadas[intervalo_umbral]), 4))

                    self.plotHistogram(savePrefix+str(intervalo_umbral) + 'MSE.png', self.plot_mse[intervalo_umbral])
                    self.plotHistogram(savePrefix+str(intervalo_umbral) + 'LOGE.png', self.plot_loge[intervalo_umbral])

                    self.plotHistogram(savePrefix+str(intervalo_umbral) + 'Diferencia.png', self.plot_resta[intervalo_umbral])

                    self.plotMSE(self.plot_mse[intervalo_umbral], [], savePrefix+str(intervalo_umbral) + 'plotMSE.png')
                    self.plotMSE(self.plot_loge[intervalo_umbral], [], savePrefix+str(intervalo_umbral) + 'plotLOGE.png')
                    
            

            self.plotRealVsCalculatedMark(savePrefix+"Ejemplo.png", CmpMarksdf)

            CmpMarksdf.loc[len(settings.notas) + 1]= self.mse
            CmpMarksdf.loc[len(settings.notas) + 2]= self.loge

    def saveSimilarityResultsOld(self, settings, similarity_type):
        
        CmpMarksdf = pd.DataFrame()
        CmpMarksdf["Nota Real"] = settings.notas
        self.loge.append(0)
        self.mse.append(0)

        
        for intervalo_umbral in self.notas_calculadas:
            #print(f'{intervalo_umbral}')
            if intervalo_umbral == "ID":
                continue
            else:
                #print(f'BBBBBBBBBBBB{self.notas_calculadas[intervalo_umbral]}')
                #Descomentar
                """
                self.plotMSE(self.notas_calculadas[intervalo_umbral],settings.notas, str(intervalo_umbral)+'.png')
                """
                fromApi = 1
                if not fromApi:
                    print(str(intervalo_umbral))
                    print("\n\n")
                    print(self.notas_calculadas[intervalo_umbral])
                    print("\n\n")
                    print(settings.notas)
                    print("\n\n")


                    CmpMarksdf[str(intervalo_umbral)] = self.notas_calculadas[intervalo_umbral]
                    self.loge.append(round(mean_squared_log_error(settings.notas[:len(self.notas_calculadas[intervalo_umbral])], self.notas_calculadas[intervalo_umbral]), 4))
                    self.mse.append(round(mean_squared_error(settings.notas[:len(self.notas_calculadas[intervalo_umbral])], self.notas_calculadas[intervalo_umbral]), 4))

                    #Descomentar
                    
                    self.plotHistogram(savePrefix+str(intervalo_umbral) + 'MSE.png', self.plot_mse[intervalo_umbral])
                    self.plotHistogram(savePrefix+str(intervalo_umbral) + 'LOGE.png', self.plot_loge[intervalo_umbral])

                    self.plotHistogram(savePrefix+str(intervalo_umbral) + 'Diferencia.png', self.plot_resta[intervalo_umbral])

                    self.plotMSE(self.plot_mse[intervalo_umbral], [], savePrefix+str(intervalo_umbral) + 'plotMSE.png')
                    self.plotMSE(self.plot_loge[intervalo_umbral], [], savePrefix+str(intervalo_umbral) + 'plotLOGE.png')
                
        
        if not fromApi:
            self.plotRealVsCalculatedMark(savePrefix+"Ejemplo.png", CmpMarksdf)

            CmpMarksdf.loc[len(settings.notas) + 1]= self.mse
            CmpMarksdf.loc[len(settings.notas) + 2]= self.loge


        # Serializing json 
        json_object = json.dumps(self.nota_spacy, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OldApi/OutputFiles2/"+savePrefix+"AnalisisSemantico.json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)


        json_object = json.dumps(self.nota_spacy_experimento, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OldApi/OutputFiles2/"+savePrefix+"ExperimentoSemantica.json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.identifyLineofResponse, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OldApi/OutputFiles2/"+savePrefix+"ExperimentoIdentificarLineaRespuesta.json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)

        #Descomentar
        
        json_object = json.dumps(self.answersDF_json2, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open("OldApi/OutputFiles2/"+savePrefix+"OriginalRespuestaSeparada.json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
        

        df_lineasIdentificadas = pd.DataFrame(self.identifyLineofResponse_toexcel)
        df_lineasIdentificadas.to_excel('OldApi/OutputFiles2/'+savePrefix+'LineaRespuesta2.xlsx', sheet_name='lineas')

        #Descomentar
        
        df3 = pd.DataFrame.from_dict(self.nota_spacy_experimento, orient='index')
        df3.to_excel('OldApi/OutputFiles2/'+savePrefix+'ExperimentoSemantica2.xlsx', sheet_name='notas')

        CmpMarksdf.to_excel('OldApi/OutputFiles2/'+savePrefix+'NotasExperiment.xlsx', sheet_name='notas')
       
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
 
 
