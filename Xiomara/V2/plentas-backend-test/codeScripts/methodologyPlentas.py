import numpy as np
import spacy


class PlentasMethodology():
    """
    The methodology developed in Plentas consists in iteratively compute the similarity between two sentences: the baseline response and one variable group of sentences from the student's response. The goal of it is to identify in the text the subresponses to each subquestion so the answer-question similarity is better obtained and thus the overall calculated similarity fits better to the expected one.

    Inputs:
        -settings: The settings from the config json and the api.
    """
    def __init__(self, settings):
        self.settings = settings
        self.maxSimilarity = -99999
        self.spacy_model = spacy.load('es_core_news_sm')
    
    def getSimilarity(self, sentences, similarityMethod):
        """
        This function calculates the similarity between two responses using the Plentas methodology

        Inputs:
            sentences: pre-processed sentences of the student's response
            similarityMethod: choose between spacy or bert
        Outputs:
            similarity: an array of the generated similarity for each subquestion
        """

        #Initializing the similarity array so if the student's response is blank default content is output 
        similarity = np.zeros(len(self.settings.indice_minipreguntas))

        #if the response is not blank ...
        if len(sentences) > 1 and sentences[0] != '':

            #obtaining the similarity for each subquestion        
            for minirespuesta, minipregunta in zip(self.settings.minirespuestas, self.settings.indice_minipreguntas):                
                
                self.maxSimilarity = -99999

                #varying the group of sentences
                for start in list(range(self.settings.minAgrupation,self.settings.maxAgrupation)): 
                    
                    #varying the size of the group of sentences
                    for size in range(len(sentences)):                                
                        try:
                            #extracting the sentences
                            r_alumno, _ = self.__Line2LineAnalysis__(sentences, size, start)
                            #computing its similarity
                            similar = self.__computeSimilarity__(r_alumno, minirespuesta, similarityMethod)

                            #storing the highest
                            if similar > self.maxSimilarity:
                                self.maxSimilarity = similar                           
                                                            
                        except:
                            break
                #stacking the similarity of each subquestion
                similarity[int(minipregunta[12:])] = similar                   
                            
        return similarity

    def __computeSimilarity__(self,sentences1,sentences2,similarityMethod):
        """
        This function applies a defined method to obtain the similarity between two sentences
        Inputs:
            -sentences1: First set of sentences to compare
            -sentences2: Second set of sentences to compare
            -similarityMethod: The inherited similarity method selected in getSimilarity
        Outputs:
            -similar: The similarity score
        """
        if similarityMethod.lower() == "spacy":
            r1 = self.spacy_model(sentences1)
            r2 = self.spacy_model(sentences2)
            similar = round(r1.similarity(r2), 3)
        else:
            similar = self.settings.BertModels_glbl.similarity(self.settings.model_path, sentences1, sentences2)[0][0].item()
        
        return similar
        
    def __Line2LineAnalysis__(self, sentences, size, start):    
        """
        This function extracts the required group of sentences from a response.
        Inputs:
            -sentences: the array of sentences from the student's response
            -size: the max number of sentences to extract.
            -start: the array position from where to start extracting
        Outputs:
            respuesta_alumno: the extracted sentences
            r_name: the label of those sentences (their position in the response and, thus, in the input array)
        """
        new_respuesta = ""                                   
        breaking_variable = sentences[size+start-1]
        for line in sentences[size:size+start]:
            new_respuesta= new_respuesta + line + '. '
            
        respuesta_alumno = new_respuesta.lower()

        if start == 1:
            r_name = "Line " + str(size+1)
            
        else:                                                
            r_name = "Lines " + str(size+1) + " - " + str(size+start)

        return respuesta_alumno, r_name  
    