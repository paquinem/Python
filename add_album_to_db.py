import sqlite3


#separate the file into lines and treat data accordingly
def start():
    file = open('input.txt', "r")

    for line in file:
        art,alb,pub = line.split('|')
        artID = check_databse(art,alb,pub)
        add_album(artID,alb,pub)
        

#check if the artist exists or not. If not, create it. Return the artist's ID
def check_databse(art,alb,pub):
    connection = sqlite3.connect('musique.db')
    cursor = connection.cursor()
    
    #find out if the artist already exists, if not, add it
    cursor.execute("SELECT id FROM artiste WHERE nom= '%s'" % art)
    if cursor.fetchone() is None:
        print('artist does not exist')
        #create the artist
        connection.execute(("INSERT INTO artiste(nom, est_solo, nombre_individus)"
                            "values(?, ?, ?)"),(art, '1', '4'))
        cursor.execute("select last_insert_rowid()")
        return cursor.fetchone()[0]
        connection.commit()
    else:
        for item in cursor:
            return item[0]         
    connection.close() 
    
    
#add the album to the DB    
def add_album(artID,alb,pub):
    connection = sqlite3.connect('musique.db')
    cursor = connection.cursor()
    
    cursor.execute(("INSERT INTO album(titre, annee, artiste_id, maison_disque_id)"
                   "values(?, ?, ?, ?)"),(alb, pub, artID, '2'))
    connection.commit()   
    connection.close()    
    

def end():
    
    connection = sqlite3.connect('musique.db')
    cursor = connection.cursor()
    cursor.execute(("SELECT * FROM album"))
    for row in cursor:
        print(row[0], row[1])
    
    
start()
end()
