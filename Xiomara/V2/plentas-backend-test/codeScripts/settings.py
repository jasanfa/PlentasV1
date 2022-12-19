
import pandas as pd
import json

from OldApi.utils.Semantics.SentenceTransformer2 import *
from codeScripts.utils import load_json, create_file_path

class GetSettings():
    """
    This class stores the selected settings for the current experiment
    """
    def __init__(self, config_settings, studentsData):

        #extracting the settings from the configuration document
        self.__getConfigSettings(config_settings)

        #getting the responses to study
        self.__getDatatoStudy(studentsData)


    def __getDatatoStudy(self, data):
        if data[0] == None:
            #extracting the info from the path in the config json         
            self.__getData(self.json_file_in)
        else:
            #extracting the info from the selected file in the api
            self.__getApiData(data)

    def setApiSettings(self, api_settings):
        """
        This function is to overwrite the parameters with the selected values from the api
        Inputs:
            -api_settings: dictionary with the stored parameters from the api
        """
        #transforming string dict into dict
        api_settings = json.loads(api_settings)

        self.PesoOrtografia = api_settings["ortographyPercentage"]
        self.PesoSintaxis = api_settings["syntaxPercentage"]
        self.PesoSemantics = api_settings["semanticPercentage"]
        self.rango_ID = api_settings["students"]     

             
    def __getConfigSettings(self, df):        

        #***self.similarity_type = 0

        self.isRawExperiment = 0  

        #+++ General settings +++

        #path where the dataset is stored
        self.json_file_in = df["ruta_fichero_entrada"]
        #path where output is to be stored
        self.json_file_out = df["ruta_fichero_salida"]

        #path to access hunspell components
        self.hunspell_aff = df["ruta_hunspell"]["aff"]
        self.hunspell_dic = df["ruta_hunspell"]["dic"]

        #range of students to study
        if df["Parametros_Analisis"]["estudiantes"]["Todos"]:
            self.rango_ID = "All"
        else:
            self.rango_ID = df["Parametros_Analisis"]["estudiantes"]["ID_rango"]
        
        #choosing the sentence grouping mode:
        # 0- All sentences 1- Grouping with interval (by defect) 2-Grouping by specific set of sentences
        if int(df["Parametros_Analisis"]["Semantica"]["frases"]["Todos"]) == 1:
            self.grpSntncsMde = 0
        elif int(df["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"])>0:
            self.grpSntncsMde = 1
        else:
            self.grpSntncsMde = 2

        self.minAgrupation = int(df["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"])
        self.maxAgrupation = int(df["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Maximo"] + 1)

        self.SetSentences = df["Parametros_Analisis"]["Semantica"]["frases"]["Set"]

        #+++ Ortography +++

        #If the ortographic level is activated
        self.Ortografia = df["Parametros_Analisis"]["Ortografia"]["Activado"]
        #Max number of permitted errors
        self.NMaxErrores = df["Parametros_Rubrica"]["Ortografia"]["NMaxErrores"]
        #Max number of permitted errors before beginning to substract
        self.FaltasSalvaguarda= df["Parametros_Rubrica"]["Ortografia"]["FaltasSalvaguarda"]
        #Level weight (rubrics)
        self.PesoOrtografia = df["Parametros_Rubrica"]["Ortografia"]["Peso"]

        #+++ Syntax +++
        #if the syntactic level is activated
        self.Sintaxis = df["Parametros_Analisis"]["Sintaxis"]["Activado"]
        #max number of sentences and words permitted
        self.NMaxFrases = df["Parametros_Rubrica"]["Sintaxis"]["NMaxFrases"]
        self.NMaxPalabras= df["Parametros_Rubrica"]["Sintaxis"]["NMaxPalabras"]
        #min readability and FH score
        self.MinFH= df["Parametros_Rubrica"]["Sintaxis"]["FH"]["MinFH"]
        self.MinLegibilidadFH= df["Parametros_Rubrica"]["Sintaxis"]["FH"]["MinLegibilidadFH"]
        self.PesoSntxis_FH = df["Parametros_Rubrica"]["Sintaxis"]["FH"]["Peso"]
        #min readability and Mu score
        self.MinMu= df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["MinMu"]
        self.MinLegibilidadMu= df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["MinLegibilidadMu"]
        self.PesoSntxis_Mu = df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["Peso"]
        #***weight of the level
        self.PesoSintaxis =  0


        #+++ Semantics +++
        #if the semantic level is activated
        self.Semantica = df["Parametros_Analisis"]["Semantica"]["Activado"]
        #***weight of the level
        self.PesoSemantics =  0

        #--- Keyword analysis ---
        #if kw generation is activated 
        self.kwExtractor = 1
        #max number of generated keywords
        self.NMaxKeywords= df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["NMaxKeywords"]
        #max number of words that can be generated
        self.TVentana= df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["TVentana"]
        #deduplication threshold
        self.Deduplication_threshold = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["Deduplication_threshold"]
        #features (generation)
        self.Features = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Generacion"]["Features"]

        #if kw search is to be computed or not
        self.BusquedaKW = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Busqueda"]["Activado"]
        #the weigh of the found number of kws
        self.PesoSmntca_KW = df["Parametros_Rubrica"]["Semantica"]["Keywords"]["Peso"]

        #--- Similarity ---
        #the different thresholds (min-max) to adapt the similarity score 
        self.UmbralesSimilitud= df["Parametros_Rubrica"]["Semantica"]["Similitud"]["UmbralesSimilitud"]
        #the minimun value to select one line of response as similar (0.615 sm - 0.875 md and lg)
        self.LofRespThreshold = 0.615
        #the weight of the level
        self.PesoSmntca_Similitud = df["Parametros_Rubrica"]["Semantica"]["Similitud"]["Peso"]    
        
        #To configure only once the bert model parameters
        self.model_path = "OldApi/Jacobo/Prueba3/Prueba_anterior/Model_bert-base-multilingual-uncased/50_Epochs"        
        self.modelr = 'bert-base-multilingual-uncased'
        self.epochr = 50

        self.BertModels_glbl = SentTransf_test([self.modelr], [self.epochr])

        #Variables to store some values
        self.notas = []
        self.nota_prof = 0
        self.studentID = ""

        #output json format
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

    def __getApiData(self, json_file):
        self.answersDF = pd.DataFrame(json_file[0])
        self.id_number = 0
        
        self.minipreguntas = []
        self.minirespuestas = []
        self.indice_minipreguntas = []
        self.respuesta_prof = ""

        self.enunciado = json_file[1]['enunciado']
        self.prof_keywords = json_file[1]['keywords']

        try:
            i=0
            while True:
                self.minirespuestas.append(json_file[1]['minipreguntas'][i]['minirespuesta'])
                self.minipreguntas.append(json_file[1]['minipreguntas'][i]['minipregunta'])

                self.indice_minipreguntas.append("minipregunta" + str(i))              

                if i == 0:        
                    self.respuesta_prof = self.respuesta_prof + self.minirespuestas[i] 
                else:
                    self.respuesta_prof = self.respuesta_prof + ' ' + self.minirespuestas[i] 
                
                i+=1
        except:
            pass

        info_profesor = []
        for minipregunta, minirespuesta in zip(self.minipreguntas, self.minirespuestas):
            info_profesor.append([minipregunta,minirespuesta])

        save_json(create_file_path("MinirespuestasProfesor.json", 2), info_profesor)

    
    def __getData(self, json_file):

    
        self.answersDF = pd.DataFrame(load_json(json_file))
        #self.answersDF_json = copy.deepcopy(data)
        #self.answersDF_json2 = dict()

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
            pass
            #self.indice_minipreguntas.append("respuesta_completa")

        #self.minirespuestas.append(self.respuesta_prof)

        info_profesor = []
        for minipregunta, minirespuesta in zip(self.minipreguntas, self.minirespuestas):
            info_profesor.append([minipregunta,minirespuesta])

        save_json(create_file_path("MinirespuestasProfesor.json", 2), info_profesor)  