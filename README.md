# Spider_Telegram
Araña para extracción de precios, desarrollada para utilización conjunta de bot en telegram.
Dispone de los siguientes comandos:

/exportar -> Exporta la lista obtenida en un fichero llamado productos.json


/lectura -> Lee el fichero json e importa a la lista los datos


/getprecios -> Lee de la lista AsyncList las urls y mete los datos en la inicial


/sondear -> sondea la lista inicial con los precios actuales, en caso de encontrar una bajada de precio en el producto avisa por mensaje en telegram.


/resetear -> Resetea la lista de precios.


#Como utilizar:
Si no tienes aun el fichero productos.json:
  1) Pon tu Token ID de telegram, e inicia el bot junto al bot.py
  2) Pega la url completa en el chat de telegram, (puedes pegar tantas urls como desees).
  3) Rellena la lista con el comando /getprecios
  4) Exporta el fichero para en un futuro no tener que realizar los pasos 2 y 3.
  5) Sondea en busca de precios.
	
	
Si ya tienes el fichero creado:
  1) Lee el fichero.
  2) Inicia el sondeo.
