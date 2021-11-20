
import numpy as np
import hunspell
import nltk
import nltk.corpus 
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import ne_chunk
import re
import yake
import spacy
#dic = hunspell.Hunspell('/Users/miguel.r/Desktop/UNIR/PLenTaS/CORPUS/dict_es_ES/es_ES', '/Users/miguel.r/Desktop/es_ES/es_ES.dic')

nlp = spacy.load('es_core_news_sm') # Paquete spaCy en español (es)

# Clase creada para contar sílabas de una palabra (Source: https://github.com/amunozf/separasilabas/blob/master/separasilabas.py)

#class char():
    #def __init__(self):
       # pass
    
class char_line():
    def __init__(self, word):
        self.word = word
        self.char_line = [(char, self.char_type(char)) for char in word]
        self.type_line = ''.join(chartype for char, chartype in self.char_line)
        
    def char_type(self, char):
        if char in set(['a', 'á', 'e', 'é','o', 'ó', 'í', 'ú']):
            return 'V' #strong vowel
        if char in set(['i', 'u', 'ü']):
            return 'v' #week vowel
        if char=='x':
            return 'x'
        if char=='s':
            return 's'
        else:
            return 'c'
            
    def find(self, finder):
        return self.type_line.find(finder)
        
    def split(self, pos, where):
        return char_line(self.word[0:pos+where]), char_line(self.word[pos+where:])
    
    def split_by(self, finder, where):
        split_point = self.find(finder)
        if split_point!=-1:
            chl1, chl2 = self.split(split_point, where)
            return chl1, chl2
        return self, False
     
    def __str__(self):
        return self.word
    
    def __repr__(self):
        return repr(self.word)

class silabizer():
    def __init__(self):
        self.grammar = []
        
    def split(self, chars):
        rules  = [('VV',1), ('cccc',2), ('xcc',1), ('ccx',2), ('csc',2), ('xc',1), ('cc',1), ('vcc',2), ('Vcc',2), ('sc',1), ('cs',1),('Vc',1), ('vc',1), ('Vs',1), ('vs',1)]
        for split_rule, where in rules:
            first, second = chars.split_by(split_rule,where)
            if second:
                if first.type_line in set(['c','s','x','cs']) or second.type_line in set(['c','s','x','cs']):
                    #print 'skip1', first.word, second.word, split_rule, chars.type_line
                    continue
                if first.type_line[-1]=='c' and second.word[0] in set(['l','r']):
                    continue
                if first.word[-1]=='l' and second.word[-1]=='l':
                    continue
                if first.word[-1]=='r' and second.word[-1]=='r':
                    continue
                if first.word[-1]=='c' and second.word[-1]=='h':
                    continue
                return self.split(first)+self.split(second)
        return [chars]
        
    def __call__(self, word):
        return self.split(char_line(word))

# Contador número de frases y palabras empleadas en la respuesta
def check_senteces_words(student_answer):
    
    # Tokenizing into sentences
    sentences=[]
    words=[]
    letter_per_word=[]
    syll=0 # syllables counter
    
    TokenizeAnswer = sent_tokenize(student_answer)
    for token in TokenizeAnswer:
        regex = '\\.'
        token = re.sub(regex , '', token)
        sentences.append(token)
    for i in range(len(sentences)):
        word = sentences[i].split(' ') 
        for j in range(len(word)):
            words.append(word[j])
            syllables = silabizer()
            syll=syll+len(syllables(word[j]))
            letter_per_word.append(len(word[j]))

    sentencesLenght = len(sentences)
    wordsLenght = (len(words))
    #print(f'Number of senteces used in the answer: {sentencesLenght}')
    #print(f'Number of words used in the answer: {wordsLenght}')
    
    return sentencesLenght, wordsLenght, syll, letter_per_word

