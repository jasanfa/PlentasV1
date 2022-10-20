import stanza
import nltk
from nltk.corpus import stopwords
import string
OTHER_WORDS = ["''", '--', '``']

import requests
from bs4 import BeautifulSoup

import json
import numpy as np
import pandas as pd
import re



def loadHMMInfo():
    #Loading HMM probability tables
    Pobs_aux= pd.read_excel(open('__appcache__/Total_Emission.xlsx', 'rb'))
    Ptrans_aux= pd.read_excel(open('__appcache__/Total_Transmision.xlsx', 'rb'))
    Pobs=Pobs_aux
    Pobs = Pobs.set_index('Unnamed: 0')
    Pobs.index.names = [None]
    Ptrans=Ptrans_aux
    Ptrans = Ptrans.set_index('Unnamed: 0')
    Ptrans.index.names = [None]

    #Loading the dictionary of lemmas
    LemmaDictionary = np.load('__appcache__/DiccionarioLemas.npy', allow_pickle='TRUE')
    LemmaDictionary = LemmaDictionary.item()

    return Pobs, Ptrans, LemmaDictionary

def saveKWInfo(file_name, showFdbck, showMarks,showFdbckDis, showMarksDis):

    print(f'{file_name}')
    tf = open("__appcache__/" + file_name + "_Feedback.json", "w")
    json.dump(showFdbck,tf)
    tf.close()

    tf = open("__appcache__/" + file_name + "_Marks.json", "w")
    json.dump(showMarks,tf)
    tf.close()

    tf = open("__appcache__/" + file_name + "_FeedbackDistribution.json", "w")
    json.dump(showFdbckDis,tf)
    tf.close()

    tf = open("__appcache__/" + file_name + "_MarksDistribution.json", "w")
    json.dump(showMarksDis,tf)
    tf.close()

def loadKWInfo(file_name):
        print(f'{"Archivo ya existe"}')

        tf = open("__appcache__/" + file_name + "_Marks.json", "r")
        file_marks = json.load(tf)
        tf.close()

        tf = open("__appcache__/" + file_name + "_Feedback.json", "r")
        file_feedback = json.load(tf)
        tf.close()

        tf = open("__appcache__/" + file_name + "_MarksDistribution.json", "r")
        file_marksDistrib = json.load(tf)
        tf.close()

        tf = open("__appcache__/" + file_name + "_FeedbackDistribution.json", "r")
        file_feedbackDistrib = json.load(tf)
        tf.close()

        return file_marks, file_feedback, file_marksDistrib, file_feedbackDistrib 




#LemmaDictionary = np.load('DiccionarioLemas.npy', allow_pickle='TRUE')
#LemmaDictionary = LemmaDictionary.item()

