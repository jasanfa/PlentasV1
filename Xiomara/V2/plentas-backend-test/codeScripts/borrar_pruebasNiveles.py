text = "<html><head></head><body><p>Profesor buenas tardes, </p>  <p>Adjunto solo los archivos en excel que me permitió subir la plataforma. El jupyter-notebook  no me lo permitió subir ni siquiera en formato html; envío todo estos dos últimos archivos a través de tutor.</p>  <p>Muchas gracias.</p></body></html>"

def removeHtmlFromString(string):
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
    return new_string

a=removeHtmlFromString(text)
print(a)