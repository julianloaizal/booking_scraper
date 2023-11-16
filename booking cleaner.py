import numpy as np
import pandas as pd
import re
import unidecode

# Se importan los DataFrames y se combinan
df = pd.read_excel(r".\BORRAR_hotels_list_ensayo.xlsx")#("C:/Users/DELL/Esteban/Web Scraping/booking_scraper/python/hotels_list.xlsx")
df_coord = pd.read_excel("./coordenadas.xlsx")
df = df.merge(df_coord[['Código','Municipio','Subregión',"Latitud","Longitud"]],on = 'Municipio', how = 'left')

# FUNCIONES

def desayuno(texto):
    """
    Identifica si un hotel incluye desayuno y lo convierte en 1 o de lo contrario en 0.

    Parameters:
        texto (str): El texto en el que se busca la presencia de "Desayuno" o "desayuno".

    Returns:
        int: Devuelve 1 si "Desayuno" o "desayuno" está presente en el texto, de lo contrario, devuelve 0.
    """
    if "Desayuno" in texto or "desayuno" in texto:
        return 1
    else:
        return 0
    
    
def extraer_numeros(valor):
    """
    Extrae un número decimal de un texto que contiene una etiqueta y un número.

    Parameters:
        valor (str): El texto que contiene la etiqueta y el número.

    Returns:
        float o nan: El número decimal extraído del texto. Retorna nan si no se encuentra un número válido.
    """
    # Utiliza una expresión regular para buscar números en el valor
    numeros = re.findall(r'\d+[,.]?\d*', valor)
    
    # Si se encuentran números, toma el primer número
    if numeros:
        # Reemplaza la coma por un punto para que Python lo reconozca como decimal
        numero = numeros[0].replace(',', '.')
        return float(numero)
    else:
        return np.nan
    
def distancia_metros(valor):
    """
    Extrae de un texto un número con unidad (m o km) y lo convierte a m.

    Parameters:
        valor (str): El texto que contiene el número con unidad.

    Returns:
        float o nan: Número correspondiente a la distancia en m.
        Retorna nan si no se encuentra un número con unidad válido.
    """
    # Utiliza una expresión regular para buscar números con unidad en el valor
    matches = re.findall(r'(\d+[,.]?\d*)\s*(km|m)', valor, re.IGNORECASE)

    if matches:
        numero, unidad = matches[0]
        # Reemplaza la coma por un punto en el número para que Python lo reconozca como decimal
        numero = numero.replace(',', '.')
        numero = float(numero)
        if unidad == 'km':
            numero *= 1000
        return numero
    else:
        return np.nan
    
def acomodacion(texto):

    """
    Extrae de un texto el tipo de acomodación y lo clasifica en dos
    columnas según su tipo y característica.

    Parameters:
        texto (str): Corresponde al texto de información de la habitación.

    Returns:
        tuple: Tupla correspondiente al tipo de acomodación y su característica.
    """

    apto = re.findall(r'\A(apartamento|casa|estudio|loft)', texto ,re.IGNORECASE)
    otro = re.findall(r'\A(bungalow|chalet|tienda|villa|cabaña)', texto ,re.IGNORECASE)
    hab = re.findall(r'(doble|compartida|cu.druple|deluxe|est.ndar|familiar|suite|triple)', texto ,re.IGNORECASE)

    if re.findall(r'\A(habitaci.n|suite|camarote|cama)|room', texto ,re.IGNORECASE):
        if hab:
            return ("habitacion",unidecode.unidecode(hab[0].lower()))
        else:
            return ("habitacion","estandar")

    elif apto:
        if apto[0] == 'Apartamento':
            return("apartamento","estandar")
        else:
            return ("apartamento",apto[0].lower())
    elif otro:
        return ("otro", otro[0].lower())
    elif texto == "":
        return (np.nan,np.nan)
    else:
        # return texto
        return ("otro", "otro")
    
def baño(texto):

    """
    Extrae de un texto si se especifica baño compartido o privado y retorna un valor
    de 0 para el primero y de 1 para el segundo.

    Parameters:
        texto (str): Corresponde al texto de información de la habitación.

    Returns:
        int o np.nan: Retorna 0 en caso de especificar baño compartido, 1 para baño privado
                   y nan para valores sin información de baño.
    """

    if re.search(r'baño', texto, re.IGNORECASE):
        if re.search(r'compartido', texto, re.IGNORECASE):
            return 0
        else: 
            return 1
    else:
        return np.nan

def dormitorios(texto):

    """
    Extrae de un texto si se especifica la palabra dormitorio o dormitorios y retorna 
    el número de estos o el valor nan en caso de no especificarse.

    Parameters:
        texto (str): Corresponde al texto de información de la habitación.

    Returns:
        list: Retorna una lista con el número de dormitorios en caso de especificar o de lo contrario
        retorna nan.
    """

    if re.findall(r'(dormitorio|dormitorios)', texto, re.IGNORECASE):
        return int(re.findall(r'\d', texto, re.IGNORECASE))
    else:
        return ([np.nan])
    


# LIMPIEZA INICIAL

    # Se eliminan los caracteres comunes "['']" en las columnas que los incluyen

cols = ['score','avg review','reviews count','comfort','distancia del centro',
        'nivel de sostenibilidad','información habitación','Desayuno incluido',
        'Cancelación incluida']
for col in cols:
    df[col] = (df[col].str.replace(r"['\[\]]", '', regex=True))


# Se eliminan los "." como separadores de decimales

cols = ['price','score','reviews count']
for col in cols:
    df[col] = (df[col].str.replace(".","",regex=False))

# Se hacen los cambios necesarios para terminar de limpiar los valores de las columnas

