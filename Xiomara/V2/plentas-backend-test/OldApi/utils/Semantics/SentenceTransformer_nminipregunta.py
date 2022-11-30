from distutils.filelist import FileList
import json
from datasets import load_dataset
from sklearn.model_selection import train_test_split
import pandas as pd
import os

from json import encoder

from utils import save_json, load_json, load_json_dtset

#variables que tengo que hacer parametrizables:
fileList = ["utils/Semantics/Dataset_train_BERT.json"]
path_created_dataset = "C:/Users/javier.sanz/UNIR/TEAMS - PLENTAS - General/new/Experimentos/20022-06-21_ModelosBERT - Entrenamiento por minipregunta/Metodos - analisis por minipregunta/TrainedModels/JoinedSubjects2.json"
#los parámetros de SentTransf_train

def getJsonInfo(fileName):
    samples = []
    subject_info = load_json(fileName)
    nmbr_minipreguntas = 0
    for id in subject_info[0].keys():
        for part_of_rubric in subject_info[0][id].keys():
            #print(subject_info[0][id])
            #break
            if part_of_rubric == "m" + str(nmbr_minipreguntas+1):
                nmbr_minipreguntas+=1
        break
    
    for id in subject_info[0].keys():
        hashed_id = id
        mark, responseStudent, responseTeacher = [],[],[]      
        for i in range(nmbr_minipreguntas):
            mark.append(subject_info[0][id]["m"+ str(i+1)+ "_score"])
            responseStudent.append(subject_info[0][id]["resp_m"+ str(i+1)])
            responseTeacher.append(subject_info[0][id]["m"+ str(i+1)])

        ie = {'responseTeacher': responseTeacher,
        'responseStudent': responseStudent,
        'mark': mark,
        'hashed_id': hashed_id
        }

        samples.append(ie)

    return samples


def PreparingDataSet():
    #Creating a list with the necesarry fields
    first_iter = 1
    for subject in fileList:
        if first_iter:
            subjectFileList = getJsonInfo(subject)
            first_iter = 0
        else: 
            subjectFileList = subjectFileList + getJsonInfo(subject)

    #Splitting the dataset into train,valid and test data
    data_train ,data_test = train_test_split(subjectFileList,test_size=0.3)
    data_train ,data_valid = train_test_split(data_train,test_size=0.1)

    data = {'train': data_train
        ,'test': data_test
        ,'valid': data_valid
        }

    save_json(path_created_dataset, data)


import json
import math
import pandas as pd
from datasets import load_dataset,Dataset,DatasetDict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error, mean_absolute_percentage_error, r2_score, roc_curve
from sentence_transformers import SentenceTransformer, InputExample, losses, util, evaluation, models
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
from torch import nn

import datasets
import sklearn
import sentence_transformers
import torch



