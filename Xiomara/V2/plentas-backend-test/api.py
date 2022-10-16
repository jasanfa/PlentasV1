from urllib import response
from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from hashids import Hashids
import zipfile
import os

from utils import save_json
#from plentas import Plentas

a = "aaa"
e = 0

responses = [
           { '0' : {
                      "ID": "9J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.1,
                      "NotaBert":0.8,
                      "Feedback": "Hola1"
           }
           },
           { '1': {
                      "ID": "7J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.2,
                      "NotaBert":0.4,
                      "Feedback": "Hola2"
           }
           },
           { '2':{
                      "ID": "8J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.3,
                      "NotaBert":0.2,
                      "Feedback": "Hola3"
                }
           },
           { '3' : {
                      "ID": "9J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.4,
                      "NotaBert":0.8,
                      "Feedback": "Hola4"
           }
           },
           { '4': {
                      "ID": "7J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.5,
                      "NotaBert":0.4,
                      "Feedback": "Hola5"
           }
           },
           { '5':{
                      "ID": "8J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.6,
                      "NotaBert":0.2,
                      "Feedback": "Hola6"
                }
           },
           { '6' : {
                      "ID": "9J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.7,
                      "NotaBert":0.8,
                      "Feedback": "Hola7"
           }
           },
           { '7': {
                      "ID": "7J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.8,
                      "NotaBert":0.4,
                      "Feedback": "Hola8"
           }
           },
           { '8':{
                      "ID": "8J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 0.9,
                      "NotaBert":0.2,
                      "Feedback": "Hola9"
                }
           },
           { '9' : {
                      "ID": "9J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 1.0,
                      "NotaBert":0.8,
                      "Feedback": "Hola10"
           }
           },
           { '10' : {
                      "ID": "rrr9J4q2VolejRejNmGQBW7",
                      "NotaSpacy": 1.1,
                      "NotaBert":0.8,
                      "Feedback": "Hola11"
           }
           },
           { '11': {
                      "ID": "fdffffffffffejRejNmGQBW7",
                      "NotaSpacy": 1.2,
                      "NotaBert":0.4,
                      "Feedback": "Hola12"
           }
           },
           { '12':{
                      "ID": "gg",
                      "NotaSpacy": 1.3,
                      "NotaBert":0.2,
                      "Feedback": "Hola13"
                }
           },
]

def create_custom_file_path(file):
    path = "StudentAnswersZip/" + file
    return path

def extractZipData(ruta_zip):
    ruta_extraccion = "StudentAnswers/"
    password = None
    archivo_zip = zipfile.ZipFile(ruta_zip, "r")
    try:
        #print(archivo_zip.namelist())
        archivo_zip.extractall(pwd=password, path=ruta_extraccion)
    except:
        pass
    archivo_zip.close()

    #hashids = Hashids(min_length=20)
    #hashids.encode(alumno_nmbr)

def answersTodict(zip_path):
    extractZipData(zip_path)
    studentAnswersDict = dict()
    hashids = Hashids(min_length=20)

    for work_folder in os.listdir("StudentAnswers"):
        for student, indx in zip(os.listdir("StudentAnswers/" + work_folder), range(len(os.listdir("StudentAnswers/" + work_folder)))):
            try:
                studentAnswersDict[hashids.encode(indx)] = dict()
                studentAnswersDict[hashids.encode(indx)]["indx"] = indx
                fichero = open("StudentAnswers/" + work_folder + "/" + student + "/" + 'comments.txt')
                lineas = fichero.readlines()
                studentAnswersDict[hashids.encode(indx)]["answer"] = lineas
            except:
                continue
    
    save_json("StudentsDict.json", studentAnswersDict)


def create_app():
    app = Flask(__name__)
    CORS(app)
    return app

app = create_app()

@app.route('/plentasapi/', methods=['GET'])
def getData():
    response = {'message': 'Plentas API is running'}
    return jsonify(response)

@app.route('/plentasapi/', methods=['POST'])

def processData():
    uploadedFile = request.files['zipFile']
    #uploadedFile = request.form['zipFile']	
    configuration = request.form["configuration"] 
    print(uploadedFile) 
    print(configuration)      
    uploadedFile.save(create_custom_file_path(uploadedFile.filename))
    answersTodict(create_custom_file_path(uploadedFile.filename)) 

    return jsonify(responses)
        
    #inputData = request.json
    #print(inputData)
    #response = {'message': 'Plentas API is running', 'message2': 'Plentas API2 is running', 'message3': 'Plentas API3 is running'}    
    #return jsonify(responses)
    #return responses_dict
    
    # aquí va toda la magia, en inputData están los datos de entrada
    #response = Plentas(inputData) 
    
     #{'message': 'success'}
    #response2 = response.processData() 
    #return response2


if __name__ == '__main__':
    app.run(debug=True)
