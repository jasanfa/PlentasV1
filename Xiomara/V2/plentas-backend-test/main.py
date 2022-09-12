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

#nltk.download('punkt')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#python -m spacy download es_core_news_sm


import numpy as np

def main(json_file, saving_path):
    
    json_file = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/biConNotaAnon.json' 
    saving_path = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/json_prueba_20oct.json' 
    
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
    
    for i in range(len(df['hashed_id'])):
        ID = df['hashed_id'][i]
        respuesta_alumno_raw = df['respuesta'][i] 
        nota_prof = df['nota'][i]
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
        else:
            regex = '\\\n'
            respuesta_alumno = re.sub(regex , ' ', respuesta_alumno_raw)
            respuesta_alumno = respuesta_alumno.lower()
            print(f'ID alumno: {ID}\n')
            errores = spelling_corrector(respuesta_alumno)
            sentencesLenght, wordsLenght, syll, letter_per_word = check_senteces_words(respuesta_alumno)
            print(wordsLenght)
            FH, legibilidad_fh = FHuertas_index(sentencesLenght, wordsLenght, syll)
            mu, legibilidad_mu = mu_index(sentencesLenght, wordsLenght, letter_per_word)
            student_keywords = keyword_extractor(respuesta_alumno_raw, 5, 'es', 3)
            doc1 = nlp(respuesta_alumno)
            doc2 = nlp(respuesta_prof)
            similar = round(doc1.similarity(doc2), 3)
            nota_spacy.append(similar)
            print(f'\nKeywords Alumno: {student_keywords}')
            print(f'Keywords Profesor: {prof_keywords}\n')
            print(f'spaCy similarity: {similar}')
            print(f'Nota del profesor: {nota_prof}')
            print('\n-----------------------------------------------------------------------------------------\n')
            student_dict = { 'ID': ID, 'Errores ortograficos': errores,
                            'Frases utilizadas para responder a la pregunta': sentencesLenght,
                            'Palabras utilizadas para responder a la pregunta': wordsLenght,
                            'Index Fernandez Huerta': FH, 'Legibilidad F-H': legibilidad_fh,
                            'mu index': mu, 'Legibilidad Mu': legibilidad_mu,
                            'Keywords alumno': student_keywords, 'Keyword profesor': prof_keywords,
                           'spaCy similarity': similar, 'Nota profesor': nota_prof}
            output_json.append(student_dict)
            
    err = round(mean_squared_error(notas, nota_spacy), 4)  
    print(f'Error cuadrático medio entre la nota del profesor y la obtenida con spacy: {err*100}%')
    # Serializing json 
    json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
    # Writing output to a json file
    with open(saving_path, "w") as outfile:
        outfile.write(json_object)


#json_file = '/Users/miguel.r/Desktop/UNIR/PLenTaS/CORPUS/biConNotaAnon.json' 
#saving_path = '/Users/miguel.r/Desktop/json_prueba_1oct.json'
json_file = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/biConNotaAnon.json' 
saving_path = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/json_prueba_20oct.json'

if __name__ == '__main__':
    main(json_file, saving_path)
    