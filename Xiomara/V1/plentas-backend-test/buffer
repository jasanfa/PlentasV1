import pandas as pd


def getThreshold(df, flag = "NINGUNA", revisor =["Xiomara", "Javier"]):
    flag_list = pd.DataFrame()
    queue = []
    indx=0

    for person in revisor:
        for row in df[person]:
            if str(row).lower() == flag.lower() and not indx in queue:
                print(row, indx, df[person][indx])
                queue.append(indx)
            indx+=1
        indx= 0


    """
    for col in df:
        for row in df[col]:            
            if str(row).lower() == flag.lower() and not indx in queue:
                print(row, indx, df[col][indx])
                queue.append(indx)
            indx+=1
        indx= 0
    """




if __name__ == '__main__':
    df = pd.read_csv('identificación-mejor-linea-bi.csv', sep=';', header=None)
    getThreshold(df)
"""
print(df)
for el in df:
    print(df[el])
    for row in df[el]:
        print(row)
    break
"""

