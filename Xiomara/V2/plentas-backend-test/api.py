from urllib import response
from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from hashids import Hashids
import zipfile
import os
from codeScripts.utils import save_json, load_json
from plentas import Plentas


#from plentas import Plentas

a = "aaa"
e = 0

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

def create_custom_file_path(file):
    path = "api/StudentAnswersZip/" + file
    return path

def extractZipData(ruta_zip):
    ruta_extraccion = "api/StudentAnswers/"
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

    """
    for work_folder in os.listdir("api/StudentAnswers"):
        for student, indx in zip(os.listdir("api/StudentAnswers/" + work_folder), range(len(os.listdir("api/StudentAnswers/" + work_folder)))):
            try:
                studentAnswersDict[hashids.encode(indx)] = dict()
                studentAnswersDict[hashids.encode(indx)]["indx"] = indx
                fichero = open("api/StudentAnswers/" + work_folder + "/" + student + "/" + 'comments.txt')
                lineas = fichero.readlines()
                studentAnswersDict[hashids.encode(indx)]["respuesta"] = lineas
            except:
                continue
    """
    studentAnswersDict = []
    for work_folder in os.listdir("api/StudentAnswers"):
        for student, indx in zip(os.listdir("api/StudentAnswers/" + work_folder), range(len(os.listdir("api/StudentAnswers/" + work_folder)))):
            try:
                fichero = open("api/StudentAnswers/" + work_folder + "/" + student + "/" + 'comments.txt')
                lineas = fichero.readlines()                                
                studentAnswersDict.append({"respuesta":lineas[0], "hashed_id":hashids.encode(indx), "TableIndex":indx}) 
            except:
                continue
    save_json("api/ApiStudentsDict.json", studentAnswersDict)
    return studentAnswersDict


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
    uploadedFile.save(create_custom_file_path(uploadedFile.filename))
    
    config_json = load_json("config.json")
    response = Plentas(config_json[0], [answersTodict(create_custom_file_path(uploadedFile.filename)), fake_file])    
    response.setApiSettings(configuration)
   

    return jsonify(response.processApiData())
        
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
