# Nombres: Juan Barrera & Katherine Barrera
# Universidad Politenica Salesina
#!/usr/bin/env python
# coding: utf-8

# ## Generación de una bolsa de palabras de manera Secuencial 
# ## Generación de una bolsa de palabras de manera Paralela con procesos 

# Carga de Dataset
##Funcion para cargar el dataset atraves de un path en donde se encuentra el archivo .csv
##nombre de van a tener las columnas atraves de nameColumns, el arhcivo esta separado mediante ','
def cargaDataSet(path, nameColumns):
    df = pd.read_csv(path, encoding='utf-8', sep=',', low_memory=False, header=None, names=nameColumns)
    #Obtencion de muestra del dataset de manera randomica para generacion de grafica. 
    #df = df.sample(frac=0.90, random_state=10)
    #df = df.sample(frac=0.75, random_state=10)
    #df = df.sample(frac=0.50, random_state=10)
    #df = df.sample(frac=0.25, random_state=10)
    #df = df.sample(frac=0.10, random_state=10)
    #df = df.sample(frac=0.05, random_state=10)
    
    #Elimnacion de filas que contienen campos vacios.
    df = df.dropna()
    #Pasamos la columna que contiene el comentario de los productos de amazon 'reviewText'a minusculas. 
    df["reviewText"]=df["reviewText"].str.lower()
    #Remplazmos los caracteres especiales que contenga la columna 'reviewText' mediante regex y los remplazmos con un espacio
    df['reviewText'].replace(regex=True, inplace=True, to_replace=r"@'[^\w\s.!@$%^&*()\-\/]+'", value=r' ')
    #Remplazmos los caracteres especiales que contenga la columna 'review' mediante regex y los remplazmos con un espacio
    df['review'].replace(regex=True, inplace=True, to_replace=r"@'[^\w\s.!@$%^&*()\-\/]+'", value=r' ')
    #Ordenamos el dataset de menor a mayor respecto a la columna 'score' del 1 a 5
    df = df.sort_values(["score"])
    #Se resetea el index del dataset para empezar desde 1 hasta 2999924
    df=df.reset_index(drop=True)

    print(df.shape)
    print(df.score.value_counts())
    return df

##Esta funcion nos permitira dividir el dataset completo en subgrupos dependiendo del identificador 
##En este caso se la columna 'score' tiene valores numericos del 1-5, por lo tanto se dividira en 5 grupos
def separacionDataSet(df, columna, identificador):
    # Guardamos un dataframe con valores booleados de las filas que cumplen con la condicion 
    # si la fila seleccionada tiene el valor de 'score' = al de identificador entonces se guarda un true 
    # de lo contrario se almacena false
    is_score = df.loc[:, columna] == identificador
    # Obtenemos las filas que tengan true y guardamos en un dataframe y retornamos este dataframe
    df_grupo = df.loc[is_score]
    return df_grupo

## Esta funcion nos permite contar las palabras repetidas que se encuntre en el dataframe que se pasa por parametro
## ademas de esto se revice el nombre del dataset con el se que se trabaja. 
def countWords(dataGrupo, grupoName):    
    #Creacion de lista en blanco para almacenar las palabras recuperadas. 
    listaTexto=[]
    #Del dataframe que nos pasan por parametro, obtenemos la columna reviewText, le convertimos en string 
    #y seperamos en palabras que se almacena en texto
    for texto in dataGrupo.reviewText.str.split(): 
        #Concatenamos con todas las filas del dataframe
        listaTexto += texto
    #Ahora simplemente convertimos la lista de palabras a una coleccion de tipo counter 
    # Esto nos facilita encontrar las palabras mas repetidas en toda la lista que obtuvimos
    # En este caso nos intersa saber las 20 primeras. 
    print("--------------------",grupoName,"----TOP 20----------------------------\n", str(Counter(listaTexto).most_common(20)))
    