class Viterbi:
    '''
    Viterbi algorithm to decode HMM information. 
    '''

    def __init__(self, PTrans: pd.DataFrame(), PObs: pd.DataFrame(), DictLemmas: dict(), sentence: str):
        """
        Class constructor. 
        Parameters:
        -PTrans: The transition table of probabilities
        -PObs: The emission table of probabilities
        -DictLemmas: The dictionary of lemmas
        -sentence: The sentence that is wanted to decode 
        """
        self._q0 = 'q0'
        self._qF = 'qF'
        self.state_dictionary = {"A":"Adjective", "D":"Determiner", "N":"Noun", "V":"Verb", "P":"Pronoun", "R":"Adverb", "C":"Conjunction", "S":"Adposition", "W":"Date", "Z":"Number", "I":"Interjection", "F":"Punctuation"}
        self._sentence = sentence
        self._dictLemmas = DictLemmas
        self._PObs= PObs
        self._PTrans = PTrans

        self._relevant_states = None
        self._prob_viterbi = pd.DataFrame()
        self._previous_max_state = None
        self._tokens_list = dict()

        self.TaggedSentence = self.__OptimalDecoding() 

    """
    Public methods
    """
    
    def ViterbiProbability(self):
        """
        Returns the probability matrix of Viterbi
        """
        return self._prob_viterbi
    
    def SyntacticAnalysis(self):
        """
        Returns a list with each token of the morphosyntactically tagged sentence (token, tag)
        """
        return self.TaggedSentence

    """
    Private methods
    """

    def __truncate(self,num,n):
        """
        It truncates the value of a float number
        """
        temp = str(num)
        for x in range(len(temp)):
            if temp[x] == '.':
                try:
                    return float(temp[:x+n+1])
                except:
                    return float(temp)      
        return float(temp)

    def __RelevantStates(self):
        """
        Gets the relevant states (the name of the grammatical categories)
        """
        self._relevant_states = set()
        for category in self.state_dictionary.keys():
          self._relevant_states.add(self.state_dictionary[category])

    def __Probabilities(self):
        """
        Calculates the probability matrix of Viterbi
        """
        if len(self._prob_viterbi) != 0:
            return self._prob_viterbi.copy()

        if not self._relevant_states:
            self.__RelevantStates()

        relevant_states = self._relevant_states

        #Matrix in which the Viterbi values ​​are stored
        viterbi_matrix = {q: dict() for q in relevant_states}

        #Matrix in which it is stored the state of origin that maximizes each probability
        self._previous_max_state = {q: dict() for q in relevant_states}

        q0 = self._q0
        prob_trans = self._PTrans
        prob_obs = self._PObs
        previous_token = None

        #Penalty for classes differing from noun or adjective
        penalty = 0.000001

        #Handles word repetition cases and word counting (frequency)
        for token in [x.lower() for x in self._sentence.split()]:
          if token in self._tokens_list.keys():
            i=2
            newToken=0
            while not newToken:
                if (token+"("+str(i)+")") in self._tokens_list.keys():
                  i = i + 1
                else:
                  try:
                    isNewToken = self._dictLemmas[token]
                    self._tokens_list[token+"("+str(i)+")"] = token
                    newToken=1
                  except:
                    self._tokens_list[token+"("+str(i)+")"]= "tokenseliminados"
                    newToken=1

          else:
            try:
              isNewToken = self._dictLemmas[token]
              self._tokens_list[token]= token
            except:
              self._tokens_list[token]= "tokenseliminados"

        #Creates the Vierbi Matrix
        for token in self._tokens_list:
            for qDestiny in relevant_states:

                prob_max = 0
                if not previous_token:
                    #q0
                    prob_max = prob_trans[qDestiny][q0]
                    
                else:
                    #Rest of the states
                    for qOrigin in relevant_states:

                        prob_qOrigin = viterbi_matrix[qOrigin][previous_token] * prob_trans[qDestiny][qOrigin]

                        if prob_qOrigin > prob_max:
                            prob_max = prob_qOrigin

                #Handles the words that are not included in the dictionary of lemmas
                if self._tokens_list[token] == "tokenseliminados":
                    if qDestiny == "Noun" or qDestiny == "Adjective":
                      viterbi_matrix[qDestiny][token] = prob_max * prob_obs[self._tokens_list[token]][qDestiny]
                    else:
                      viterbi_matrix[qDestiny][token] = prob_max * prob_obs[self._tokens_list[token]][qDestiny] * penalty                    
                else:
                    viterbi_matrix[qDestiny][token] = prob_max * prob_obs[self._tokens_list[token]][qDestiny]

            previous_token = token


        self._prob_viterbi = pd.DataFrame.from_dict(viterbi_matrix, orient='index')

        return self._prob_viterbi.copy()

    def __OptimalDecoding(self):
        """
        It decodes the information previously calculated in order to get the best path in the Viterbi matrix 
        """

        prob_viterbi = self.__Probabilities()
        reverse_sentence = [x.lower() for x in self._tokens_list]
        reverse_sentence.reverse()     
        tagged_sentence = []

        #Last word of the sentence
        _word = reverse_sentence[0]
        tag = prob_viterbi[_word].idxmax()
        tagged_sentence.append({'token': _word, 'tag': tag, 'prob': prob_viterbi[_word].max()})

        #Rest of the words
        previous_word = _word
        prob_obs = self._PObs
        prob_trans = self._PTrans

        aux_state = tag
        for _word in reverse_sentence[1:]:            

            for state in self._relevant_states:                
                if  self.__truncate(prob_viterbi[previous_word][tag],6) == self.__truncate(prob_viterbi[_word][state] * prob_obs[self._tokens_list[previous_word]][tag] * prob_trans[tag][state],6):
                    aux_state = state
                    break
                  
            tag = aux_state
            tagged_sentence.append({'token': _word, 'tag': tag, 'prob': prob_viterbi[_word][tag]}) 
            previous_word = _word  


        #Getting the real order of the tokens
        tagged_sentence.reverse()


        return tagged_sentence




















