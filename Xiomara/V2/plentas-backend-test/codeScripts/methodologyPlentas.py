import numpy as np
import spacy

from codeScripts.rubrics import *

class PlentasMethodology():
    """
    The methodology developed in Plentas consists in iteratively compute the similarity between two sentences: the baseline response and one variable group of sentences from the student's response. The goal of it is to identify in the text the subresponses to each subquestion so the answer-question similarity is better obtained and thus the overall calculated similarity fits better to the expected one.

    Inputs:
        -settings: The settings from the config json and the api.
    """
    def __init__(self, settings):
        self.settings = settings
        self.maxSimilarity = -99999
        self.SemanticLevel = Semantica2(self.settings)
          
          
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

        #obtaining the similarity for each subquestion
        for minirespuesta, minipregunta in zip(self.settings.minirespuestas, self.settings.indice_minipreguntas):
            self.SemanticLevel.output.initInforms(self.settings.studentID, minipregunta)

            #if the response is not blank ...
            if len(sentences) >= 1 and sentences[0] != '':

                self.maxSimilarity = -99999
                
                #varying the group of sentences
                for agrupation in list(range(self.settings.minAgrupation,self.settings.maxAgrupation)):
                    
                    #varying the size of the group of sentences
                    for s in range(len(sentences)):                                
                        try:
                            #extracting the sentences
                            r_alumno, r_label = self.__Line2LineAnalysis__(sentences, s, agrupation)
                            #computing its similarity
                            #similar = self.__computeSimilarity__(r_alumno, minirespuesta, similarityMethod)
                            similar = self.SemanticLevel.computeSimilarity(r_alumno, minirespuesta, similarityMethod)

                            self.SemanticLevel.output.updateInformsBucle(self.settings.studentID, minipregunta, r_alumno, r_label, agrupation, similar, 1 if similar > self.maxSimilarity else 0)   

                            #storing the highest
                            if similar > self.maxSimilarity:
                                self.maxSimilarity = similar
                             
                        except:
                            break

                #stacking the similarity of each subquestion
                similarity[int(minipregunta[12:])] = self.maxSimilarity       
                         
        return similarity

        
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
    

    def EvaluationMethod(self, studentID, response, similarity_array, similarity_type = "spacy"):
        notaSpacy = 0
        esSuperior = 0
        esIntermedio = 0        
        for umbralL, umbralH in zip(self.SemanticLevel.output.min_umbral, self.SemanticLevel.output.max_umbral):
            for minipregunta, similarity in zip(self.settings.indice_minipreguntas, similarity_array):
                print(minipregunta, similarity)
                if similarity >= umbralL:
                    if similarity <= umbralH:
                        if not esSuperior:
                            esIntermedio = 1
                    else:
                        esIntermedio = 0
                        esSuperior = 1


                if esSuperior: 
                    notaSpacy +=1
                elif esIntermedio:
                    notaSpacy += 0.5

                esSuperior = 0
                esIntermedio = 0

            notaSpacy = notaSpacy/len(self.settings.indice_minipreguntas)
            self.SemanticLevel.output.updateInforms(studentID, umbralL, umbralH, notaSpacy, response)

            if umbralL == 0.3 and umbralH == 0.7:
                notaGuardar = notaSpacy


            notaSpacy = 0
        print(notaGuardar)
        print("\n")
        return notaGuardar



    

     



    