class SentTransf_train():
    def __init__(self, modelsToTrain = [
                  {"checkPoint": "distiluse-base-multilingual-cased-v1", "fromScratch": False},
                  {"checkPoint": "paraphrase-multilingual-MiniLM-L12-v2", "fromScratch": False},
                  {"checkPoint": "paraphrase-multilingual-mpnet-base-v2", "fromScratch": False},
                  {"checkPoint": "all-distilroberta-v1", "fromScratch": False},
                  {"checkPoint": "bert-base-multilingual-uncased", "fromScratch": True},
                  {"checkPoint": "dccuchile/bert-base-spanish-wwm-uncased", "fromScratch": True}
              ], epochsToTest = [1,5,10,30,50,100], saving_path = 'C:/Users/javier.sanz/UNIR/TEAMS - PLENTAS - General/new/Experimentos/20022-06-21_ModelosBERT - Entrenamiento por minipregunta/Metodos - analisis por minipregunta/TrainedModels/'):

        #modelsToTrain = [{"checkPoint": "distiluse-base-multilingual-cased-v1", "fromScratch": False}]
        #epochsToTest = [1]  
        self.saving_path = saving_path
        self.data_train = self.__getDatasetPartition(path_created_dataset, "train")
        self.data_test = self.__getDatasetPartition(path_created_dataset, "test")
        self.data_valid = self.__getDatasetPartition(path_created_dataset, "valid")    
        
        #epochsToTest = [1,5,10,30,50,100]
        #Get evaluator
        evaluator = self.__CreateModelEvaluationData()

        #Train the models
        for model in modelsToTrain:
            for epochs in epochsToTest:
                self.__TrainModel(model["checkPoint"], evaluator, epochs, model["fromScratch"])

    def __getDatasetPartition(self, fileName, split):

        #subject1_fileDataset = load_dataset("json", data_files=fileName)
        subject1_fileDataset = load_json_dtset(fileName)
        
        samples = []

        for i in range (0,len(subject1_fileDataset[0][split])): #len(subject1)
            for j in range (len(subject1_fileDataset[0][split][i]['mark'])):
                #print(subject1_fileDataset[0][split][i]['mark'], j)
                mark = subject1_fileDataset[0][split][i]['mark'][j]
                #print(mark)
                responseStudent = subject1_fileDataset[0][split][i]['responseStudent'][j]
                responseTeacher = subject1_fileDataset[0][split][i]['responseTeacher'][j]
                
                ie = InputExample(texts=[responseTeacher, responseStudent], label=mark)
                samples.append(ie)
            
        return samples 

    def __CreateModelEvaluationData(self):
        sentences1 = []
        sentences2 = []
        scores = []

        for i in range (0,len(self.data_valid)):
            sentences1.append(self.data_valid[i].texts[0])
            sentences2.append(self.data_valid[i].texts[1])
            scores.append(self.data_valid[i].label)

        evaluator = evaluation.EmbeddingSimilarityEvaluator(sentences1, sentences2, scores)
        return evaluator

    def __TrainModel(self, checkpoint, evaluator, epochs, fromScratch):
        batch_size = int(len(self.data_train) * 0.1)
        #Create the model from checkpoint
        if (not fromScratch):
            model = SentenceTransformer(checkpoint)
        else:
            word_embedding_model = models.Transformer(checkpoint, max_seq_length=256)
            pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
            dense_model = models.Dense(in_features=pooling_model.get_sentence_embedding_dimension(), out_features=256, activation_function=nn.Tanh())
            model = SentenceTransformer(modules=[word_embedding_model, pooling_model, dense_model])

        train_dataloader = DataLoader(self.data_train, shuffle=True, batch_size=batch_size)
        train_loss = losses.CosineSimilarityLoss(model)

        #Fit the model
        local_model_path = self.saving_path + 'Model_' + checkpoint + '/' + str(epochs) + '_Epochs'
        warmup_steps = math.ceil(len(train_dataloader) * epochs * 0.1) #10% of train data for warm-up
        evaluation_steps = int(len(train_dataloader)*0.1)
        print(len(train_dataloader),warmup_steps,evaluation_steps)
        model.fit(train_objectives=[(train_dataloader, train_loss)]
                    , epochs=epochs
                    , warmup_steps=warmup_steps
                    , evaluator=evaluator
                    , evaluation_steps=evaluation_steps
                    ,output_path=local_model_path
                    ,save_best_model=True)

        try:
            os.mkdir(self.saving_path + "models")
        except:
            pass
    
        model.save(self.saving_path + "models/" +checkpoint+ str("-Epochs-") + str(epochs))


import json
import math
import pandas as pd
from datasets import load_dataset,Dataset,DatasetDict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error, mean_absolute_percentage_error, r2_score, roc_curve
from sentence_transformers import SentenceTransformer, InputExample, losses, util, evaluation
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader


