# -*- coding: utf-8 -*-
import telebot
from telebot import types
from lxml import html
import csv, os, json
import requests
from exceptions import ValueError
from time import sleep
import urllib2
from bs4 import BeautifulSoup
import io, json
global inicial
inicial = []
global AsinList
AsinList = []
#Insertar el token ID obtenido por el bot GodFather En TElegram
TOKEN = ''
bot = telebot.TeleBot(TOKEN)

#mete la url a la lista global
def Insertar(mensaje, texto):
    AsinList.append(texto)
   # print AsinList

#espera a recibir un /getprecios y manda a leer la lista
@bot.message_handler(commands=['getprecios'])
def get_precios(mensaje):
    if len(AsinList) == 0:
        print "error lista vacia"
        bot.send_message(mensaje.chat.id, 'La lista esta vacia, debe insertar productos previamente pasandome el enlace completo EJ: http//www.XXX.es a amazon/gearbest/pccomponentes')
    else:
        ReadAsin(mensaje)


def Scraping(url, mensaje):
    #headers de navegador para que nos permita ejecutar la url
    headers = {
       'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    #peticion a la url solicitada con la cabecera anterior
    req = urllib2.Request(url, headers=headers)
    page = urllib2.urlopen(req)
    if page.getcode() != 200:
        raise ValueError('captha')
    # Parsea el HTML usando el modulo beautiful soap y lo metemos en soup
    soup = BeautifulSoup(page, 'html.parser')

    while True:
        sleep(3)
        try:
                if url.find('pccomponentes') != -1:
                    precio_box = soup.find('span', attrs={'class': 'baseprice'})
                    nombre_box = soup.find('h1', attrs={'itemprop': 'name'})
                    nombre = nombre_box.text.replace("\n", '')
                    precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                    print "entro a pccompo\n"
                if url.find('amazon.es') != -1:
                    precio_box = soup.find('span', attrs={'id': 'priceblock_ourprice'})
                    nombre_box = soup.find('span', attrs={'id': 'productTitle'})
                    nombre = nombre_box.text.replace("\n", '')
                    if precio_box == None:
                        precio_box = soup.find('span', attrs={'id': 'priceblock_saleprice'})
                    precio=precio_box.text
                    nombre = nombre.replace("                                                                                                                                                        ","")

                    print "entro a amazon\n"
                if url.find('gearbest') != -1:
                    precio_box = soup.find('span', attrs={'class': 'my_shop_price new_shop_price ajax-price'})
                    nombre_box = soup.find('div', attrs={'class': 'goods-info-top'})
                    nombre = nombre_box.text.replace("\n", '')
                    precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                    if precio == 0:
                        precio_box = soup.find('b', attrs={'class': 'my_shop_price ajax-price'})
                        precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                    print "entro a gearbest\n"
                if url.find('banggood') != -1:
                    precio_box = soup.find('div', attrs={'class': 'now'})
                    nombre_box = soup.find('h1', attrs={'itemprop': 'name'})
                    nombre = nombre_box.text.replace("\n", '')
                    precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                    print "entro a banggood\n"
                # creo una lista que devuelvo e inserto en otra lista global
                data = {
                    'NOMBRE': nombre,
                    'PRECIO': precio,
                    'URL': url,
                }

                return data
        except Exception as e:
            print e


def ReadAsin(mensaje):
        print AsinList
        chat_id = mensaje.chat.id
        bot.send_message(chat_id, 'Espere mientras cargo los datos del producto solicitado...')
        for i in AsinList:
            url =  i #Pasamos las urls de la Lista
            #Lista_return obtendra la lista creada en la funcion scraping
            lista_return = Scraping(url, mensaje)
            #metemos cada lista en una lista global llamada inicial
            inicial.append(lista_return)
            sleep(5)
        bot.send_message(mensaje.chat.id, 'Finalizada la obtención inicial de precios')

@bot.message_handler(commands=['sondear'])
def Readlist(mensaje):
    chat_id = mensaje.chat.id
    if len(inicial) !=0: #Si la lista ya ha sido inicializada a los valores iniciales entro
        bot.send_message(chat_id, 'Sondeando...')
        while True:
            ReadSondeo(mensaje)
            sleep(20)
        bot.send_message(chat_id, 'El sondeo ha finalizado')
    else:
        bot.send_message(chat_id, 'Primero has de ejecutar /getprecios')

def ReadSondeo(mensaje):
        chat_id = mensaje.chat.id
        value=0
        for i in inicial:
            lista =  i #Pasamos las urls de la Lista
            print "Procesando: " + lista['URL']
            #Lista_return obtendra la lista creada en la funcion scraping
            value=SondeoScrap(lista['URL'], mensaje)
            sleep(5)



@bot.message_handler(commands=['reiniciar'])
def Borrar_Lista(mensaje):

    print "Borrando lista..."
    del inicial[:]
    bot.send_message(mensaje.chat.id, 'Lista borrada con exito')

def SondeoScrap(url, mensaje):
    #headers de navegador para que nos permita ejecutar la url
    headers = {
       'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    #peticion a la url solicitada con la cabecera anterior
    req = urllib2.Request(url, headers=headers)
    page = urllib2.urlopen(req)
    if page.getcode() != 200:
        raise ValueError('captha')
    # Parsea el HTML usando el modulo beautiful soap y lo metemos en soup
    soup = BeautifulSoup(page, 'html.parser')

    while True:
        sleep(3)
        try:
            if url.find('pccomponentes') != -1:
                precio_box = soup.find('span', attrs={'class': 'baseprice'})
                nombre_box = soup.find('h1', attrs={'itemprop': 'name'})
                nombre = nombre_box.text.replace("\n", '')
                precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                print "Sondeo a pccompo\n"
            if url.find('amazon.es') != -1:
                precio_box = soup.find('span', attrs={'id': 'priceblock_ourprice'})
                nombre_box = soup.find('span', attrs={'id': 'productTitle'})
                nombre = nombre_box.text.replace("\n", '')
                nombre= nombre.replace("                                                                                                                                                        ","")
                if precio_box == None:
                    precio_box = soup.find('span', attrs={'id': 'priceblock_saleprice'})
                precio = precio_box.text
                print "Sondeo a amazon\n"
            if url.find('gearbest') != -1:
                precio_box = soup.find('span', attrs={'class': 'my_shop_price new_shop_price ajax-price'})
                nombre_box = soup.find('div', attrs={'class': 'goods-info-top'})
                nombre = nombre_box.text.replace("\n", '')
                precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                if precio == 0:
                    precio_box = soup.find('b', attrs={'class': 'my_shop_price ajax-price'})
                    precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                print "Sondeo a gearbest\n"
            if url.find('banggood') != -1:
                precio_box = soup.find('div', attrs={'class': 'now'})
                nombre_box = soup.find('h1', attrs={'itemprop': 'name'})
                nombre = nombre_box.text.replace("\n", '')
                precio = ' '.join(''.join(precio_box.text).split()) if precio_box else 0
                print "Sondeo a BangGood\n"

            #recorro la lista para buscar el precio mas bajo
            for producto in inicial:
                    if nombre == producto['NOMBRE']:
                        if precio < producto['PRECIO']:
                            bot.send_message(mensaje.chat.id, "Producto: " + nombre)
                            bot.send_message(mensaje.chat.id, "Precio Antiguo: " + producto['PRECIO'] + " precio Nuevo: " + precio)
                            bot.send_message(mensaje.chat.id, "Enlace: " + url)
                        print "Precio Inicial: "+producto['PRECIO'] +"\nPrecio Actual: "+precio+"\n"
                        return 0
            return 1
        except Exception as e:
            print e


def listener(mensaje):
    try:
        for m in mensaje:
            texto = m.text
        if texto.find('pccomponentes') != -1 or texto.find('amazon') != -1 or texto.find('gearbest') != -1 or texto.find('banggood') != -1:
            print "insertado"
            Insertar(mensaje, texto)
        else:
            print "El texto no es un comando\n"
    except Exception as e:
        print e
@bot.message_handler(commands=['exportar'])
def exportar(mensaje):
    chat=mensaje.chat.id;
    # Abre archivo en modo escritura
    extracted_data = []
    for i in inicial:
        extracted_data.append(i)
        sleep(5)
    f = open('productos.json', 'w')
    json.dump(extracted_data, f, indent=4)
    print "Exportado el archivo.\n"
    bot.send_message(chat, "Archivo exportado con éxito.")

    # Cierra archivo

@bot.message_handler(commands=['lectura'])
def lectura(mensaje):
    chat=mensaje.chat.id;

    leer = json.loads(open('productos.json').read())

    for i in range(0, len(leer)):
        inicial.append(leer[i])
    print "Archivo de datos cargado a memoria \n"
    bot.send_message(chat, "Archivo de datos cargado a memoria.")



if __name__ == '__main__':
    try:
        bot.set_update_listener(listener)
    except Exception as e:
        print e
    bot.polling(none_stop=True)
