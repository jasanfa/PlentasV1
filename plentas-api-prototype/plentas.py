import pandas as pd
import re
import json
from sklearn.metrics import mean_squared_error
import numpy as np
import os
import statistics

import spacy
nlp = spacy.load('es_core_news_sm')

from utils import silabizer, spelling_corrector, clean_words, sent_tokenize, word_categorization, mu_index, FHuertas_index, check_senteces_words, keyword_extractor
from kwIdentificator import NLP_Answers, NLP_Questions, loadHMMInfo


class Plentas():
    
    def __init__(self, settings_file):

        self.__getConfigSettings(settings_file)
        self.__getData(self.__json_file_in)

        try:
            os.mkdir('dir1')
            self.Pobs, self.Ptrans, self.LemmaDictionary = loadHMMInfo()

            self.KWfile_info = NLP_Questions(self.answersDF,{},{}, self.LemmaDictionary)

            self.IdentifiedKW = NLP_Answers(self.answersDF,self.KWfile_info.Synonyms(), self.KWfile_info.Antonyms(), self.KWfile_info.LemmatizedKeywords(), self.LemmaDictionary, self.Ptrans, self.Pobs, self.KWfile_info.Windows())

            tf = open("dir1/Feedback.json", "w")
            json.dump(self.IdentifiedKW.showFeedback(),tf)
            tf.close()

            self.file_feedback = self.IdentifiedKW.showFeedback()

            tf = open("dir1/Marks.json", "w")
            json.dump(self.IdentifiedKW.showMarks(),tf)
            tf.close()

            self.file_marks = self.IdentifiedKW.showMarks()

            tf = open("dir1/FeedbackDistribution.json", "w")
            json.dump(self.IdentifiedKW.showFeedbackDistribution(),tf)
            tf.close()

            self.file_feedbackDistrib = self.IdentifiedKW.showFeedbackDistribution()

            tf = open("dir1/MarksDistribution.json", "w")
            json.dump(self.IdentifiedKW.showKeywordsDistribution(),tf)
            tf.close()

            self.file_marksDistrib = self.IdentifiedKW.showKeywordsDistribution()
            
        except:
           
            print(f'{"Archivo ya existe"}')
            tf = open("dir1/Marks.json", "r")
            self.file_marks = json.load(tf)
            tf.close()

            tf = open("dir1/Feedback.json", "r")
            self.file_feedback = json.load(tf)
            tf.close()

            tf = open("dir1/MarksDistribution.json", "r")
            self.file_marksDistrib = json.load(tf)
            tf.close()

            tf = open("dir1/FeedbackDistribution.json", "r")
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

        self.enunciado = df['metadata'][0]['enunciado']
        self.prof_keywords = df['metadata'][0]['keywords']
        self.minipregunta_1 = df['metadata'][0]['minipreguntas'][0]['minipregunta']
        self.minipregunta_2 = df['metadata'][0]['minipreguntas'][1]['minipregunta']
        self.minipregunta_3 = df['metadata'][0]['minipreguntas'][2]['minipregunta']
        self.minipregunta_4 = df['metadata'][0]['minipreguntas'][3]['minipregunta']
        self.minirespuesta_1 = df['metadata'][0]['minipreguntas'][0]['minirespuesta']
        self.minirespuesta_2 = df['metadata'][0]['minipreguntas'][1]['minirespuesta']
        self.minirespuesta_3 = df['metadata'][0]['minipreguntas'][2]['minirespuesta']
        self.minirespuesta_4 = df['metadata'][0]['minipreguntas'][3]['minirespuesta']
        self.respuesta_prof = self.minirespuesta_1 + ' ' + self.minirespuesta_2 + ' ' + self.minirespuesta_3 + ' ' + self.minirespuesta_4




    def __ApplySemanticFunctions(self, respuesta_alumno):
        if self.Features.lower() == "none":
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.NMaxKeywords), 'es', int(self.TVentana), float(self.Deduplication_threshold), None)
        else:
            stdnt_kw = keyword_extractor(respuesta_alumno, int(self.NMaxKeywords), 'es', int(self.TVentana), float(self.Deduplication_threshold), self.Features)

        doc1 = nlp(respuesta_alumno)
        doc2 = nlp(self.respuesta_prof)
        similar = round(doc1.similarity(doc2), 3)

        return [stdnt_kw, similar]


    def processData(self):
        output_json=[]
        nota_spacy=[]
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

        for i in IDs:
            ID = df['hashed_id'][i]
            respuesta_alumno_raw = df['respuesta'][i] 
            nota_prof = df['nota'][i]
            notas.append(nota_prof)

            if respuesta_alumno_raw == '':
                #print('El alumno no ha contestado a la pregunta')
                nota_spacy.append(0)
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
                    semantica_output = []
                    if self.setFrases == 0:
                        student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno_raw)
                        nota_spacy.append(similar)
                        semantica_output.append(["All lines", student_keywords, similar])

                    else:           
                       
                        sentences=[]                        
                        TokenizeAnswer = sent_tokenize(respuesta_alumno)
                        for token in TokenizeAnswer:
                            regex = '\\.'
                            token = re.sub(regex , '', token)
                            sentences.append(token)

                        if self.setFrases == 1:

                            for i in list(range(int(self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Minimo"]),int(self.configDf["Parametros_Analisis"]["Semantica"]["frases"]["Agrupacion"]["Maximo"] + 1))):
                                #print(f'\n\n\n\n{sentences}\n\n')                            
                                for s in range(len(sentences)):
                                    #print(f'{s} {i} {len(sentences)}')
                                    new_respuesta = ""

                                    try:                                       
                                        breaking_variable = sentences[s+i-1]
                                        for line in sentences[s:s+i]:
                                            new_respuesta= new_respuesta + line + '. '
                                            
                                        respuesta_alumno = new_respuesta.lower()
                                        #print(f'+++++++++++++++++++++++++++++++++++++++++++++++')
                                        #print(f'Esto es lo que quiero\n {respuesta_alumno}')
                                        respuesta_alumno = respuesta_alumno.lower()
                                        student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno)
                                        r_name = "Lines " + str(s) + " - " + str(s+i)
                                        nota_spacy.append(similar)
                                        semantica_output.append([r_name, student_keywords, similar])
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

                                new_respuesta= new_respuesta + sentences[int(line)-1] + '. '
                                r_name = r_name + str(int(line)) + " "

                            respuesta_alumno = new_respuesta.lower()
                            student_keywords, similar = self.__ApplySemanticFunctions(respuesta_alumno)
                            nota_spacy.append(similar)
                            
                            semantica_output.append([r_name, student_keywords, similar])

                #print(f'{semantica_output}')
                #print(f'{notas}\n\n\n{nota_spacy}\n\n\n{len(notas)} \n\n\n{len(nota_spacy)}')

                mean_notaSpacy = statistics.mean(nota_spacy)
                err = round(mean_squared_error(notas, [mean_notaSpacy]), 4) 
                print(f'{err}\n\n\n{notas}\n\n\n{mean_notaSpacy}') 
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
                
                nota_Semantica = self.PesoSmntca_Similitud * (1-err) + self.PesoSmntca_KW * float(re.sub("Nota: ","",self.file_marks[ID][1]))

                nota_Sintaxis = self.PesoSntxis_FH * FH/100 + self.PesoSntxis_Mu * mu/100
                
                #print(f'AAAAAAAAAAA\n\n{self.IdentifiedKW.showMarks()}\n\n')
                
                student_dict = { 'ID': ID, 'Errores ortograficos': [errores, mistakes], 'Nota en Ortografía': nota_Ortografia,
                                'Frases utilizadas para responder a la pregunta': sentencesLenght,
                                'Palabras utilizadas para responder a la pregunta': wordsLenght,
                                'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                                'mu index': mu, 'Legibilidad Mu': legibilidad_mu,'Nota en Sintaxis': nota_Sintaxis,
                                'Keywords alumno (auto)': semantica_output,'Keywords alumno': self.file_marks[ID], 'Keyword profesor': self.prof_keywords, 'Justificación de esos keywords': self.file_feedback[ID], 'Nota en Semantica': nota_Semantica, 'Nota profesor': nota_prof}

                output_json.append(student_dict)
                nota_spacy = []
                notas = []            

        

        # Serializing json 
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open(self.__json_file_out, "w") as outfile:
            outfile.write(json_object)
        
        return json_object

        