class SentTransf_test():
    def __init__(self, modelsToTest = ['distiluse-base-multilingual-cased-v1'
                ,'paraphrase-multilingual-MiniLM-L12-v2'
                ,'paraphrase-multilingual-mpnet-base-v2'
                ,'all-distilroberta-v1'
                ,'bert-base-multilingual-uncased'
                ,'dccuchile'
              ], epochsToTest = [1,5,10,30,50,100], save_path = 'C:/Users/javier.sanz/UNIR/TEAMS - PLENTAS - General/new/Experimentos/20022-06-21_ModelosBERT - Entrenamiento por minipregunta/Metodos - analisis por minipregunta/TrainedModels'):
        
        self.modelsToTest = modelsToTest
        self.epochsToTest = epochsToTest
        self.save_path = save_path
        
        #model for similarity calc only (to reduce time)
        model_path = self.save_path + "/" + "Model_"+ modelsToTest[0] + "/" + str(epochsToTest[0])+ '_Epochs'
        self.model = SentenceTransformer(model_path)
        #modelsToTest = ['distiluse-base-multilingual-cased-v1']
        #epochsToTest = [1] 
        
    def similarity(self, text1, text2):
        #local_model_path = self.save_path + '/' + checkpoint + '/' + str(epochs) + '_Epochs'

        #Compute embedding for both lists
        embeddings1 = self.model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.model.encode(text2, convert_to_tensor=True)

        #Compute cosine-similarits
        cosine_score = util.cos_sim(embeddings1, embeddings2)
        return cosine_score


    def test_model(self):
        try:
            os.mkdir(self.save_path + '/tests')
        except: 
            pass      
        
        self.data_test = self.__getDatasetPartition(path_created_dataset, "test")
        
        self.model_name = []
        self.epochs = []
        self.metricMAE = []
        self.metricMSE = []
        self.metricRMSE = []
        self.metricRMSLE = []
        self.metricMAPE = []
        self.metricR2 = []
        #Train & Test the model
        cnt=0


        for checkpoint in self.modelsToTest:

            #checkpoint = 'Model_' + checkpoint.replace('/','_')
            checkpoint = 'Model_' + checkpoint
            #df = pd.DataFrame(columns=['Sentence1', 'Sentence2', 'Hashed_id', 'Mark'])
            df = pd.DataFrame()
            dfMetrics = pd.DataFrame(columns=['Model','Epochs', 'MAE', 'MSE', 'RMSE', 'RMSLE', 'MAPE', 'R2'])

            for epochs in self.epochsToTest:
                self.__TestModel(checkpoint, self.data_test, epochs, df)
                self.model_name.append(checkpoint)

            #Save Score Results file
            df.to_csv(self.save_path + '/tests/' + checkpoint +'_Scores_Results.csv', index=False, sep=';', encoding='utf-8')

        #Save Metrics file
        dfMetrics['Model'] = self.model_name
        dfMetrics['Epochs'] = self.epochs
        dfMetrics['MAE'] = self.metricMAE
        dfMetrics['MSE'] = self.metricMSE
        dfMetrics['RMSE'] = self.metricRMSE
        dfMetrics['RMSLE'] = self.metricRMSLE
        dfMetrics['MAPE'] = self.metricMAPE
        dfMetrics['R2'] = self.metricR2
        dfMetrics.to_csv(self.save_path + '/tests/All_Metrics_Results.csv', index=False, sep=';', encoding='utf-8')




    def __getDatasetPartition(self, fileName, split):
        #subject1_fileDataset = load_dataset("json", data_files=fileName, split="train")
        subject1_fileDataset = load_json_dtset(fileName)
        samples = []

        for i in range (0,len(subject1_fileDataset[0][split])): #len(subject1)
            hashed_id = subject1_fileDataset[0][split][i]['hashed_id']
            mark = subject1_fileDataset[0][split][i]['mark']
            responseStudent = subject1_fileDataset[0][split][i]['responseStudent']
            responseTeacher = subject1_fileDataset[0][split][i]['responseTeacher']
            
            ie = InputExample(guid= hashed_id, texts=[responseTeacher, responseStudent], label=mark)
            samples.append(ie)

        return samples  

    def __TestModel(self, checkpoint, data, epochs, df):
        #Load model
        #local_model_path = 'jfarray' + '/' + checkpoint  + '_' + str(epochs) + '_Epochs'
        #self.epochs.append(str(epochs))
        
        local_model_path = self.save_path + '/' + checkpoint + '/' + str(epochs) + '_Epochs'
        model = SentenceTransformer(local_model_path)

        for id_minipregunta in range(len(data[0].texts[0])):  
            hashed_ids = []
            sentences1 = []
            sentences2 = []
            marks = []
            scores = []
            marksFloat = []
            scoresFloat = []          
            for i in range (0,len(data)): #len(data)
                sentences1.append(data[i].texts[0][id_minipregunta])
                sentences2.append(data[i].texts[1][id_minipregunta])

            #Compute embedding for both lists
            embeddings1 = model.encode(sentences1, convert_to_tensor=True)
            embeddings2 = model.encode(sentences2, convert_to_tensor=True)
            
            #Compute cosine-similarits
            cosine_scores = util.cos_sim(embeddings1, embeddings2)

            #Output the pairs with their score
            for i in range(len(sentences1)):
                hashed_ids.append(data[i].guid)
                #print(data[i].label)
                marks.append(str(data[i].label[id_minipregunta]).replace('.',','))
                marksFloat.append(data[i].label[id_minipregunta])
                scores.append(str(round(cosine_scores[i][i].item(),3)).replace('.',','))
                scoresFloat.append(round(cosine_scores[i][i].item(),3))
            
            #Save scores in the file
            df['Hashed_id minipregunta' + str(id_minipregunta)] = hashed_ids
            df['Mark minipregunta' + str(id_minipregunta)] = marks
            df['Score_' + str(epochs) + " minipregunta" + str(id_minipregunta)] = scores
            df['Sentence1 minipregunta' + str(id_minipregunta)] = sentences1
            df['Sentence2 minipregunta' + str(id_minipregunta)] = sentences2

            self.epochs.append(str(epochs))
            #Calculate metrics 'MAE', 'MSE', 'RMSE', 'RMSLE', 'MAPE', 'R2'
            print(marksFloat, scoresFloat)
            self.metricMAE.append(str(mean_absolute_error(marksFloat, scoresFloat)).replace('.',','))
            self.metricMSE.append(str(mean_squared_error(marksFloat, scoresFloat, squared = True)).replace('.',','))
            self.metricRMSE.append(str(mean_squared_error(marksFloat, scoresFloat, squared = False)).replace('.',','))
            try:
                self.metricRMSLE.append(str(mean_squared_log_error(marksFloat, scoresFloat)).replace('.',','))
            except:
                self.metricRMSLE.append('-')
            
            self.metricMAPE.append(str(mean_absolute_percentage_error(marksFloat, scoresFloat)).replace('.',','))
            self.metricR2.append(str(r2_score(marksFloat, scoresFloat)).replace('.',','))

            #modelo 12,4 e input 12,1 por haber hecho el split por minipregunta
            """
            #Evaluate Model this test data
            batch_size = 15 #Initializes the batch size with the same value as the training
            test_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(self.data_test, batch_size=batch_size, name= checkpoint)

            test_evaluator(model, output_path= self.save_path + '/tests/')

            """
        
