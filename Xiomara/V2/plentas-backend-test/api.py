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

#fake fale is the file that represents the folder that teachers should upload with question-answer baseline
fake_file = {
		"enunciado": "Describe, en menos de 200 palabras, la importancia del gobierno del dato en la empresa. Tu respuesta, que debe ser una redacción y no un listado, debe contener la respuesta a las siguientes preguntas: ¿qué debe abarcar el gobierno del dato?, ¿cuál es el nuevo ciclo de vida del dato?,¿quién debe liderar este tipo de estrategias?,¿cómo se puede beneficiar la empresa?,¿cómo se beneficia el cliente?",
		"minipreguntas": [
			{
				"minipregunta": "¿qué debe abarcar el gobierno del dato? ",
				"minirespuesta": "El gobierno del dato permite a las empresas gestionar sus datos (disponibilidad, integridad, usabilidad y seguridad), convertirlos en información y posteriormente en conocimiento para una mejor toma de decisiones, repercutiendo así en beneficios competitivos."
			},
			{
				"minipregunta": "¿cuál es el nuevo ciclo de vida del dato?",
				"minirespuesta": "Para transformar la información en conocimiento, los datos deben ser confiables, oportunos, completos y accesibles. El dato tiene un ciclo de vida que incluye las siguientes etapas: captura, almacenamiento, modificación, uso, gestión, protección y borrado."
			},
			{
				"minipregunta": "¿quién debe liderar este tipo de estrategias?",
				"minirespuesta": "La estrategia de gobierno del dato debe ser liderada por la empresa, debería existir una oficina de gobierno, tener un conjunto de procedimientos y un plan para ejecutar dichos procedimientos."
			},
			{
				"minipregunta": "¿cómo se puede beneficiar la empresa? ¿cómo se beneficia el cliente?",
				"minirespuesta": "El cambio de mentalidad y de organización contribuye a la digitalización de la empresa, protección de los datos, procesos más eficientes, se agiliza la toma de decisiones que repercute en una mejor atención al cliente."
			}
		],
		"keywords": [
			"gobierno del dato",
			"lidera la empresa",
			"protección del dato",
			"borrado del dato",
			"toma de decisiones"
		]
	}


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
            try:
                #opening the file
                fichero = open(create_file_path("StudentAnswers/" + work_folder + "/" + student + "/" + 'comments.txt', doctype= 1))
                #reading it
                lineas = fichero.readlines()
                #saving it                                
                studentAnswersDict.append({"respuesta":lineas[0], "hashed_id":hashids.encode(indx), "TableIndex":indx}) 
            except:
                continue

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
        
    
    print("EEEEEEEEEEEEEEEEEEEE")
    print(fileName)
    

    #getting our tuned settings
    config_json = load_json("config.json")

    print(createTeacherJson(configuration))
    print("\n\n\n")
    #configuring plentas methodology
    response = Plentas(config_json[0], [answersTodict(create_file_path("StudentAnswersZip/" + fileName, doctype= 1)), createTeacherJson(configuration_dict)])
    #overwriting the custom settings for the settings from the api      
    response.setApiSettings(configuration)
   
    return jsonify(response.processApiData())


if __name__ == '__main__':
    app.run(debug=True)