class NLP_Questions:
    """
    Extracts the needed information to process the student's answers and creates the synonym and antonym dictionaries
    """

    def __init__(self, file_name: list(), synonym_dict: dict(), antonym_dict: dict(), LemmaDictionary:dict() ):
        """
        Class constructor. 
        Parameters:
        -file_name: The path of the file where the information is stored
        -synonym_dict: The dictionary of synonyms 
        -antonym_dict: The dictionary of antonyms
        -LemmaDictionary: The dictionary of lemmas
        """        
        self.synonyms = synonym_dict
        self.antonyms = antonym_dict
        self.stopwords = set(stopwords.words('spanish'))
        self.LemmaDictionary = LemmaDictionary

        

        self.file = file_name

        self.keywords = self.__GetKeywords()
        self.tokenizedKeywords = None
        self.lemmatizedKeywords = []

        self.nlp = stanza.Pipeline(lang='es', processors='tokenize,mwt,pos,lemma')

        self.__ProcessInfo()  
        self.windowMaxSize = self.__GetWindowSizes()

    """
    Public methods
    """     

    def Keywords(self):
        """
        Returns the keyword dictionary with its lemma
        """
        return self.tokenizedKeywords

    def LemmatizedKeywords(self):
        """
        Returns a list with the lemma of each keyword
        """
        return self.lemmatizedKeywords
 
    
    def Synonyms(self):
        """
        Returns the dictionary of synonyms
        """
        return self.synonyms

    def Antonyms(self):
        """
        Returns the dictionary of antonyms
        """
        return self.antonyms
    
    def Windows(self):
        """
        Returns each window size to identify the keyword
        """      
        return self.windowMaxSize

    def SaveDictionaries(self, path=""):
        """
        Saves all the interesting information.
        Parameters:
        -path: The path where you want to save the files
        """   

        tf = open(path+"DiccionarioSinonimos.json", "w")
        json.dump(self.synonyms,tf)
        tf.close()

        tf = open(path+"DiccionarioAntonimos.json", "w")
        json.dump(self.antonyms,tf)
        tf.close()

        tf = open(path+"TokenizedKeywords.json", "w")
        json.dump(self.tokenizedKeywords,tf)
        tf.close()

        tf = open(path+"LemmatizedKeywords.json", "w")
        json.dump(self.lemmatizedKeywords,tf)
        tf.close()

        tf = open(path+"WindowMaxSize.json", "w")
        json.dump(self.windowMaxSize,tf)
        tf.close()

    
    """
    Private methods
    """

    
    def __GetKeywords(self):
        """
        Gets all the keywords 
        """
        print(f'AAAA{self.file}')
        print(f'\n tipo {type(self.file)}\n')
        keywords_list = []
        for answer in self.file:
            print(f'BBB{answer}')
            for section in answer:
                print(f'CCC{section}')
                if section == "metadata":
                    for element in answer[section]:
                        if element == "keywords":
                            for keyword in answer[section][element]:
                                if keyword in keywords_list:
                                    continue
                                else:
                                    keywords_list.append(keyword)

        print(f'Lista de keywords: {keywords_list}\n')

        return keywords_list

    def __Lemmatization(self, word):
        """
        Allows to transform a word into its lemma.
        Parameters:
        -word: The word that you want to lemmatize
        """
        try:
            lemma_aux = self.LemmaDictionary[word]
            #words from the dictionary of lemmas that don't need WSD
            if len(lemma_aux)==1 and word not in self.stopwords:
                for gcategory in lemma_aux:
                    lemma = lemma_aux[gcategory]

            else:
                #words from the dictionary of lemmas that need WSD
                doc = self.nlp(word)
                lemma = doc.sentences[0].words[0].lemma

        except:
                #words that are not included in the dictionary of lemmas
                doc = self.nlp(word)
                lemma = doc.sentences[0].words[0].lemma
        
        return lemma 

    def __createExpression(self,expression,word):
        """
        Creates a way to concatenate words.
        Parameters:
        -expression: the string whre you want to concatenate words
        -word: the word you want to add in the expression
        """     

        if expression == "":
            expression = word
        else:
            expression = expression + " " + word

        return expression

    def __GetWindowSizes(self):
        """
        Creates a way to concatenate words
        """ 
        list_all = []
        list_keys = []
        list_syn = []
        list_ant = []
        
        for keyword in self.lemmatizedKeywords:
            #Getting the windows of the keywords 
            length = len(keyword.split())
            if not length in list_keys:
                list_keys.append(length)

            #Getting the windows of the antonyms 
            if len(keyword.split()) == 1:
                for component in self.antonyms[keyword]["Dictionary"]:
                    for category in self.antonyms[keyword]["Dictionary"][component]:
                        for element in self.antonyms[keyword]["Dictionary"][component][category]:                                    
                            length3 = len(element.split())
                            if not length3 in list_ant:
                                list_ant.append(length3)
            
            #Getting the windows of the synonyms 
            for word in keyword.split():
                if word in self.stopwords:
                    continue
                else:
                    word_l = self.__Lemmatization(word)
                    for component in self.antonyms[word_l]["Dictionary"]:
                        for category in self.antonyms[word_l]["Dictionary"][component]:                 
  
                            if len(keyword.split()) > 1:
                                for element in self.synonyms[word_l]["Dictionary"][component][category]:                                    
                                    length2 = len(element.split())
                                    if not length2 in list_syn:
                                        list_syn.append(length2)
                            else:
                                for element in self.synonyms[keyword]["Dictionary"][component][category]:
                                    length2 = len(element.split())
                                    if not length2 in list_syn:
                                        list_syn.append(length2)
        list_keys.sort()
        list_syn.sort()
        list_ant.sort()

        list_all = [list_keys, list_syn, list_ant]
        print(f'Lista de todo {list_all}\n')
        return list_all

    def __TokenizeKeywords(self):
        """
        Processes the keywords in order to tokenize and lemmatize them
        """ 
        tokenizedKeywords = dict()
        for keyword in self.keywords:
            #Compund keywords
            if  len(keyword.split()) > 1:
                splittedKeyword = keyword.split()
                keylist = []
                keyword_buffer =""
                for word in splittedKeyword:
                    keylist.append(self.__Lemmatization(word))
                    if keyword_buffer == "":
                        keyword_buffer = self.__Lemmatization(word)
                    else:
                        keyword_buffer = keyword_buffer + " " + self.__Lemmatization(word)

                tokenizedKeywords[keyword] = keylist
                self.lemmatizedKeywords.append(keyword_buffer)
                del keylist

            else:
                #simple unit keywords
                tokenizedKeywords[keyword] = self.__Lemmatization(keyword)
                self.lemmatizedKeywords.append(self.__Lemmatization(keyword))

        return tokenizedKeywords

    def __FindSynonyms(self, word_lemma):
        """
        Accesses WordReference to get the synonyms and antonyms of each word and creates the dictionaries.
        Parameters:
        -word_lemma: The lemma of the word that you want to search in order to get its synonyms and antonyms
        """ 
        #Web scraping
        url = 'https://www.wordreference.com/sinonimos/'
        find = url + word_lemma
        resp = requests.get(find)
        bs = BeautifulSoup(resp.text, 'lxml')
        xml_list = bs.find_all(class_='trans clickable')

        #Getting the useful information 
        self.synonyms[word_lemma] = dict()
        self.antonyms[word_lemma] = dict()
        self.synonyms[word_lemma]["Dictionary"] = dict()
        self.antonyms[word_lemma]["Dictionary"] = dict()
        word_synonym = []
        word_antonym = []
        for tree in xml_list:
          node= tree.find_all('li')
          names= tree.find_all('h3')
          for name in names:
              word = name.next_element
          for content in node:
            compare1 = content.find_all('span')
            compare2 =[content.next_element]
            if compare2 == compare1:
              for info in compare1:
                ant= info.next_element.split(',  ')
                for element2 in ant:
                    element2 = element2.replace("Antónimos: ","")
                    if len(element2.split()) == 1:
                        word_antonym.append(self.__Lemmatization(element2))
                    else:
                        expression=""
                        for subword in element2.split():
                            expression = self.__createExpression(expression, self.__Lemmatization(subword))
                        word_antonym.append(expression)

            else:
              sin =content.next_element.split(',  ')
              for element in sin:
                if len(element.split()) == 1:
                    word_synonym.append(self.__Lemmatization(element))
                else:
                    expression=""
                    for subword in element.split():
                        expression = self.__createExpression(expression, self.__Lemmatization(subword))

                    word_synonym.append(expression)

          #Indexing the levels of the dictionary and adding the information
          doc = self.nlp(word)
          self.synonyms[word_lemma]["Dictionary"][word] = dict()
          self.antonyms[word_lemma]["Dictionary"][word] = dict()  
          self.synonyms[word_lemma]["Dictionary"][word][doc.sentences[0].words[0].upos] = dict()
          self.antonyms[word_lemma]["Dictionary"][word][doc.sentences[0].words[0].upos] = dict()  
          self.synonyms[word_lemma]["Dictionary"][word][doc.sentences[0].words[0].upos] = word_synonym.copy()
          self.antonyms[word_lemma]["Dictionary"][word][doc.sentences[0].words[0].upos] = word_antonym.copy()

          word_synonym.clear()
          word_antonym.clear()
          self.synonyms[word_lemma]["Compound"] = 0
          self.antonyms[word_lemma]["Compound"] = 0

    def __ProcessInfo(self):
        """
        Main programme of the class
        """
        self.tokenizedKeywords = self.__TokenizeKeywords()
        for keyword in self.tokenizedKeywords:

            if  len(keyword.split()) == 1:
                if self.tokenizedKeywords[keyword] in self.synonyms.keys():
                    continue
                else:
                    #Analyze simple unit keywords
                    self.__FindSynonyms(self.tokenizedKeywords[keyword])
                    doc = self.nlp(self.__Lemmatization(keyword))
                    self.synonyms[self.__Lemmatization(keyword)]["GCategory"] = doc.sentences[0].words[0].upos                      

            else:
                #Getting the units of a compound word to analyze them too
                for word in self.tokenizedKeywords[keyword]:
                    if word in self.stopwords:
                        continue
                    else:
                        #Indicate that the word is not a keyword itself
                        self.__FindSynonyms(word) 
                        self.synonyms[word]["Compound"] = 1
                        self.antonyms[word]["Compound"] = 1

                        print(f'wordddd : {word}')
                        doc = self.nlp(self.__Lemmatization(word))
                        self.synonyms[self.__Lemmatization(word)]["GCategory"] = doc.sentences[0].words[0].upos 



















