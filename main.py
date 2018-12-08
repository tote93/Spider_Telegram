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
import FuncAuxiliares

global array

array = ["/sondear", "/lectura", "/exportar", "/getprecios", "/reiniciar" , "/estado"]
TOKEN = '407510413:AAFIYZBxBF1mAUK1w0qPnBGU-rts5dJ-II8'
bot = telebot.TeleBot(TOKEN)

def listener(mensaje):
    try:
        for m in mensaje:
            url_producto = m.text
            chat_id = m.chat.id
            name = m.from_user.first_name
        if url_producto in array:
            return 0
        elif url_producto.find('pccomponentes') != -1 or url_producto.find('amazon') != -1 or url_producto.find('banggood') != -1 or url_producto.find('mediamarkt') != -1:
             FuncAuxiliares.checkFile(chat_id,name)
             FuncAuxiliares.insertar(url_producto, chat_id, mensaje)
    except Exception as e:
        print e
@bot.message_handler(commands=['start'])
def inicio(mensaje):
    try:
        chat_id = mensaje.chat.id
        name =  mensaje.from_user.first_name
        FuncAuxiliares.checkFile(chat_id, name)
    except Exception as e:
        print "Error -> " +str(e)
@bot.message_handler(commands=['exportar'])
def exportar(mensaje):
    FuncAuxiliares.exportar(mensaje.chat.id)

@bot.message_handler(commands=['sondear'])
def sondear(mensaje):
    FuncAuxiliares.Readlist(mensaje)

#espera a recibir un /getprecios y manda a leer la lista
@bot.message_handler(commands=['getprecios'])
def get_precios(mensaje):
    FuncAuxiliares.obtenerPrecios(mensaje)

@bot.message_handler(commands=['reiniciar'])
def reiniciar(mensaje):
    FuncAuxiliares.borrarLista(mensaje)

@bot.message_handler(commands=['lectura'])
def lectura(mensaje):
    FuncAuxiliares.leerFichero(mensaje.chat.id)

@bot.message_handler(commands=['estado'])
def Estado(mensaje):
    bot.send_message(mensaje.chat.id,"Running.\n")

if __name__ == '__main__':
    try:
        bot.set_update_listener(listener)
    except Exception as e:
        print e
    bot.polling(none_stop=True)