# Contador faltas de ortografía
def spelling_corrector(student_answer, hunspell_aff = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/es_ES/es_ES' , hunspell_dic = '/Users/javier.sanz/OneDrive - UNIR/Desktop/PLeNTas_V3/es_ES/es_ES.dic' ):

    dic = hunspell.Hunspell(hunspell_aff, hunspell_dic)
    errors=0
    words = student_answer.split(' ')
    wrong_words = ""
    for word in words:
        for element in clean_words(word):            
            if not dic.spell(element):
                #print(f'Spelling mistake: {element}')
                wrong_words= wrong_words + element + " "
                errors+=1        
    #print(f'Spelling mistakes: {errors}')
    return errors,wrong_words
        
# Legibilidad de la respuesta en función del índice Fernández-Huerta
def FHuertas_index(sentencesLenght, wordsLenght, syll):
    FH = 206.84 - 0.60*(syll*100/wordsLenght) - 1.02*(sentencesLenght*100/wordsLenght) 
    FH = round(FH, 3)
    #print(f'\nFernández-Huerta Index: {FH}')
    if 0 < FH <= 30:
        #print('Legibilidad FH: muy difícil.')
        legibilidad_fh = 'muy díficil'
    if 30 < FH <= 50:
        #print('Legibilidad FH: difícil.')  
        legibilidad_fh = 'díficil'
    if 50 < FH <= 60:
        #print('Legibilidad FH: ligeramente difícil.')
        legibilidad_fh = 'ligeramente díficil'
    if 60 < FH <= 70:
        #print('Legibilidad FH: adecuado.')
        legibilidad_fh = 'adecuado'
    if 70 < FH <= 80:
        #print('Legibilidad FH: ligeramente fácil.')
        legibilidad_fh = 'ligeramente fácil'
    if 80 < FH <= 90:
        #print('Legibilidad FH: fácil.')
        legibilidad_fh = 'fácil'
    if 90 < FH <= 100:
        #print('Legibilidad FH: muy fácil.')
        legibilidad_fh = 'muy fácil'
        
    return FH, legibilidad_fh
    
# Legibilidad de la respuesta en función del índice mu
def mu_index(sentencesLenght, wordsLenght, letter_per_word):
    med = np.mean(letter_per_word)
    var = np.var(letter_per_word)
    mu=(wordsLenght/(wordsLenght-1))*(med/var)*100
    mu=round(mu, 3)
    #print(f'\nMu index: {mu}')
    if 0 < mu <= 30:
        #print('Legibilidad Mu: muy difícil.')
        legibilidad_mu = 'muy difícil'
    if 30 < mu <= 50:
        #print('Legibilidad Mu: difícil.')  
        legibilidad_mu = 'difícil'
    if 50 < mu <= 60:
        #print('Legibilidad Mu: ligeramente difícil.')
        legibilidad_mu = 'ligeramente difícil'
    if 60 < mu <= 70:
        #print('Legibilidad Mu: adecuado.')
        legibilidad_mu = 'adecuado'
    if 70 < mu <= 80:
        #print('Legibilidad Mu: ligeramente fácil.')
        legibilidad_mu = 'ligeramente fácil'
    if 80 < mu <= 90:
        #print('Legibilidad Mu: fácil.')
        legibilidad_mu = 'fácil'
    if 90 < mu <= 100:
        #print('Legibilidad Mu: muy fácil.')
        legibilidad_mu = 'muy fácil'
        
    return mu, legibilidad_mu

# Extractor de las kewords de un texto con librería yake
def keyword_extractor(text, numOfKeywords, language, max_ngram_size,deduplication_threshold = 0.9, features=None):
    test_keywords=[]
    # Deleting special characters and set text in lower case
    regex = '\\\n'
    text = re.sub(regex , ' ', text)
    text = text.lower()    
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features= features )
    keywords = custom_kw_extractor.extract_keywords(text)
    for kw in keywords:
        test_keywords.append(kw[0])
    return test_keywords

# categorización de palabras
def word_categorization(student_answer):    
    fileDocument=[]
    TokenizeAnswer = sent_tokenize(student_answer)
    for token in TokenizeAnswer:
        fileDocument.append(token)
    sentencesLenght = len(fileDocument)
    sentence=0
    while sentence < sentencesLenght:      
        # Word Tokenize sentence and Tagging the grammer tag to words (verb, noun, adj, etc...)
        word_tokens = word_tokenize(fileDocument[sentence])
        doc = nlp(fileDocument[sentence])
        pre_chunk = [(w.text, w.pos_) for w in doc]
        #print(pre_chunk)
        sentence += 1
        #pre_chunk = nltk.pos_tag(word_tokens)
        tree = ne_chunk(pre_chunk) # same tagging than before
        #grammer_np = ("NP: {<DT>?<JJ>*<NN>}")
        
        # Chunking rules to filter out:
        grammer_np = ("NP: {<DET>?<ADJ>*<NOUN>*<VERB>}")
        grammar = r"""
          NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and nouns
              {<NNP>+}                # chunk sequences of proper nouns
        """
        chunk_parser = nltk.RegexpParser(grammer_np)
        chunk_result = chunk_parser.parse(tree)

#..................................................................................................
def char_split(word, character):
    palabra1=""
    palabra2=""
    found = 0
    for w in word:
        if w == character and not found:
            found = 1
        else:
            if not found:
              palabra1 = palabra1 + w
            else:
              palabra2 = palabra2 + w

    return [palabra1, palabra2]

def clean_words(string):
    words_sentence = []
    for w in string:
      if not w.isalnum():
        if char_split(string, w)[0] != "":
            words_sentence.append(char_split(string, w)[0])
        string = char_split(string, w)[len(char_split(string, w))-1]

    if string != "":
        words_sentence.append(string)
    return words_sentence
        
        
        