from urllib import response
from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
#from plentas import Plentas

a = "aaa"
e = 0

responses = [
           { '0' : {
                      "ID": "9J4q2VolejRejNmGQBW7",
                      "Ortografia": {
                                 "Errores ortograficos": [
                                            3,
                                            "cpu pates cpu "
                                 ],
                                 "Nota en Ortograf�a": 0.12000000000000001
                      },
                      "Sintaxis": {
                                 "Frases utilizadas para responder a la pregunta": 5,
                                 "Palabras utilizadas para responder a la pregunta": 33,
                                 "Index Fernandez Huerta": 65.931,
                                 "Legibilidad F-H": "adecuado",
                                 "mu index": 40.614,
                                 "Legibilidad Mu": "dif�cil",
                                 "Nota en Sintaxis": 0.21309
                      },
                      "Semantica": {
                                 "Keywords alumno (auto)": [
                                            "componentes mas importantes",
                                            "instrucciones recibidas",
                                            "componentes mas",
                                            "mas importantes",
                                            "encarga de procesar"
                                 ],
                                 "Keywords alumno": [
                                            [
                                                       "Instrucci�n"
                                            ],
                                            "Nota: 0.17"
                                 ],
                                 "Keyword profesor": [
                                            "CPU",
                                            " Unidad de procesamiento",
                                            " Unidad de control",
                                            " Secuencial",
                                            " Registros",
                                            " Instrucci�n"
                                 ],
                                 "Justificaci�n de esos keywords": [
                                            "La palabra instrucci�n aparece en el texto y es una forma de expresar la palabra clave Instrucci�n, pero su significado puede no ser el adecuado"
                                 ],
                                 "Nota en Semantica": 0.18400000000000002,
                                 "Nota profesor": 0.25
                      }
           }
           },
           { '1': {
                      "ID": "1gO3GWpmbk5ezJn4KRjL",
                      "Ortografia": {
                                 "Errores ortograficos": [
                                            3,
                                            "cpu cpu boole "
                                 ],
                                 "Nota en Ortograf�a": 0.12000000000000001
                      },
                      "Sintaxis": {
                                 "Frases utilizadas para responder a la pregunta": 4,
                                 "Palabras utilizadas para responder a la pregunta": 94,
                                 "Index Fernandez Huerta": 72.287,
                                 "Legibilidad F-H": "ligeramente f�cil",
                                 "mu index": 37.291,
                                 "Legibilidad Mu": "dif�cil",
                                 "Nota en Sintaxis": 0.21915600000000002
                      },
                      "Semantica": {
                                 "Keywords alumno (auto)": [
                                            "ingl�s lo indican",
                                            "central de procesamiento",
                                            "siglas en ingl�s",
                                            "unidad central",
                                            "unidad"
                                 ],
                                 "Keywords alumno": [
                                            [
                                                       "Instrucci�n",
                                                       "Unidad de control"
                                            ],
                                            "Nota: 0.33"
                                 ],
                                 "Keyword profesor": [
                                            "CPU",
                                            " Unidad de procesamiento",
                                            " Unidad de control",
                                            " Secuencial",
                                            " Registros",
                                            " Instrucci�n"
                                 ],
                                 "Justificaci�n de esos keywords": [
                                            "La palabra instrucci�n aparece en el texto y es una forma de expresar la palabra clave Instrucci�n, pero su significado puede no ser el adecuado",
                                            "La expresi�n clave Unidad de control aparece correctamente empleada en el texto"
                                 ],
                                 "Nota en Semantica": 0.21600000000000003,
                                 "Nota profesor": 1.0
                      }
           }
           },
           { '2':{
                      "ID": "gLPQZOpnel5aKBzyVXvA",
                      "Ortografia": {
                                 "Errores ortograficos": [
                                            13,
                                            "cpu instruciones hardware entendible cpu ejecucion rapido efficiente ejecucion intrucciones cpu entiden codigo "
                                 ],
                                 "Nota en Ortograf�a": 0
                      },
                      "Sintaxis": {
                                 "Frases utilizadas para responder a la pregunta": 2,
                                 "Palabras utilizadas para responder a la pregunta": 67,
                                 "Index Fernandez Huerta": 78.422,
                                 "Legibilidad F-H": "ligeramente f�cil",
                                 "mu index": 41.574,
                                 "Legibilidad Mu": "dif�cil",
                                 "Nota en Sintaxis": 0.239992
                      },
                      "Semantica": {
                                 "Keywords alumno (auto)": [
                                            "permite recibir instruciones",
                                            "entendible al computador",
                                            "unidad de procesamiento",
                                            "permite recibir",
                                            "recibir instruciones"
                                 ],
                                 "Keywords alumno": [
                                            [
                                                       "Instrucci�n",
                                                       "Unidad de procesamiento"
                                            ],
                                            "Nota: 0.33"
                                 ],
                                 "Keyword profesor": [
                                            "CPU",
                                            " Unidad de procesamiento",
                                            " Unidad de control",
                                            " Secuencial",
                                            " Registros",
                                            " Instrucci�n"
                                 ],
                                 "Justificaci�n de esos keywords": [
                                            "La palabra instrucci�n aparece en el texto y es una forma de expresar la palabra clave Instrucci�n, pero su significado puede no ser el adecuado",
                                            "La expresi�n clave Unidad de procesamiento aparece correctamente empleada en el texto"
                                 ],
                                 "Nota en Semantica": 0.21600000000000003,
                                 "Nota profesor": 0.25
                      }
           }
           },
]



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
    inputData = request.json
    print(inputData)
    #response = {'message': 'Plentas API is running', 'message2': 'Plentas API2 is running', 'message3': 'Plentas API3 is running'}    
    return jsonify(responses)
    #return responses_dict
    
    # aquí va toda la magia, en inputData están los datos de entrada
    #response = Plentas(inputData) 
    
     #{'message': 'success'}
    #response2 = response.processData() 
    #return response2


if __name__ == '__main__':
    app.run(debug=True)

