# -*- coding: utf-8 -*-
import io, json
import telebot
import MySQLdb
import re
from Usuario import Usuario
import csv, os, json
from time import sleep
import io, json
from telebot import types
from lxml import html
import csv, os, json
import requests
from exceptions import ValueError
import urllib2
from bs4 import BeautifulSoup
import io, json


#Variables necesarias para conexión y uso del bot
TOKEN = '407510413:AAFIYZBxBF1mAUK1w0qPnBGU-rts5dJ-II8'
bot = telebot.TeleBot(TOKEN)
connection = MySQLdb.connect (host = "localhost",
                              user = "root",
                              passwd = "root",
                              db = "findpricesbot")

cursor = connection.cursor(MySQLdb.cursors.DictCursor)
#Fin variables necesarias para conexion

global usuario, current_path
usuario=Usuario() #Usuario a editar
current_path=os.path.dirname(os.path.abspath(__file__))+"\JsonFiles\\" #ruta a la carpeta de Json



def checkFile(chat_id, name):


    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute("Select id, Nombre from Usuarios where id="+str(chat_id)+";")
        row = cursor.fetchall()
        if row:

            for resultado in row:
                usuario.setId(resultado["id"])
                usuario.setNombre(resultado["Nombre"])

                print "%s, %s" % (resultado["id"], resultado["Nombre"])
                bot.send_message(chat_id,"Bienvenido a FindPricesBot.")
                lectura(chat_id, usuario)
        else:
            # Abre archivo en modo escritura e insertamos la id en el fichero
            print "entro en else"
            cursor.execute("INSERT INTO Usuarios(id, Nombre) VALUES('"+str(chat_id)+"', '"+name+"');")
            connection.commit()
            print "Usuario insertado a archivo.\n"
            try:
                file =open(current_path + str(chat_id) + ".json", 'r')
            except :
                extracted_data = []
                file = open(current_path + str(chat_id) + ".json", 'w')
                json.dump(extracted_data, file, indent=4)
            file.close()

            bot.send_message(chat_id, "Bienvenido a FindPricesBot\nPara insertar un nuevo producto, simplemente pegue la url del producto deseado.")
        cursor.close()
        connection.close()
    except:
        print "error doble /start"



def lectura(chat_id, usuario):
#Cargamos la lista del json del usuario
    listado_productos=current_path+str(chat_id)+".json"
    print "el listado es -> "+listado_productos
    try:
        leer = json.loads(open(listado_productos).read())
        for i in range(0, len(leer)):
            usuario.setInitialList(leer[i])
        print "Archivo de datos cargado a memoria \n"
        bot.send_message(chat_id, "Archivo de datos cargado a memoria.")
        print usuario.getInitialList()
    except:
        print "No es posible abrir el archivo"


def insertar(url_producto, chat_id, mensaje):

    usuario.setAsinList(url_producto)
    #print usuario.getAsinList()
    bot.send_message(chat_id, "Producto insertado al listado, obteniendo datos del producto...")

    lista_return = Scraping(url_producto, mensaje)
    # metemos cada lista en una lista global llamada inicial
    usuario.setInitialList(lista_return)
    exportar(chat_id)


def obtenerPrecios(mensaje):
    if len(usuario.getAsinList()) == 0:
        print "error lista vacia"
        bot.send_message(mensaje.chat.id, 'La lista esta vacia, debe insertar productos previamente pasandome el enlace completo EJ: http//www.XXX.es a amazon/gearbest/pccomponentes')
    else:
        ReadAsin(mensaje)


def ReadAsin(mensaje):

    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Espere mientras cargo los datos del producto solicitado...')
    for i in usuario.getAsinList():
        url = i  # Pasamos las urls de la Lista
        # Lista_return obtendra la lista creada en la funcion scraping
        lista_return = Scraping(url, mensaje)
        # metemos cada lista en una lista global llamada inicial
        usuario.setInitialList(lista_return)
        sleep(5)
    bot.send_message(mensaje.chat.id, 'Finalizada la obtención inicial de precios')


