import pandas as pd
import json
from utils import getIDrange
from tools import Ortografia, Sintaxis, Semantica, GetSettings
import copy



class Plentas():

    def __init__(self, config):
        self.settings = GetSettings(config)
    
    def processData(self):
        output_json=[]
        self.settings.answersDF = pd.DataFrame(self.settings.answersDF)
        IDs = getIDrange(self.settings.rango_ID, self.settings.answersDF)

        sintactics = Sintaxis()
        ortography = Ortografia()
        semantics = Semantica(self.settings.BusquedaKW, self.settings)  

        #print(f'AAAA {self.settings.rango_ID}')      

        for id in IDs:
            studentID = self.settings.answersDF['hashed_id'][id]
            self.settings.student_dict["ID"] = studentID

            respuesta_alumno_raw = self.settings.answersDF['respuesta'][id].lower()

            self.settings.nota_prof = self.settings.answersDF['nota'][id]
            self.settings.student_dict["Semantica"]["Nota profesor"] = self.settings.nota_prof

            self.settings.notas.append(self.settings.nota_prof)

            #print(f'{studentID}, {respuesta_alumno_raw}')       

            if self.settings.Sintaxis:
                sintactics.Analysis(self.settings, respuesta_alumno_raw)                

            if self.settings.Ortografia:
                ortography.Analysis(self.settings, respuesta_alumno_raw)              

            if self.settings.Semantica:
                semantics.Analysis(self.settings,studentID, respuesta_alumno_raw)

            output_json.append(copy.deepcopy(self.settings.student_dict))
                         
        if self.settings.Sintaxis:
            sintactics.saveResults(self.settings)                   

        if self.settings.Semantica:
            semantics.saveResults(self.settings)
            
        json_object = json.dumps(output_json, indent = 11, ensure_ascii= False) 
        with open(self.settings.json_file_out, "w") as outfile:
            outfile.write(json_object)
        
        return json_object

        