class NLP_Answers:

    """
    Processes the sentences of each student to find keywords and calculates the mark of each one
    """

    def __init__(self, file_name: list(), synonym_dict: dict(), antonym_dict: dict(), keywords_dict: dict(), LemmaDictionary:dict(), PTrans: pd.DataFrame(), PObs: pd.DataFrame(), windowMaxSize = [[1], [1], [1]]):
        """
        Class constructor.
        Parameters:
        -file_name: The path of the file that contains the information
        -synonym_dict: The dictionary of synonyms
        -antonym_dict: The dictionary of antonyms
        -keywords_dict: The list of lemmatized keywords
        -LemmaDictionary: The dictionary of lemmas
        -PTrans: The probability table of transition
        -PObs: The probability table of emission
        -windowMaxSize: The sizes of window of each set (keyword-synonym-antonym)
        """         
        self.windowMaxSize = windowMaxSize
        self.synonyms = synonym_dict
        self.antonyms = antonym_dict
        self.keywords = keywords_dict
        self._LemmaDictionary = LemmaDictionary
        self._PObs= PObs
        self._PTrans = PTrans

        self.stopwords = set(stopwords.words('spanish')).union(set(string.punctuation), set(OTHER_WORDS))
        self.nlp = stanza.Pipeline(lang='es', processors='tokenize,mwt,pos,lemma')

        self.feedback = dict()
        self.califications = dict()
        self.feedback_nofilter = dict()
        self.califications_nofilter = dict()

        self.lemmatizedSentence = None

        self.file = file_name  
        self.__ProcessInfo() 
    
    
    """
    Public methods
    """

    def showFeedback(self):
        """
        Returns the filtered feedback of each student's answer
        """
        return self.feedback
    def showMarks(self):
        """
        Returns the filtered found keywords and the given mark of each student's answer
        """
        return self.califications

    def showFeedbackDistribution(self):
        """
        Returns the feedback of each student's answer
        """
        return self.feedback_nofilter

    def showKeywordsDistribution(self):
        """
        Returns the found keywords and the given mark of each student's answer
        """
        return self.califications_nofilter


    """
    Private methods
    """

    def __SentenceLemmatization(self, sentence, complete_analysis = 0):
        """
        It calculates the lemma and the grammatical category of each word of the sentence
        Parameters:
        -sentence: The sentence you want to lemmatize
        -complete_analysis: 0 for processing only keywords with Viterbi, 1 for complete analysis
        """   
        sentence_split = sentence.split()
        useViterbi = 0
        lemmatized_sentence = []        


        for token in sentence_split:
            token = token.lower()
            try:
                lemma_aux = self.LemmaDictionary[token]

            except:
                lemma_aux = {'Ninguno': 'ninguno'}

            #Checking if Viterbi analysis is needed
            if complete_analysis:
                if len(lemma_aux)>1 and self.__Lemmatization(token) not in self.stopwords:
                    useViterbi = 1
                    break
            else:
                break_loop = 0
                if len(lemma_aux)>1 and self.__Lemmatization(token) not in self.stopwords:
                    for option in lemma_aux.keys():
                        if lemma_aux[option] in self.keywords:
                            break_loop = 1
                            useViterbi = 1
                            break
                    if break_loop:
                        break
        #Applying the Viterbi algorithm        
        if useViterbi:
            viterbi = Viterbi(self._PTrans, self._PObs.T, self._LemmaDictionary, sentence)
            tagged_sentence = viterbi.SyntacticAnalysis() 
            lemmatized_sentence = list()
            for _word in tagged_sentence:
                _word['token'] = _word['token'].lower()
                try:
                    _word_aux = re.sub("\(|\)|0|1|2|3|4|5|6|7|8|9|0","", _word['token'])
                    lemma_aux = self.LemmaDictionary[_word_aux]
                    lemmatized_sentence.append([lemma_aux[_word['tag']], _word['tag']])
                except:
                    lemmatized_sentence.append([_word['token'], _word['tag']])

        else:
            #Applying Stanza
            for token in sentence_split:
                token = token.lower()
                doc = self.nlp(token)
                lemmatized_sentence.append([self.__Lemmatization(token), doc.sentences[0].words[0].upos])


        return lemmatized_sentence


    def __Lemmatization(self, word):
        """
        Calculates the lemma of a word
        Parameters:
        -word: The word you want to lemmatize
        """ 
        try:
            lemma_aux = self._LemmaDictionary[word]
            
            #Using the dictionary of lemmas if the word is a simple unit
            if len(lemma_aux)==1 and word not in self.stopwords:
                for gcategory in lemma_aux:
                    lemma = lemma_aux[gcategory]

            else:
                #using stanza
                doc = self.nlp(word)
                lemma = doc.sentences[0].words[0].lemma

        except:
            #using stanza
            doc = self.nlp(word)
            lemma = doc.sentences[0].words[0].lemma

        return lemma 

    def __createExpression(self,expression,word):
        """
        Creates a way to concatenate words
        Parameters:
        -expression: the string whre you want to concatenate words
        -word: the word you want to add in the expression
        """         
        if expression == "":
            expression = word
        else:
            expression = expression + " " + word

        return expression      


    def __GetStudentsAnswers(self):
        """
        Gets the answer and ID of each student 
        """ 
        StudentsAnswers_list = []
        StudentsID_list = []
        for answer in self.file:
            for section in answer:
                if section == "respuesta":
                    StudentsAnswers_list.append(answer[section])
                if section == "hashed_id":
                    StudentsID_list.append(answer[section])

        return StudentsAnswers_list, StudentsID_list
     


    def __PrepareSentence(self, answer):
        """
        Divides the sentence into shorter phrases for easier processing
        Parameters:
        -answer: The sentence you want to divide 
        """  
        new_sentences = []
        #division criteria
        sentences = re.split(r'((?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s)', answer)
        for sentence in sentences:
            if len(sentence.split()) > 10:
                division_sentences = sentence.split(",")
                for division in division_sentences:
                    #making sure all symbols are off the word
                    new_sentences.append(re.sub("\n|\.|\,|\:|\"|\;","",division))
            else:
                #making sure all symbols are off the word
                new_sentences.append(re.sub("\n|\.|\,|\:|\"|\;","",sentence))

        return new_sentences


    def __SentenceTransformation(self, sentence):
        """
        Makes a sentence from the lemmas that were calculated in __SentenceLemmatization
        Parameters:
        -sentence: The string that is going to be lemmatized
        """         
        sentence = sentence.lower()
        new_sentence = ""
        for token in self.lemmatizedSentence:
            new_sentence = self.__createExpression(new_sentence,token[0])
        
        return new_sentence

    def __isInSentence(self,sentence, search_word):
        """
        Searches if a word appears in a sentence or group of words
        Parameters:
        -sentence: A given sentence
        -search_word: The word you want to search for in that sentence
        """ 
        for word in sentence:
            word=word.lower()
            if word == search_word:
                return 1
        return 0

    def __CalculateMark(self, student):
        """
        Calculates and assigns the mark of each student given the keywords that were found
        Parameters:
        -student: The ID of the student you are going to evaluate
        """ 

        self.feedback_nofilter[student] = self.feedback[student].copy()
        self.califications_nofilter[student] = self.califications[student].copy()
        
        #Filtering the repeated feedback of the student
        filtered_list = [x for x in self.feedback[student] if x != []]
        new_list = []
        for row in filtered_list:
            for feedback_element in row:
                new_list.append(feedback_element)

        self.feedback[student] = list(set(new_list))
        
        #Filtering the repeated number of keywords
        filtered_list = [x for x in self.califications[student] if x != []]
        new_list = []
        for row in filtered_list:
            for keyword_element in row:
                new_list.append(keyword_element)
        
        self.califications[student] = [] 
        self.califications[student].append(list(set(new_list)))

        #Evaluating the student
        Mark = 1 * len(self.califications[student][0])/len(self.keywords)
        self.califications[student].append("Nota: " + str(round(Mark, 2)))      
          
 
    def __isNegated(self, sentence, word, window):
        """
        Searches if an antonym appears negated in the sentence
        Parameters:
        -sentence: A given sentence
        -word: The antonym that you are analyzing
        -window: The window size to look 
        """ 

        negated_words = ["no", "nunca", "jamás", "nada", "ni", "siquiera", "ningún", "tampoco", "ninguno", "nadie", "ninguna"]

        isNegated = 0
        words=""
        for i in range(len(sentence)-window+1):
          for j in range(window):
            words = self.__createExpression(words, sentence[i+j])
          
          for adverb in negated_words:
              if adverb in words and word in words:
                  isNegated = True   
                  break
              else:
                words=""
        return isNegated

    def __isWordInWindow(self,phrase, word, window):
        """
        Scrolls a variable size filter to search for matches in the sentence
        Parameters:
        -phrase: A given sentence
        -word: The word you want to check if it is in the sentence
        -window: The window size to look 
        """ 

        if len(word.split()) != window:
            return 0
        else:
            #Preparing the word that you are going to search
            new_word=""
            for token in word.split():
              new_word = self.__createExpression(new_word, token)
              
            isInside = 0
            words=""
            #Checking if the word is in the sentence (in a given window)
            for i in range(len(phrase)-window+1):
              for j in range(window):
                words = self.__createExpression(words, phrase[i+j])
              #If there is a match, stop searching
              if words.lower() == new_word.lower():
                isInside = True   
                break
              else:
                words=""
            return isInside


    def __calculateGrammarCategory(self, sentence, keyword):
        """
        Gets the grammatical category of a word
        Parameters:
        -sentence: A given sentence
        -keyword: The keyword you want to know its grammatical category
        """ 
        grammatical_category = []
        for token in self.lemmatizedSentence:
            if token[0] == keyword:
                grammatical_category.append(token[1])      
            
        return grammatical_category

    def __Evaluate(self, sentence, student):
        """
        Creates searching loops in order to find keywords in the sentence
        Parameters:
        -sentence: A given sentence
        -student: The ID of the student whose answer you are analyzing
        """
        words_guessed=[]
        feedback_list = []
        sentence = self.__SentenceTransformation(sentence)
        sentence_split = sentence.split()
        #print(f'{sentence_split}')
        wlist1 = self.windowMaxSize[0]
        wlist2 = self.windowMaxSize[1]
        wlist3 = self.windowMaxSize[2]

        #Search for keywords
        for windowsize in wlist1:
            for keyword in self.keywords:
                #Checking the existence of a keyword
                if self.__isWordInWindow(sentence_split, keyword, windowsize):
                    sintax_good= 1
                    for component in keyword.split():
                        grammatical_category = self.__calculateGrammarCategory(sentence, component)                  

                        for g_category in grammatical_category:
                            if component in self.stopwords:
                                continue
                            else:
                                #checking if the keyword has the correct grammatical category
                                if g_category == self.synonyms[component]["GCategory"] or len(self.synonyms[component]["Dictionary"]) == 0:
                                    if len(keyword.split()) == 1:
                                        feedback_list.append("La palabra clave " + keyword + " aparece correctamente utilizada en el texto")
                                        words_guessed.append(keyword)
                                        
                                else:
                                    sintax_good = 0
                                    feedback_list.append("La palabra clave " + keyword + " aparece en el texto, pero no con la categoría gramatical buscada, por lo que su sentido podría ser inadecuado")
                                    words_guessed.append(keyword)
                      
                    #checking if the keyword has the correct grammatical category for a commpound keyword
                    if sintax_good and len(keyword.split()) > 1:
                        feedback_list.append("La expresión clave " + keyword + " aparece correctamente empleada en el texto")
                        words_guessed.append(keyword)
                    elif not sintax_good and len(keyword.split()) > 1:
                        feedback_list.append("La expresión clave " + keyword + " aparece, pero su significado podría no ser el adecuado")
                        words_guessed.append(keyword)

        #Search for synonyms
        for windowsize in wlist2:
            for keyword in self.keywords:
                #Checking the existence of a synonym
                if len(keyword.split())==1 and len(self.synonyms[keyword]["Dictionary"]) > 0 and not self.synonyms[keyword]["Compound"]:
                    for component in self.synonyms[keyword]["Dictionary"]:
                        if component != keyword and self.__isInSentence(sentence_split, component):
                            feedback_list.append("La palabra " + component + " aparece en el texto y es una forma de expresar la palabra clave " + keyword + ", pero su significado puede no ser el adecuado")
                            words_guessed.append(keyword)

                        for category in self.synonyms[keyword]["Dictionary"][component]:
                            for element in self.synonyms[keyword]["Dictionary"][component][category]:
                                if self.__isWordInWindow(sentence_split, element, windowsize):
                                    if len(element.split())>1:
                                        feedback_list.append("En el texto aparece la expresión " + element + ", que es sinónima del lema de la palabra clave " + keyword)
                                        words_guessed.append(keyword)
                                    
                                    else: 
                                        #checking the grammatical category of the synonym                                      
                                        grammatical_category = self.__calculateGrammarCategory(sentence, element)

                                        for g_category in grammatical_category:
                                            if g_category == self.synonyms[keyword]["GCategory"] or len(self.synonyms[keyword]["Dictionary"]) ==  0:
                                                feedback_list.append("En el texto aparece la palabra " + element + ", que es sinónima del lema de la palabra clave " + keyword)
                                                words_guessed.append(keyword)
                                            else:
                                                feedback_list.append("El sinonimo " + element + " de la palabra clave " + keyword + " aparece, pero no con la categoría gramatical buscada, por lo que su sentido podría ser inadecuado")
                                                words_guessed.append(keyword)
                #analyzing compound keywords                                                             
                elif len(keyword.split()) > 1:
                    no_word = 0
                    expression = ""
                    for word in keyword.split():
                        #print(f'{word}')
                        #Analyze each one of the units of a compound word
                        if self.__isInSentence(sentence_split, word):
                            expression = self.__createExpression(expression, word)
                        else:
                            if word in self.stopwords:
                                expression = self.__createExpression(expression, word)
                            else:
                                no_word = 1                            
                                for component in self.synonyms[word]["Dictionary"]:
                                    for category in self.synonyms[word]["Dictionary"][component]:
                                        for sin in self.synonyms[word]["Dictionary"][component][category]:
                                            if self.__isInSentence(sentence_split, sin):
                                                no_word = 0
                                                expression = self.__createExpression(expression, sin)
                                            else:
                                                continue
                        if no_word:
                            break
                    #if the compound keyword match
                    if not no_word:
                        if self.__isWordInWindow(sentence_split, expression,windowsize):
                            if expression == keyword:
                                continue
                            else:
                                feedback_list.append("En el texto aparece la expresión " + expression + ", que es sinónima de la sentencia clave " + keyword)
                                words_guessed.append(keyword)
        #Search for antonyms
        for windowsize in wlist3:
            for keyword in self.antonyms.keys():
                if len(self.antonyms[keyword]["Dictionary"]) == 0:
                    continue
                else:
                    for component in self.antonyms[keyword]["Dictionary"]:
                        for category in self.antonyms[keyword]["Dictionary"][component]:
                            for element in self.antonyms[keyword]["Dictionary"][component][category]: 
                                #Analyzing if the antonym exists in the sentence                            
                                if self.__isWordInWindow(sentence_split, element, windowsize):
                                    #Analyzing if the antonym has a negated word near
                                    if self.__isNegated(sentence_split, word, 5):
                                        feedback_list.append("En el texto aparece la palabra " + element + " negada, que es antónima de " + keyword)
                                        words_guessed.append(keyword)
                                    else:
                                        feedback_list.append("Aparece la palabra " + element + ", que es antónima de " + keyword + ", pero no se ha encontrado ninguna forma de negación, por lo que podría no compartir el significado buscado")
                                        words_guessed.append(keyword)                                                     
        
        #Collecting and saving the information of the given student
        self.feedback[student].append(list(set(feedback_list)))
        self.califications[student].append(list(set(words_guessed)))

    def __ProcessInfo(self):
        """
        Main programme of the class
        """
        answers, IDs = self.__GetStudentsAnswers()
        #Getting the answer and ID of the student
        for student_answer, ID in zip(answers, IDs):
            self.feedback[ID] = []
            self.califications[ID] = []
            sentences = self.__PrepareSentence(student_answer)
            #Analyze all the sentences of the student's answer
            for sentence in sentences:
                self.lemmatizedSentence = self.__SentenceLemmatization(sentence)
                self.__Evaluate(sentence, ID)
            #Calculate the mark               
            self.__CalculateMark(ID)