def Scraping(url, mensaje):

    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
    if url.find('banggood') != -1 :
        req = urllib2.Request(url, headers=headers)
        page = urllib2.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        if page.getcode() != 200:
            raise ValueError('captha')

    else:
        page = requests.get(url, headers=headers, timeout=5)
        if page.status_code != 200:
            raise ValueError('captha')
    while True:
        sleep(3)
        try:
            if url.find('amazon.es') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//h1[@id="title"]//text()'
                XPATH_SALE_PRICE = '// *[ @ id = "price_inside_buybox"]/text()'
                XPATH_ORIGINAL_PRICE = '// *[ @ id = "priceblock_ourprice"]/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else "0"
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else "0"

                if SALE_PRICE == "0":
                    XPATH_SALE_PRICE = '//*[@id="buyNewSection"]/div/div/span/span/text()'
                    RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                    SALE_PRICE = ''.join(RAW_SALE_PRICE).strip()
                if ORIGINAL_PRICE == "0":
                    XPATH_ORIGINAL_PRICE = '// *[ @ id = "olp-sl-new"] / span / span/text()'
                    RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
                    ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip()
            if url.find('pccomponentes') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//h1[@itemprop="name"]//text()'
                XPATH_SALE_PRICE = '//*[@id="precio-main"]/span[1]/text()'
                XPATH_ORIGINAL_PRICE = '//*[@id="precio-main"]/span[2]/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                EU = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else "0"

                CENT = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else "0"
                ORIGINAL_PRICE=SALE_PRICE = EU + CENT



            """if url.find('gearbest') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//*[@id="goodsDetail"]/div[2]/div[2]/div[1]/h1/text()'
                XPATH_SALE_PRICE = '//*[@id="js-panelIntroPromoPrice"]/div[1]/span[1]/text()'
                XPATH_ORIGINAL_PRICE = '//*[@id="js-panelIntroNormalPrice"]/span/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
"""

            if url.find('banggood') != -1:

                NAME = soup.find('strong', attrs={'class': 'title_strong'})
                SALE_PRICE = soup.find('span', attrs={'class': 'price_num'})
                ORIGINAL_PRICE = soup.find('div', attrs={'class': 'item_now_price'})

                SALE_PRICE = ' '.join(''.join(SALE_PRICE.text).split()) if SALE_PRICE else "0"
                ORIGINAL_PRICE = ' '.join(''.join(ORIGINAL_PRICE.text).split()) if ORIGINAL_PRICE else "0"
                NAME = ' '.join(''.join(NAME).split()) if NAME else None
                if NAME == None:
                    NAME = soup.find('div', attrs={'class': 'title_hd'})
                    NAME = ' '.join(''.join(NAME).split()) if NAME else None

            if url.find('mediamarkt') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//*[@id="product-details"]/div[1]/h1/text()'
                XPATH_SALE_PRICE = '//*[@id="product-details"]/div[2]/div[1]/div[2]/text()'
                XPATH_ORIGINAL_PRICE = '//*[@id="product-details"]/div[2]/div[1]/div[2]/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None




            PRICE="0"
            if "0" != ORIGINAL_PRICE:
                PRICE = ORIGINAL_PRICE
            elif "0" != SALE_PRICE:
                PRICE = SALE_PRICE
            PRICE=normalizarPrecio(PRICE)
            data = {
                'NOMBRE': NAME,
                'PRECIO': PRICE,
                'URL': url,
            }
            print data
            return data
        except Exception as e:
            print e