#Esta funcion nos permite verificar que las palabras no se encuntren dentro de las stopwords        
def obtenerValoresPorGrupos(datasetGrupo, grupoName):  
    #Se hace uso de una funcion lambda en donde se obtiene los registros de la columna 'reviewText'
    #se hace una separacion por palabras del oracion que tenga el registro de la columna 'reviewText'
    #esta palabra se compara con la lista de stopword defina y si el resultado es true entonces se 
    #concatena con un espacio dentro del mismo registro. 
    datasetGrupo["reviewText"] = datasetGrupo["reviewText"].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    #LLamada a la funcion conteo de palabras se pasa el nuevo dataset sin stopwords
    countWords(datasetGrupo, grupoName)
    



#Importación de librerías
#from do_something import do_it_now
import time
import multiprocessing
import numpy as np
import pandas as pd
## Importacion de paquetes para procesamiento de Lenguaje natural
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from collections import Counter
from mpi4py import MPI


stop =stopwords.words("english")

#Funcion principal del programa
if __name__ == "__main__":

    #Con esto apagamos los mensajes de warning de pandas 
    pd.options.mode.chained_assignment = None
    #El comunicador define un grupo de procesos que pueden comunicarse entre sí.
    comm=MPI.COMM_WORLD
    #La identificación de un proceso se basa en rangos. A cada proceso se le 
    #asigna un rango para cada comunicador al que pertenece
    rank = comm.rank

    #print("\n***********************MPI",rank,"***************************")

    #Definicion del proceso con un rango global de 0 como el proceso maestro
    if rank==0:
        #Descarga de stopwords
        nltk.download('stopwords')
        porter = PorterStemmer()
        #Adicion de palabras comunes del idioma ingles
        stop.append("i")
        stop.append("the")
        stop.append("you")
        stop.append("he")
        stop.append("she")
        stop.append("it")
        stop.append("we")
        stop.append("they") 
        stop.append(".") 
        stop.append("i'm") 
        stop.append("he's")
        stop.append("she's") 
        stop.append("it's")
        stop.append("we're")
        stop.append("you're")
        stop.append("they're")

        
        #Llamada a funcion de carga de dataset, paso de path y nombre de columnas
        data = cargaDataSet('amazon_review_full_csv/train.csv', ['score', 'review', 'reviewText'])
        #Creacion de lista de la cantidad de procesos que se van a realizar
        destination_process = [1,2,3,4,5]

        #Recorrido de la lista mediante for para envio de mensajes
        for i in destination_process:
            #Envio de parametros para los destinatarios 
            #Envio de dataset para cada procesador
            comm.send(data,dest=i)

    #Destino identificado como numero 1
    if rank==1:
        #Se recibe el mensaje enviado desde rank=0, almacenamos en data
        data=comm.recv(source=0)
        #Separacion de los distintos puntajes que posee la columna score del 1-5
        df_grupo1 = separacionDataSet(data, 'score', 1)
        #LLamada para obtener palabras
        obtenerValoresPorGrupos(df_grupo1, ("Dataset Grupo 1"))

    #Destino identificado como numero 2
    if rank==2:
        
        data=comm.recv(source=0)
        #Separacion de los distintos puntajes que posee la columna score del 1-5
        df_grupo2 = separacionDataSet(data, 'score', 2)
        obtenerValoresPorGrupos(df_grupo2, ("Dataset Grupo 2"))

    #Destino identificado como numero 3  
    if rank==3:
        data=comm.recv(source=0)
        #Separacion de los distintos puntajes que posee la columna score del 1-5
        df_grupo3 = separacionDataSet(data, 'score', 3)
        obtenerValoresPorGrupos(df_grupo3, ("Dataset Grupo 3"))
    
    #Destino identificado como numero 4
    if rank==4:
        data=comm.recv(source=0)
        #Separacion de los distintos puntajes que posee la columna score del 1-5
        df_grupo4 = separacionDataSet(data, 'score', 4)
        obtenerValoresPorGrupos(df_grupo4, ("Dataset Grupo 4"))

    #Destino identificado como numero 5
    if rank==5:
        data=comm.recv(source=0)
        #Separacion de los distintos puntajes que posee la columna score del 1-5
        df_grupo5 = separacionDataSet(data, 'score', 5)
        obtenerValoresPorGrupos(df_grupo5, ("Dataset Grupo 5"))    