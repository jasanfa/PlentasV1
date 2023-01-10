from urllib import response
from flask import Flask, request, jsonify
from flask_cors import CORS
from hashids import Hashids
import zipfile
import os
from codeScripts.utils import save_json, load_json, create_file_path
from plentas import Plentas
import json
import pathlib


def createTeacherJson(configuration):
    """
    This function extracts the information about the subquestions and subanswers and puts them in the correct format.
    Inputs:
        config: The configured info from the api.
    Outputs:
        teachersJson: The generated dictionary with the subquestions.
    """
    teachersJson = {"enunciado": "", "minipreguntas":[], "keywords":""}

    #5 is the maximum number of permitted subquestions in the configuration2 page
    
    for i in range(5):
       
        try:
            teachersJson["minipreguntas"].append({
				"minipregunta": configuration["minip" + str(i+1)],
				"minirespuesta": configuration["minir" + str(i+1)]
			})

        except:
            break

    return teachersJson

def extractZipData(ruta_zip):
    """
    This function extracts the students's answers from the zip file (the one the teacher has in the task section).
    Inputs:
        ruta_zip: The path inherited from answersTodict
    """
    #defining the path where the extracted info is to be stored
    ruta_extraccion = create_file_path("StudentAnswers/", doctype= 1)
    #extracting the info
    archivo_zip = zipfile.ZipFile(ruta_zip, "r")
    try:
        archivo_zip.extractall(pwd=None, path=ruta_extraccion)
    except:
        pass
    archivo_zip.close()

def removeHtmlFromString(string):
    """
    This function removes the html tags from the student's response.
    Inputs:
        -string: The student's response
    Outputs:
        -new_string: The filtered response
    """
    string = string.encode('utf-8', 'replace')
    string = string.decode('utf-8', 'replace')
    new_string = ""
    skipChar = 0
    for char in string:
        if char == "<":
            skipChar = 1
        elif char == ">":
            skipChar = 0
        else:
            if not skipChar:        
                new_string = new_string+char

    new_string = new_string.encode('utf-8', 'replace')
    new_string = new_string.decode('utf-8', 'replace')
    return new_string

def answersTodict(zip_path):
    """
    This function extracts the students's answers and stacks them in one specific format so that it can be processed next.
    Inputs:
        ruta_zip: The path where the zip file is stored
    Outputs:
        studentAnswersDict: The dictionary with all the responses
    """
    #extracting the data
    extractZipData(zip_path)

    hashids = Hashids(min_length=20)
    studentAnswersDict = []

    #stacking the information of each extracted folder
    for work_folder in os.listdir(create_file_path("StudentAnswers/", doctype= 1)):
        for student, indx in zip(os.listdir(create_file_path("StudentAnswers/" + work_folder, doctype= 1)), range(len(os.listdir(create_file_path("StudentAnswers/" + work_folder, doctype= 1))))):
            student_name = student.split("(")
            student_name = student_name[0]
            try:
                #opening the file

                #fichero = open(create_file_path("StudentAnswers/" + work_folder + "/" + student + "/" + 'comments.txt', doctype= 1))
                #where the actual response is
                fichero = open(create_file_path("StudentAnswers/" + work_folder + "/" + student + "/" + 'Adjuntos del envio/Respuesta enviada', doctype= 1), encoding='utf-8')                
                #reading it
                lineas = fichero.readlines()

                #removing html                
                lineas[0] = removeHtmlFromString(lineas[0])           
                                
                #saving it                                
                studentAnswersDict.append({"respuesta":lineas[0], "hashed_id":student_name, "TableIndex":indx})

            except:
                studentAnswersDict.append({"respuesta":"", "hashed_id":student_name, "TableIndex":indx})

    #saving the final dictionary
    save_json(create_file_path('ApiStudentsDict.json', doctype= 1),studentAnswersDict)
    return studentAnswersDict



#*************** APP ***************
#app creation
def create_app():
    app = Flask(__name__)
    CORS(app)
    return app

app = create_app()

#get methods
@app.route('/plentasapi/', methods=['GET'])
def getData():
    response = {'message': 'Plentas API is running'}
    return jsonify(response)

#post methods
@app.route('/plentasapi/', methods=['POST'])

def processData():
    """
    This function triggers the evaluation of data, connecting the api with the Plentas tools
    Outputs:
        response.processApiData(): A list with indexed information about the students's evaluation 
    """
    #inputData = request.json  --- old version

    #getting the settings from the api
    configuration = request.form["configuration"]
    configuration_dict = json.loads(configuration)
    
    #saving the selected zip file
    try:
        uploadedFile = request.files['zipFile']
        uploadedFile.save(create_file_path("StudentAnswersZip/" + uploadedFile.filename, doctype= 1))
        fileName = uploadedFile.filename
    except:        
        p = pathlib.PureWindowsPath(configuration_dict["filepath"])
        filePath = str(p.as_posix())
        fileName = filePath.split("/") 
        fileName = fileName[-1]
        

    #getting our tuned settings
    config_json = load_json("configV2.json")

    #configuring plentas methodology
    response = Plentas(config_json[0], [answersTodict(create_file_path("StudentAnswersZip/" + fileName, doctype= 1)), createTeacherJson(configuration_dict)])
    #overwriting the custom settings for the settings from the api      
    response.setApiSettings(configuration)
   
    return jsonify(response.processApiData())


if __name__ == '__main__':
    app.run(debug=True)