def SondeoScrap(url, mensaje):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    if url.find('banggood') != -1:
        req = urllib2.Request(url, headers=headers)
        page = urllib2.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        if page.getcode() != 200:
            raise ValueError('captha')

    else:
        page = requests.get(url, headers=headers, timeout=5)
        if page.status_code != 200:
            raise ValueError('captha')
    while True:
        sleep(3)
        try:
            if url.find('amazon.es') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//h1[@id="title"]//text()'
                XPATH_SALE_PRICE = '// *[ @ id = "price_inside_buybox"]/text()'
                XPATH_ORIGINAL_PRICE = '// *[ @ id = "priceblock_ourprice"]/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else "0"
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else "0"

                if SALE_PRICE == "0":
                    XPATH_SALE_PRICE = '//*[@id="priceblock_dealprice"]/text()'
                    RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                    SALE_PRICE = ''.join(RAW_SALE_PRICE).strip()
                if ORIGINAL_PRICE == "0":
                    XPATH_ORIGINAL_PRICE = '// *[ @ id = "olp-sl-new"] / span / span/text()'
                    RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
                    ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip()

            if url.find('pccomponentes') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//h1[@itemprop="name"]//text()'
                XPATH_SALE_PRICE = '//*[@id="precio-main"]/span[1]/text()'
                XPATH_ORIGINAL_PRICE = '//*[@id="precio-main"]/span[2]/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                EU = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else "0"

                CENT = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else "0"
                ORIGINAL_PRICE=SALE_PRICE = EU + CENT

            if url.find('banggood') != -1:

                NAME = soup.find('strong', attrs={'class': 'title_strong'})
                SALE_PRICE = soup.find('span', attrs={'class': 'price_num'})
                ORIGINAL_PRICE = soup.find('div', attrs={'class': 'item_now_price'})

                SALE_PRICE = ' '.join(''.join(SALE_PRICE.text).split()) if SALE_PRICE else "0"
                ORIGINAL_PRICE = ' '.join(''.join(ORIGINAL_PRICE.text).split()) if ORIGINAL_PRICE else "0"
                NAME = ' '.join(''.join(NAME).split()) if NAME else None
                if NAME == None:
                    NAME = soup.find('div', attrs={'class': 'title_hd'})
                    NAME = ' '.join(''.join(NAME).split()) if NAME else None

            if url.find('mediamarkt') != -1:
                doc = html.fromstring(page.content)
                XPATH_NAME = '//*[@id="product-details"]/div[1]/h1/text()'
                XPATH_SALE_PRICE = '//*[@id="product-details"]/div[2]/div[1]/div[2]/text()'
                XPATH_ORIGINAL_PRICE = '//*[@id="product-details"]/div[2]/div[1]/div[2]/text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)

                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None

            PRICE = "0"
            if "0" != ORIGINAL_PRICE:
                PRICE = ORIGINAL_PRICE
            elif "0" != SALE_PRICE:
                PRICE = SALE_PRICE
            PRICE = normalizarPrecio(PRICE)
            # recorro la lista para buscar el precio mas bajo
            print ' entro scrap'
            for producto in usuario.getInitialList():
                if NAME == producto['NOMBRE']:
                    if float(PRICE) < float(producto['PRECIO']):
                        bot.send_message(mensaje.chat.id, "Producto: " + NAME)
                        bot.send_message(mensaje.chat.id,
                                         "Precio Antiguo: " + producto['PRECIO'] + " precio Nuevo: " + PRICE)
                        bot.send_message(mensaje.chat.id, "Enlace: " + url)
                    print "Precio Inicial: " + producto['PRECIO'] + "\nPrecio Actual: " + PRICE + "\n"
            sleep(2)
            return 1
        except Exception as e:
            print e


def normalizarPrecio(precio):
    precio=precio.upper()
    val = re.sub('[A-Z]', '', precio)
    val = re.sub('\$', '', val)
    val = val.replace(",", '.')
    val = val.replace(".-", '')

    return val


def Readlist(mensaje):
    chat_id = mensaje.chat.id
    if len(usuario.getInitialList()) != 0:  # Si la lista ya ha sido inicializada a los valores iniciales entro
        bot.send_message(chat_id, 'Sondeando...')
        while True:
            ReadSondeo(mensaje)
            sleep(720)
        bot.send_message(chat_id, 'El sondeo ha finalizado')
    else:
        bot.send_message(chat_id, 'Primero has de ejecutar /getprecios')

def ReadSondeo(mensaje):
    chat_id = mensaje.chat.id
    value = 0
    for i in usuario.getInitialList():
        lista = i  # Pasamos las urls de la Lista
        print "Procesando: " + lista['URL']
        # Lista_return obtendra la lista creada en la funcion scraping
        value = SondeoScrap(lista['URL'], mensaje)
        sleep(5)

def borrarLista(mensaje):
    print "Borrando lista..."
    usuario.borrarInicialList()
   # os.remove(current_path + str(mensaje.chat.id) + ".json")
    bot.send_message(mensaje.chat.id, 'Lista borrada con exito')





def leerFichero(msg):

    leer = json.loads(open(current_path+ str(msg)+".json").read())
    for i in range(0, len(leer)):
        usuario.setInitialList(leer[i])
    print "Archivo de datos cargado a memoria. "+str(len(usuario.getInitialList()))
    bot.send_message(msg, "Archivo de datos cargado a memoria.")

def exportar(chat_id):

    # Abre archivo en modo escritura
    extracted_data = []
    if len(usuario.getInitialList()) == 0:
        bot.send_message(chat_id, "No hay nada que exportar.")
    else:
        for i in usuario.getInitialList():
            extracted_data.append(i)
            sleep(5)
        f = open(current_path + str(chat_id) + ".json", 'w')
        json.dump(extracted_data, f, indent=4)
        print "Exportado el archivo.\n"
        bot.send_message(chat_id, "Operación realizada con éxito.")


