# Spider_Telegram
Spider for price extraction, developed for joint use of bot in telegram.
It has the following commands:

/exportar -> Export the list obtained in a file called products.json


/lectura -> Read the json file and import the data into the list


/getprecios -> Read the urls from the AsyncList list and enter the data in the initial


/sondear -> poll the initial list with the current prices, in case of finding a price drop in the product, notify by message on telegram.


/resetear -> Reset the price list.


#How to use:
If you don't have the products.json file yet:
  1) Put your telegram Token ID, and start the bot next to the bot.py
  2) Paste the complete url in the telegram chat, (you can paste as many urls as you want).
  3) Fill in the list with the command / get prices
  4) Export the file so that in the future you don't have to perform steps 2 and 3.
  5) Search for prices.


If you already have the file created:
  1) Read the file.
  2) Start polling.
