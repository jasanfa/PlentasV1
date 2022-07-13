import sys
sys.path.append("utils/Semantics/")

#from SentenceTransformer2 import *
from SentenceTransformer_nminipregunta import *
#PreparingDataSet()
#SentTransf_train()
prueba = SentTransf_test()

print(prueba.similarity("La célula es la unidad morfológica y funcional de todo ser vivo. La célula es el elemento de menor tamaño que puede considerarse vivo. Puede clasificarse a los organismos vivos según el número de células que posean: si solo tienen una, se les denomina unicelulares; si poseen más, se les llama pluricelulares.", "La célula es la unidad morfológica y funcional los seres vivos. Es el elemento de menor tamaño vivo. Los organismos vivos se clasifican según el número de células en unicelulares, si solo tienen una, o en pluricelulares, si tienen más."))

print(prueba.similarity("La célula es la unidad morfológica y funcional de todo ser vivo. La célula es el elemento de menor tamaño que puede considerarse vivo. Puede clasificarse a los organismos vivos según el número de células que posean: si solo tienen una, se les denomina unicelulares; si poseen más, se les llama pluricelulares.", "La célula es la unidad morfológica y funcional los seres vivos. Es el elemento de menor tamaño vivo. Los organismos vivos se clasifican según el número de células en unicelulares, si solo tienen una, o en pluricelulares, si tienen más."))

