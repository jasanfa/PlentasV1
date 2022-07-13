import pandas as pd
import json
def char_split(word, character):
    palabra1=""
    palabra2=""
    found = 0
    for w in word:
        if w == character and not found:
            found = 1
        else:
            if not found:
              palabra1 = palabra1 + w
            else:
              palabra2 = palabra2 + w

    return [palabra1, palabra2]
def clean_words(string):
    words_sentence = []
    for w in string:
      if not w.isalnum():
        if char_split(string, w)[0] != "":
            words_sentence.append(char_split(string, w)[0])
        string = char_split(string, w)[len(char_split(string, w))-1]

    if string != "":
        words_sentence.append(string)
    return words_sentence
 
df = pd.read_excel(open('Jacobo/Metodos - analisis por minipregunta/notas-parciales.xlsx', 'rb'))
 
df2 = pd.read_excel(open('Jacobo/Metodos - analisis por minipregunta/metodos-de-captura.xlsx', 'rb'))
 

outcast_list = ["02224902_20210320213352"]

def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

students_dataset = dict()

tengo = []

cnt = 0
for name, ap1, ap2, respm1, respm2, respm3, respm4 in zip(df["nombre"], df["ap1"],df["ap2"],df["D3.1"],df["D3.2"],df["D3.3"],df["D3.4"]):
    #print(name + " " + ap1 + " " + ap2)
    name1 = name + " " + ap1 + " " + ap2
    if name1 == "Jose Sanchez-Runde Gavaldà":
        name1 = "José Javier Sánchez-Runde Gavaldà"
    for student, identificador, respuesta in zip(df2["nombre"], df2["identificador"],df2["respuesta"]):
        if normalize(student.lower()) == normalize(name1.lower()) or str(identificador) in outcast_list:
            #print(student)
            students_dataset[identificador] = dict()
            students_dataset[identificador]["respuesta_completa"] = respuesta

            print(respuesta)

            students_dataset[identificador]["m1_score"] = respm1
            students_dataset[identificador]["m2_score"] = respm2
            students_dataset[identificador]["m3_score"] = respm3
            students_dataset[identificador]["m4_score"] = respm4

            students_dataset[identificador]["resp_m1"] = ""
            students_dataset[identificador]["resp_m2"] = ""
            students_dataset[identificador]["resp_m3"] = ""
            students_dataset[identificador]["resp_m4"] = ""

            if identificador in outcast_list:
                outcast_list.remove(identificador)

            cnt+=1

            tengo.append(name1)
            break
        

print(cnt)


with open("__appcache__/metodos-de-captura-conNota-Anon.json", "r", encoding="utf8") as f:
    data = json.loads("[" + f.read().replace("}\n{", "},\n{") + "]")


cnt = 0
list_identif = []
for student in data:
    #print(student["hashed_id"])
    for identificador in students_dataset.keys():
        #print(students_dataset[identificador]["respuesta_completa"][:70].lower())
        if students_dataset[identificador]["respuesta_completa"][:70].lower() == student["respuesta"][:70].lower():
            students_dataset[identificador]["hashed_id"] = student["hashed_id"]
            list_identif.append(identificador)
            cnt+=1
            break

json_object = json.dumps(students_dataset, indent = 11, ensure_ascii=False) 
    # Writing output to a json file
with open("Metodos_Filtrado_ScoreporMinipregunta.json", "w", encoding="utf-8") as outfile:
    outfile.write(json_object)

