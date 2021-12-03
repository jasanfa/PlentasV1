import pandas as pd
import re
import json
from sklearn.metrics import mean_squared_error
import numpy as np
import os
import statistics

import spacy
nlp = spacy.load('es_core_news_sm')

from utils import silabizer, spelling_corrector, clean_words, sent_tokenize, word_categorization, mu_index, FHuertas_index, check_senteces_words, keyword_extractor,getNameFile
from kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo


class Plentas():
    
    def __init__(self, settings_file):

        self.__getConfigSettings(settings_file)
        self.__getData(self.__json_file_in)

        try:
            os.mkdir('__appcache__')
            self.Pobs, self.Ptrans, self.LemmaDictionary = loadHMMInfo()

            self.KWfile_info = NLP_Questions(self.answersDF,{},{}, self.LemmaDictionary)

            self.IdentifiedKW = NLP_Answers(self.answersDF,self.KWfile_info.Synonyms(), self.KWfile_info.Antonyms(), self.KWfile_info.LemmatizedKeywords(), self.LemmaDictionary, self.Ptrans, self.Pobs, self.KWfile_info.Windows())
            print(f'{getNameFile(self.__json_file_in)}')
            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_Feedback.json", "w")
            json.dump(self.IdentifiedKW.showFeedback(),tf)
            tf.close()

            self.file_feedback = self.IdentifiedKW.showFeedback()

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_Marks.json", "w")
            json.dump(self.IdentifiedKW.showMarks(),tf)
            tf.close()

            self.file_marks = self.IdentifiedKW.showMarks()

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_FeedbackDistribution.json", "w")
            json.dump(self.IdentifiedKW.showFeedbackDistribution(),tf)
            tf.close()

            self.file_feedbackDistrib = self.IdentifiedKW.showFeedbackDistribution()

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_MarksDistribution.json", "w")
            json.dump(self.IdentifiedKW.showKeywordsDistribution(),tf)
            tf.close()

            self.file_marksDistrib = self.IdentifiedKW.showKeywordsDistribution()
            
        except:
           
            print(f'{"Archivo ya existe"}')

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_Marks.json", "r")
            self.file_marks = json.load(tf)
            tf.close()

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_Feedback.json", "r")
            self.file_feedback = json.load(tf)
            tf.close()

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_MarksDistribution.json", "r")
            self.file_marksDistrib = json.load(tf)
            tf.close()

            tf = open("__appcache__/" + getNameFile(self.__json_file_in) + "_FeedbackDistribution.json", "r")
            self.file_feedbackDistrib = json.load(tf)
            tf.close()            
        


   
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

        self.NMaxKeywords= df["Parametros_Analisis"]["Semantica"]["Keywords"]["NMaxKeywords"]
        self.TVentana= df["Parametros_Analisis"]["Semantica"]["Keywords"]["TVentana"]
        self.Deduplication_threshold = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Deduplication_threshold"]
        self.Features = df["Parametros_Analisis"]["Semantica"]["Keywords"]["Features"]
        self.MinSpacySimilar= df["Parametros_Rubrica"]["Semantica"]["Similitud"]["MinSpacySimilar"]

        self.FaltasSalvaguarda= df["Parametros_Rubrica"]["Ortografia"]["FaltasSalvaguarda"]

        self.PesoOrtografia = df["Parametros_Rubrica"]["Ortografia"]["Peso"]

        self.PesoSntxis_FH = df["Parametros_Rubrica"]["Sintaxis"]["FH"]["Peso"]
        self.PesoSntxis_Mu = df["Parametros_Rubrica"]["Sintaxis"]["Mu"]["Peso"]

        self.PesoSmntca_KW = df["Parametros_Rubrica"]["Semantica"]["Keywords"]["Peso"]
        self.PesoSmntca_Similitud = df["Parametros_Rubrica"]["Semantica"]["Similitud"]["Peso"]




    def __getData(self, json_file):

        #json_file = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/biConNotaAnon.json' 
        with open(json_file, "r", encoding="utf8") as f:
            data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")

        self.answersDF = data        
        df = pd.DataFrame(data)
        self.minipreguntas = []
        self.minirespuestas = []
        self.respuesta_prof = ""

        self.enunciado = df['metadata'][0]['enunciado']
        self.prof_keywords = df['metadata'][0]['keywords']

        for i in range(4):
            self.minirespuestas.append(df['metadata'][0]['minipreguntas'][i]['minirespuesta'])
            self.minipreguntas.append(df['metadata'][0]['minipreguntas'][i]['minipregunta'])

            if i == 3:        
                self.respuesta_prof = self.respuesta_prof + self.minirespuestas[i] 
            else:
                self.respuesta_prof = self.respuesta_prof + self.minirespuestas[i] + ' '


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
            
        notas=[]
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

            nota_spacy[ID] = dict()
            nota_spacy_reducido[ID] = dict()

            if respuesta_alumno_raw == '':
                #print('El alumno no ha contestado a la pregunta')                
                for a in range(5):
                    if a == 4:
                        nota_spacy[ID]["respuesta_completa"]= [0]
                    else:
                        nota_spacy[ID]["minipregunta" + str(a)] = [0]


                        

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

                if self.Semantica:

                    for minirespuesta, indx in zip(self.minirespuestas, range(5)):

                        if indx == 4:
                            nota_spacy[ID]["respuesta_completa"]= []
                            nota_spacy_reducido["respuesta_completa"]= []
                        else:
                            nota_spacy[ID]["minipregunta" + str(indx)] = [] 
                            nota_spacy_reducido[ID]["minipregunta" + str(indx)] = []                       
 
                        if self.setFrases == 0:
                            student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno_raw, minirespuesta)

                            if indx == 4:
                                nota_spacy[ID]["respuesta_completa"].append(["All lines", student_keywords, similar])
                            else:
                                nota_spacy[ID]["minipregunta" + str(indx)].append(["All lines", student_keywords, similar])

                        else:           
                        
                            sentences=[]                        
                            TokenizeAnswer = sent_tokenize(respuesta_alumno)
                            for token in TokenizeAnswer:
                                regex = '\\.'
                                token = re.sub(regex , '', token)
                                sentences.append(token)

                            if self.setFrases == 1:

                                for number in list(range(int(self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"]),int(self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Maximo"] + 1))):
                                    print(f'\n\n\n\n{sentences}\n\n')                            
                                    for s in range(len(sentences)):
                                        print(f'{s} {number} {len(sentences)}')
                                        new_respuesta = ""

                                        try:                                       
                                            breaking_variable = sentences[s+number-1]
                                            for line in sentences[s:s+number]:
                                                new_respuesta= new_respuesta + line + '. '
                                                
                                            respuesta_alumno = new_respuesta.lower()
                                            print(f'+++++++++++++++++++++++++++++++++++++++++++++++')
                                            print(f'Esto es lo que quiero\n {respuesta_alumno}')
                                            respuesta_alumno = respuesta_alumno.lower()
                                            student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno, minirespuesta)

                                            if number == 1:
                                                r_name = "Line " + str(s+1)
                                                
                                            else:                                                
                                                r_name = "Lines " + str(s+1) + " - " + str(s+number)

                                            if indx == 4:
                                                nota_spacy[ID]["respuesta_completa"].append([r_name, student_keywords, similar])
                                            else:
                                                nota_spacy[ID]["minipregunta" + str(indx)].append([r_name, student_keywords, similar])

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
                                print(f'{sentences}\n\n')
                                print(f'{respuesta_alumno}')
                                student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno, minirespuesta)

                                if indx == 4:
                                    nota_spacy[ID]["respuesta_completa"].append([r_name, student_keywords, similar])
                                else:
                                    nota_spacy[ID]["minipregunta" + str(indx)].append([r_name, student_keywords, similar])


                #print(f'{semantica_output}')
                #print(f'{notas}\n\n\n{nota_spacy}\n\n\n{len(notas)} \n\n\n{len(nota_spacy)}')

                #notaSpacy = statistics.mean(nota_spacy)
                
                notaSpacy = 0
                esSuperior = 0
                

                for pregunta in nota_spacy[ID]:
                    nota_spacy_reducido[ID][pregunta] = []
                    for info in nota_spacy[ID][pregunta]:
                        print(f'{info[2]}\n\n')
                        try:
                            if info[2] > self.MinSpacySimilar:
                                esSuperior = 1
                                nota_spacy_reducido[ID][pregunta].append(info)                           
                                
                        except:
                            continue 
                    if esSuperior: 
                        notaSpacy +=1
                    esSuperior = 0   


                err = round(mean_squared_error(notas, [notaSpacy/4]), 4) 
                print(f'error {err} nota {notas} notaspacy{notaSpacy/4} \n') 
                #print(f'Error cuadrático medio entre la nota del profesor y la obtenida con spacy: {err*100}%')


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
                
                student_dict = { 'ID': ID, 'Errores ortograficos': [errores, mistakes], 'Nota en Ortografía': nota_Ortografia,
                                'Frases utilizadas para responder a la pregunta': sentencesLenght,
                                'Palabras utilizadas para responder a la pregunta': wordsLenght,
                                'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                                'mu index': mu, 'Legibilidad Mu': legibilidad_mu,'Nota en Sintaxis': nota_Sintaxis,
                                'Análisis por frase': nota_spacy_reducido[ID],'Keywords alumno': self.file_marks[ID], 'Keyword profesor': self.prof_keywords, 'Justificación de esos keywords': self.file_feedback[ID], 'Nota en Semantica': nota_Semantica, 'Nota profesor': nota_prof}

                student_dict = { 'ID': ID,
                'Ortografia': {              
                        'Errores ortograficos': [errores, mistakes], 'Nota en Ortografía': nota_Ortografia},
                'Sintaxis': {
                    'Frases utilizadas para responder a la pregunta': sentencesLenght,
                    'Palabras utilizadas para responder a la pregunta': wordsLenght,
                    'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                    'mu index': mu, 'Legibilidad Mu': legibilidad_mu,'Nota en Sintaxis': nota_Sintaxis},
                'Semantica':{
                    'Keywords alumno (auto)': nota_spacy_reducido[ID],'Keywords alumno': self.file_marks[ID], 'Keyword profesor': self.prof_keywords, 'Justificación de esos keywords': self.file_feedback[ID], 'Nota en Semantica': nota_Semantica, 'Nota profesor': nota_prof}}

                output_json.append(student_dict)
                #nota_spacy = []
                notas = []            

        if self.Semantica:
            # Serializing json 
            json_object = json.dumps(nota_spacy, indent = 11, ensure_ascii= False) 
            # Writing output to a json file
            with open("AnalisisSemantico.json", "w") as outfile:
                outfile.write(json_object)

            json_object = json.dumps(nota_spacy_reducido, indent = 11, ensure_ascii= False) 
            # Writing output to a json file
            with open("AnalisisSemanticoReducido.json", "w") as outfile:
                outfile.write(json_object)

        # Serializing json 
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open(self.__json_file_out, "w") as outfile:
            outfile.write(json_object)
        
        return json_object

        