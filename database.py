import MySQLdb
import sys
try:
    firstarg = sys.argv[1]
except:
    firstarg = "SELECT * from usuarios"

connection = MySQLdb.connect (host = "localhost",
                              user = "root",
                              passwd = "root",
                              db = "findpricesbot")

cursor = connection.cursor()
cursor.execute ("SELECT * from usuarios")
row = cursor.fetchone()
for rows in row:
    print(rows)
cursor.close()
connection.close()