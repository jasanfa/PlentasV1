import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import copy

from OldApi.utils.Semantics.SentenceTransformer2 import *
from codeScripts.utils import create_file_path, clean_words, save_json

#Done

class SemanticOutput():
    """
    Class to store the semantic processing and extract results
    """
    def __init__(self, settings):

        self.nota_spacy = dict()
        self.nota_spacy_experimento = dict()

        self.identifyLineofResponse = dict()
        self.identifyLineofResponse_toexcel = []

        self.notas_calculadas = dict()

        self.min_umbral = []
        self.max_umbral = []
        r= settings.UmbralesSimilitud.split(",")
        for i in r:
            c_w= clean_words(i)
            self.min_umbral.append(float(c_w[0]+'.'+c_w[1]))
            self.max_umbral.append(float(c_w[2]+'.'+c_w[3]))
            self.notas_calculadas['Umbral ' + c_w[0]+'.'+c_w[1] + ' - ' + c_w[2]+'.'+c_w[3]] = []


        #variables taken from the settings
        self.answersDF_json2 = dict()
        self.grpSntncsMde = settings.grpSntncsMde
        self.indiceMinipreguntas = settings.indice_minipreguntas
        self.LofRespThreshold = settings.LofRespThreshold
   
        self.indx = 1
    
    def __createDict__(self, nota_spacy:dict(), studentID, minipregunta, type = 0):
        if studentID not in nota_spacy.keys():
            nota_spacy[studentID] = dict()
        if type == 0:
            nota_spacy[studentID][minipregunta]= []
        else:
            nota_spacy[studentID][minipregunta]= dict()
        return nota_spacy

    def __plotHistogram__(self, save_file, x):
        """
        Generates an histogram of the given data.
        Inputs:
            save_file: The path where the histogram is to be generated.
            x: The data to be represented.
        """
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

    def initInforms(self, studentID, minipregunta):
        """
        This function is for initializing the variables where data is to be stored.
        Inputs:
            studentID: The id of the student
            minipregunta: The minipregunta that is being studied
        """
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

    def updateInformsBucle(self, studentID, minipregunta, response, response_label, numberOfSentences, similarity, isMaxSimil):
        """
        This function is the previous needed step before using updateInforms. Stores the important iterative-generated information
        Inputs:
            -studentID: The id of the student
            -minipregunta: The minipregunta that is being studied
            -response: The student's response
            -response_label: The generated label that indicates the sentence number of the extracted response in the text.
            -numberOfSentences: The number of splitted sentences.
            -similarity: The obtained similarity score.
            -isMaxSimil: If the similarity score is the highest obtained at the moment or not.
        """
        #Storing the similarity score obtained for only one sentence
        if numberOfSentences == 1:
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)] = dict()
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)]["Similitud"] = similarity
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)]["Frase"] = response
            self.identifyLineofResponse[studentID][minipregunta][str(self.indx)]["Lineas"] = response_label

            self.answersDF_json2[studentID]["respuesta"][self.indx] = response
            self.indx+=1
        else:
            self.indx = 1

        #storing the maximum similarity for each set of sentences length
        if isMaxSimil:
            self.nota_spacy_experimento[studentID][str(numberOfSentences)] = dict()
            self.nota_spacy_experimento[studentID][str(numberOfSentences)]["MaxSimilitud"] = similarity
            self.nota_spacy_experimento[studentID][str(numberOfSentences)]["Frase"] = response
            self.nota_spacy_experimento[studentID][str(numberOfSentences)]["Lineas"] = response_label

        #storing the similarity in every case
        self.nota_spacy[studentID][minipregunta].append([response, None, None] if response == "" else [response, similarity, response_label])

    def updateInforms(self, studentID, umbralL, umbralH, calculatedMark, response = ""):
        """
        This function is to store the obtained results from the processing of one response.
        Inputs:
            -studentID: The id of the student
            -umbralL: The fixed low threshold (config json)
            -umbralH: The fixed high threshold (config json)
            -calculatedMark: The calculated mark.
            -response: The student's response
        """

        #storing calculated marks
        self.notas_calculadas['Umbral ' + str(umbralL) + ' - ' + str(umbralH)].append(0 if response == "" else calculatedMark/len(self.indiceMinipreguntas))

        #storing where the model thought the answer was
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
                        if self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"] > max_n and not indx in queue and self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]>self.LofRespThreshold:
                            max_n = self.identifyLineofResponse[studentID][minipregunta][indx]["Similitud"]
                            indx_queue = indx
                    queue.append(indx_queue)
                    highlightedrows = highlightedrows + str(indx_queue) + " "
                    highlightedmarks = highlightedmarks + str(max_n) + " "
                    max_n = -999999
                    indx_queue = 0

                self.identifyLineofResponse_toexcel.append([minipregunta, highlightedrows, highlightedmarks])
                highlightedrows = ""
                highlightedmarks = ""
                queue = []

    def saveSimilarityResults(self, settings, similarity_type):
        """
        Saves the recopiled data in the corresponding format and path differentiating the types of semantic calculation.
        Inputs:
            -settings: system settings.
            -similarity_type: "spacy" if similarity is being calculated from Spacy (if it is not, bert is selected)
        """
        savePrefix = "Spacy - " if similarity_type == "spacy" else str(settings.modelr) + str(settings.epochr) + " - "
        
        #previous name - "AnalisisSemantico.json"
        save_json(create_file_path(savePrefix + "SimilitudPorConjunto.json",2), self.nota_spacy)
        save_json(create_file_path(savePrefix + "MaxSimilitudPorConjunto.json",2), self.nota_spacy_experimento)
        save_json(create_file_path(savePrefix + "LineaRespuesta.json",2), self.identifyLineofResponse)
        save_json(create_file_path(savePrefix + "RespuestaSeparadaPorFrases.json",2), self.answersDF_json2)
        
        
        Notasdf = pd.DataFrame()
        for intervaloUmbral in self.notas_calculadas:
            Notasdf[intervaloUmbral] = self.notas_calculadas[intervaloUmbral]
        Notasdf.to_excel(create_file_path(savePrefix +'NotasCalculadas.xlsx',2), sheet_name='notas')

        self.__plotHistogram__(savePrefix + "HistogramaNotasGeneradas.png", self.notas_calculadas)
    
class SintacticOutput():
    """
    Class to store the sintactic processing
    """
    def __init__(self):
        self.leg_FH =[]
        self.leg_mu = []

    def saveLegibilityResults(self):
        """
        Saves the recopiled data in the corresponding format.
        """
        save_json(create_file_path("FH-Readability.json",2), self.leg_FH, False)
        save_json(create_file_path("mu-Readability.json",2), self.leg_mu, False)

        x = []
        for i in range(len(self.leg_FH)):
            x.append(i)
        plt.figure(figsize=(15,7))
        plt.plot(x, self.leg_FH, label = "FH", color = (0.1,0.1,0.1))
        plt.plot(x, self.leg_mu, '--', label = "mu", color = (0.5,0.5,0.5))
        plt.xlabel("Student")
        plt.ylabel("Legibility (0-100)")
        plt.legend(loc=1)
        plt.title("FH vs mu")
        plt.xticks(rotation=-45)
        plt.grid()
        plt.savefig(create_file_path("Img_FHvsMu.png",3))   
 
class OrtographicOutput():
    """
    Class to store the ortographic processing
    """
    def __init__(self):
        self.notaOrtografia = []
        self.mistakes = []
        self.number_mistakes = []

    def saveOrtographicResults(self):
        save_json(create_file_path("NotasOrtografia.json",2), self.notaOrtografia, False)

