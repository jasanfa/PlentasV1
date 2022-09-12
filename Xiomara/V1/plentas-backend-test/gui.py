import pandas as pd
import re
import json
from sklearn.metrics import mean_squared_error
from utils import silabizer, spelling_corrector
from utils import word_categorization
from utils import mu_index
from utils import FHuertas_index
from utils import check_senteces_words
from  utils import keyword_extractor
import spacy
nlp = spacy.load('es_core_news_sm') # Paquete spaCy en español (es)


import nltk
import nltk.corpus 
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import ne_chunk
from utils import clean_words


import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

class prototipo_GUI(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("GUI_Youtube.ui", self)
        #self.boton_desactivar.setEnabled(False)
        #self.boton_activar.clicked.connect(self.fn_activar)
        #self.boton_desactivar.clicked.connect(self.fn_desactivar)
        self.nivel1.stateChanged.connect(self.checkBoxLevel1)
        self.nivel2.stateChanged.connect(self.checkBoxLevel2)
        self.nivel3.stateChanged.connect(self.checkBoxLevel3)

        self.rb_todas.toggled.connect(self.RadioButtonLineAll)
        self.rb_especificar.toggled.connect(self.RadioButtonLineSpecific)

        self.btn_Start.clicked.connect(self.ButtonStart)

        self.txt_especificar.hide()
        self.window_size.setValue(3)

       

        
    def checkBoxLevel1(self):
        if self.nivel1.isChecked():
            print(f'Calculando el nivel ortográfico de la respuesta')
    def checkBoxLevel2(self):
        if self.nivel2.isChecked():
            print(f'Calculando el nivel sintáctico de la respuesta')
    def checkBoxLevel3(self):
        if self.nivel3.isChecked():
            print(f'Calculando el nivel semántico de la respuesta')

    def RadioButtonLineAll(self):
        if self.rb_todas.isChecked():
            print(f'Se calcula para todas las líneas')
            self.txt_especificar.hide()
      
    def RadioButtonLineSpecific(self):
        if self.rb_especificar.isChecked():
            print(f'Se calcula para ciertas líneas')
            self.txt_especificar.show()

    def ButtonStart(self):
        print(f'Analizando...')
        json_file = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/biConNotaAnon.json' 
        saving_path = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/json_prueba_20oct.json' 
        
        if self.rb_todas.isChecked():
            self.text_display2.setText("Se analizan todas las líneas de la respuesta que se muestra en el primer display")
        #print(f'\n\n{specific_sentence}\n\n')
        # Convert json file into dataframe:
        #df = pd.read_json(json_file)
        with open(json_file, "r", encoding="utf8") as f:
            data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")
        
        df = pd.DataFrame(data)

        output_json=[]
        nota_spacy=[]
        notas=[]
        enunciado = df['metadata'][0]['enunciado']
        prof_keywords = df['metadata'][0]['keywords']
        minipregunta_1 = df['metadata'][0]['minipreguntas'][0]['minipregunta']
        minipregunta_2 = df['metadata'][0]['minipreguntas'][1]['minipregunta']
        minipregunta_3 = df['metadata'][0]['minipreguntas'][2]['minipregunta']
        minipregunta_4 = df['metadata'][0]['minipreguntas'][3]['minipregunta']
        minirespuesta_1 = df['metadata'][0]['minipreguntas'][0]['minirespuesta']
        minirespuesta_2 = df['metadata'][0]['minipreguntas'][1]['minirespuesta']
        minirespuesta_3 = df['metadata'][0]['minipreguntas'][2]['minirespuesta']
        minirespuesta_4 = df['metadata'][0]['minipreguntas'][3]['minirespuesta']
        respuesta_prof = minirespuesta_1 + ' ' + minirespuesta_2 + ' ' + minirespuesta_3 + ' ' + minirespuesta_4
        
        std_ID = self.student_ID.value()
        self.text_display1.setText(df['respuesta'][std_ID])

        #for i in range(len(df['hashed_id'])):
        ID = df['hashed_id'][std_ID]
        respuesta_alumno_raw = df['respuesta'][std_ID] 
        nota_prof = df['nota'][std_ID]
        notas.append(nota_prof)
        if respuesta_alumno_raw == '':
            print('El alumno no ha contestado a la pregunta')
            nota_spacy.append(0)
            student_dict = { 'ID': ID, 'Errores ortograficos': None,
                            'Frases utilizadas para responder a la pregunta': None,
                            'Palabras utilizadas para responder a la pregunta': None,
                            'Index Fernandez Huerta': None, 'Legibilidad F-H': None,
                            'mu index': None, 'Legibilidad Mu': None,
                            'Keywords alumno': None, 'Keyword profesor': None,
                        'Spacy similarity': None, 'Nota profesor': nota_prof}
            self.text_display3.setText('ID: ' + str(ID) + '\n' + 'Respuesta en blanco')            
        else:
            regex = '\\\n'
            respuesta_alumno = re.sub(regex , ' ', respuesta_alumno_raw)
            respuesta_alumno = respuesta_alumno.lower()
            if self.rb_todas.isChecked():
                #print(f'ID alumno: {respuesta_alumno}\n')
                sentencesLenght, wordsLenght, syll, letter_per_word = check_senteces_words(respuesta_alumno)
            else:
                if self.rb_especificar.isChecked():
                        answer_lines = self.txt_especificar.toPlainText().split()
        
                        specific_sentence = []
                        for l in answer_lines:
                            for number in clean_words(l):
                                specific_sentence.append(number)
                        
                        sentences=[]                        
                        TokenizeAnswer = sent_tokenize(respuesta_alumno)
                        for token in TokenizeAnswer:
                            regex = '\\.'
                            token = re.sub(regex , '', token)
                            sentences.append(token)
                        
                        new_respuesta = ""
                        for line in specific_sentence:
                            new_respuesta= new_respuesta + sentences[int(line)-1] + '. '

                        self.text_display2.setText(new_respuesta)
                        respuesta_alumno = new_respuesta
                        sentencesLenght, wordsLenght, syll, letter_per_word = check_senteces_words(respuesta_alumno)
                            

            #Ortografia
            if self.nivel1.isChecked():
                errores = spelling_corrector(respuesta_alumno)
            else:
                errores = None            
            #print(wordsLenght)

            #Sintaxis
            if self.nivel2.isChecked():
                FH, legibilidad_fh = FHuertas_index(sentencesLenght, wordsLenght, syll)
                mu, legibilidad_mu = mu_index(sentencesLenght, wordsLenght, letter_per_word)
            else:
                FH = None
                legibilidad_fh = None
                mu = None
                legibilidad_mu = None

            #Semantica
            if self.nivel3.isChecked():
                student_keywords = keyword_extractor(respuesta_alumno_raw, 5, 'es', self.window_size.value())
                doc1 = nlp(respuesta_alumno)
                doc2 = nlp(respuesta_prof)
                similar = round(doc1.similarity(doc2), 3)
                nota_spacy.append(similar)
            else:
                student_keywords = None
                similar = None
                
            #print(f'\nKeywords Alumno: {student_keywords}')
            #print(f'Keywords Profesor: {prof_keywords}\n')
            #print(f'spaCy similarity: {similar}')
            #print(f'Nota del profesor: {nota_prof}')
            #print('\n-----------------------------------------------------------------------------------------\n')
            student_dict = { 'ID': ID, 'Errores ortograficos': errores,
                            'Frases utilizadas para responder a la pregunta': sentencesLenght,
                            'Palabras utilizadas para responder a la pregunta': wordsLenght,
                            'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                            'mu index': mu, 'Legibilidad Mu': legibilidad_mu,
                            'Keywords alumno': student_keywords, 'Keyword profesor': prof_keywords,
                        'spaCy similarity': similar, 'Nota profesor': nota_prof}
            output_json.append(student_dict)

            display_text = 'ID: ' + str(ID) + '\n' + 'Frases utilizadas para responder a la pregunta: ' + str(sentencesLenght) + '\n' + 'Palabras utilizadas para responder a la pregunta: ' + str(wordsLenght) + '\n'
            if self.nivel1.isChecked():
                display_text = display_text + 'Errores ortograficos: ' + str(errores) + '\n'

            if self.nivel2.isChecked():
                display_text = display_text + 'Index Fernandez Huerta: '+ str(FH) + '\n' + 'Legibilidad F-H: ' + str(legibilidad_fh) + '\n' + 'mu index: ' + str(mu) + '\n' + 'Legibilidad Mu: ' + str(legibilidad_mu) + '\n'

            if self.nivel3.isChecked():
                display_text = display_text + 'Keywords alumno: ' + str(student_keywords) + '\n' + 'Keyword profesor: ' + str(prof_keywords) + '\n' + 'spaCy similarity: ' + str(similar) + '\n'

            display_text = display_text + 'Nota profesor: ' + str(nota_prof)

            self.text_display3.setText(display_text)
        
        #err = round(mean_squared_error(notas, nota_spacy), 4)  
        #print(f'Error cuadrático medio entre la nota del profesor y la obtenida con spacy: {err*100}%')
        # Serializing json 
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        # Writing output to a json file
        with open(saving_path, "w") as outfile:
            outfile.write(json_object)

        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = prototipo_GUI()
    GUI.show()
    sys.exit(app.exec_())