df['price'] = pd.to_numeric(df['price'].str.replace('COP','').str.strip())
df['score'] = pd.to_numeric(df['score'].str.replace(",","."))
df['reviews count'] = pd.to_numeric(df['reviews count'].str.replace(r'\b(comentario|comentarios)\b', '', regex=True))
# df['nivel de sostenibilidad'] = df['nivel de sostenibilidad'].str.replace("Travel Sustainable Nivel ","")
df['nivel de sostenibilidad'] = df['nivel de sostenibilidad'].apply(extraer_numeros)
df['Desayuno incluido'] = df['Desayuno incluido'].apply(desayuno)
df['comfort'] = (df['comfort'].apply(extraer_numeros))
df['Cancelación incluida'] = df['Cancelación incluida'].map({
                                                            'Cancelación gratis, Sin pago por adelantado': 2,
                                                            'Cancelación gratis': 1,'': 0})



# COLUMNAS NUEVAS

# Las siguientes columna se crea con el fin de tener una referencia para eliminar los duplicados

df["Origen_ref"] = df["distancia del centro"].apply(lambda x: x.split()[-1])

df['distancia origen m'] = df['distancia del centro'].apply(distancia_metros)

df['origen'] = np.where(df['Origen_ref'] == 'centro', 0, 1)

# Se crean columnas para tipo de acomodación y características

df["acomodacion"] = (df["información habitación"].apply(acomodacion)).apply(lambda x: x[0])
df["caracteristica"] = (df["información habitación"].apply(acomodacion)).apply(lambda x: x[1])

# Columna para especificar baño privado (1) o baño compartido (0)

df['baño'] = df['información habitación'].apply(baño)

#Columna con número de dormitorios

df['dormitorios'] = df['información habitación'].apply(dormitorios).apply(lambda x: x[0])

# Se reorganizan las columnas
df = df.iloc[:,[0,1,2,3,4,5,6,19,18,20,11,7,8,21,22,23,24,9,10,12,13,14,15,16,17]]

# FILAS DUPLICADAS

# Se genera referencia de shape antes de la limpieza
shape_df_pre = df.shape
shape_df_pre

"""
Primero se eliminan las filas donde se repite el nombre del hotel y el municipio. 
Se usan estos parámetros ya que los duplicados ocasionalmente varían en url y esto
impide que se identifiquen correctamente los duplicados por municipio. 
"""

df.drop_duplicates(subset = ('hotel','Municipio'), inplace = True)

# Para los hoteles que tiene "distancia al centro", se conserva esta fila y se eliminan las demás

#Primero, se encuentran los hoteles duplicados que incluyen el valor 'distancia al centro'
a = df[df['hotel'].duplicated(keep = False)]
con_centro = a.groupby('hotel')['origen'].apply(lambda x: 0 in x.values)
con_centro = con_centro[con_centro].index.tolist()

# Luego, Con los nombres de estos hoteles, se seleccionan los que no corresponden a centro (1) y se eliminan, conservando los que sí (0).
duplicados_centro = df[df['hotel'].isin(con_centro)].sort_values(by = 'origen').duplicated(subset='hotel')
duplicados_centro = duplicados_centro[duplicados_centro].index
df.drop(duplicados_centro, inplace = True)

"""
__________________________________________________________________________________________________________________
Esto se podría borrar
"""
# Se elimina el resto de duplicados con respecto a la distancia al origen
duplicados_otros = df.loc[df.duplicated(subset='hotel')].sort_values(by=['hotel','distancia origen m']).index
df.drop(duplicados_otros,inplace = True)

"""
___________________________________________________________________________________________________________________
"""
print(f"Se eliminaron en total {shape_df_pre[0]-df.shape[0]} filas")

# Se reinician los índices
df.reset_index(drop=True,inplace=True)

# BORRAR COLUMNAS INNECESARIAS

# Se borran las columnas que ya no se necesitan

df.columns
df.drop(['distancia del centro','Origen_ref','origen','información habitación'],axis=1, inplace=True)

# ASIGNAR TIPO DE DATOS A COLUMNAS

# df[['hotel',
#      'avg review',
#      'Municipio',
#      'url',
#      'Subregión']] = df[['hotel',
#                           'avg review',
#                           'Municipio',
#                           'url',
#                           'Subregión']].astype(str)

# df[['price', 
#     'reviews count', 
#     'distancia origen m', 
#     'Desayuno incluido', 
#     'Cancelación incluida',
#     'Código',
#     'nivel de sostenibilidad']] = df[['price', 
#                                         'reviews count', 
#                                         'distancia origen m', 
#                                         'Desayuno incluido', 
#                                         'Cancelación incluida',
#                                         'Código',
#                                         'nivel de sostenibilidad']].astype(int)

# df[['score', 
#     'comfort', 
#     'Latitud', 
#     'Longitud']] = df[['score', 
#                         'comfort', 
#                         'Latitud', 
#                         'Longitud']].astype(int)

# SEPARACIÓN DATASETS

# Se generan dos datasets, uno para Medellín y el otro para el resto de municipios
df_med = df.loc[df['Municipio'] == 'MEDELLIN'].reset_index(drop=True)
df_ant = df.loc[df['Municipio'] != 'MEDELLIN'].reset_index(drop=True)

# EXPORT

# Se exportan ambos datasets como un libro de excel con dos hojas
with pd.ExcelWriter('booking_clean.xlsx') as writer:
    df_ant.to_excel(writer, sheet_name='Antioquia')
    df_med.to_excel(writer, sheet_name='Medellin')

# fin = time.time()
# print(f"Tiempo ejecución: {fin-inicio:.2f} segundos")