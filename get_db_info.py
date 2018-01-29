import sqlite3
import time

connection = sqlite3.connect("musique.db")
cursor = connection.cursor()
cursor.execute("SELECT id,nom FROM artiste")
for row in cursor:
    print(row[0], row[1]) 

time.sleep(.300)
val = input("\nSelect the artist ID from which you'd like the discography: ")

cursor.execute("SELECT titre FROM album WHERE artiste_id=%s" % val)
for row in cursor:
    print(row[0])

connection.close()
