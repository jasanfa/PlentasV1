from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from plentas import Plentas


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
    # aquí va toda la magia, en inputData están los datos de entrada
    response = Plentas(inputData) 
    
     #{'message': 'success'}
    response2 = response.processData() 
    return response2


if __name__ == '__main__':
    app.run(debug=True)

