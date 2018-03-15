import os
import sqlite3
import datetime
from flask import Flask
from flask import request
from flask import g
from flask import redirect
from flask import url_for
from flask import flash
from flask import render_template


jour_temps = []
debut = 0


app = Flask(__name__)
app.secret_key = "Chinpokomon"

DATABASE = os.path.join(app.root_path, 'db.db')


def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db


@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_databases', None)
  if db is not None:
    db.close()
		
		
def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('db.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

		
@app.cli.command('initdb')
def initdb_command():
  #if the file existance is not none
  init_db()
  print('databse ready to go')
	
	
@app.route('/', methods=['GET','POST'])
def landing():
  erreur = None
  mat_list = get_mat_list()
  date_du_jour = get_date()
  if request.method == 'POST':
    if request.form['matricule'] not in mat_list:
      erreur = "Invalid employee number"
    elif not check_format(request.form['matricule']):
      erreur = "Invalid employee number (Ensure format follows XXX-99)"
    else:
      flash('Bonjour %s' %request.form['matricule'])
      return redirect(url_for('day', matricule=request.form['matricule'], date_du_jour=date_du_jour, erreur=erreur))
  return render_template('landing.html', erreur=erreur)


@app.route('/<matricule>/<date_du_jour>/', methods=['GET', 'POST'])
def day(matricule, date_du_jour):
  erreur = None
  a = get_worked_hours(matricule, date_du_jour)
#  if request.method == 'GET':
#    print(matricule)
#    if check_format(matricule) == False:
#      erreur = "Invalid employee number"
#      redirect(url_for('landing', erreur=erreur))
  return render_template('day.html', matricule=matricule, date_du_jour=date_du_jour, entries=a, prev=get_prev(date_du_jour), next=get_next(date_du_jour), erreur=erreur)


@app.route('/<matricule>/delete/<id_>/', methods=['POST'])
def delete(matricule, id_):
  db = get_db()
  db.execute('delete from heures where id = ?', (id_, ))
  db.commit()
  flash('Entree supprimee')
  date_du_jour = get_date()
  return redirect(url_for('day', matricule=matricule, date_du_jour=date_du_jour))


@app.route('/<matricule>/update/<date_du_jour>/<id_>', methods=['GET', 'POST'])
def update(matricule, date_du_jour, id_):
  erreur = None
  if request.method == 'POST':
    temps = request.form['nombreMinutes']
    print(type(temps))
    if int(temps) > 1440 or int(temps) < 1:
       erreur = "Enter a valid time (must be between 1 and 1440 minutes)"
    else:
      db = get_db()   
      db. execute('update heures set duree = ? where id = ?', (temps, id_, ))
      db.commit()
      flash('Entree mise a jour')
      return redirect(url_for('day', matricule=matricule, date_du_jour=date_du_jour))
  return render_template('update.html', matricule=matricule, date_du_jour=date_du_jour, id_=id_, erreur=erreur)


@app.route('/<matricule>/<date>/add/', methods=['GET','POST'])
def add(matricule, date):
  erreur=None #Add empty box valiation?
  if request.method == 'POST':
    erreur = None
    mat = matricule
    date = date
    projet = request.form['numeroProjet']
    temps = request.form['nombreMinutes']
    if int(temps) > 1440 or int(temps) < 1:
       erreur = "Enter a valid time (must be between 1 and 1440 minutes)"
    else:
      db = get_db()
      db.execute('insert into heures (matricule, code_de_projet, date_publication, duree) values(?, ?, ?, ?)', (mat, projet, date, temps, ))
      db.commit()
      return redirect(url_for('day', matricule=matricule, date_du_jour=date))
  return render_template('add.html', matricule=matricule, date=date, erreur=erreur)


@app.route('/<matricule>/', methods=['GET', 'POST'])
def list2(matricule):
  entree = get_months(matricule)
  #if entree[0] is already there, dont show it.
  l = get_single_list(entree)
  if request.method == 'POST':
    mois = request.form['mois_chiffre']
    annee = request.form['annee']
    mois_url = str(annee)+"-"+str(mois)
    return redirect(url_for('month', matricule=matricule, mois=mois_url))
  return render_template('list2.html', matricule=matricule, entree=l)


@app.route('/<matricule>/overview/<mois>/', methods=['GET', 'POST'])
def month(matricule, mois):
  liste = get_data(matricule, mois)  #ADD NOT NONE ON ALL FORS !!!
  unique_days_list = get_dict_month(liste)
  date = mois.split("-")
  short_list = combine_hours(liste)
  entrees = long_list(short_list, unique_days_list)
  return render_template('month.html', matricule=matricule, mois=mois, debut=liste[0], entrees=entrees, annee=date[0], mois_lettre=get_single_month(date[1]), mois_prev=get_mo_prev(mois), mois_next=get_mo_next(mois))


def get_mat_list():
  l = []
  db = get_db()
  entrees = db.execute('select matricule from heures')
  for elem in entrees:
    l.append(elem[0])
  return l


def get_date():
  now = datetime.datetime.now()
  year = now.year
  month = now.month #add a zero
  day = now.day #add a zero
  l = [str(year), str(month), str(day)]
  return "-".join((l))


def get_worked_hours(mat, jour):
  l = []
  db = get_db()
  entrees = db.execute('select id,code_de_projet,duree,matricule,date_publication from heures')
  for elem in entrees:
    if elem[3] == mat and elem[4] == jour:
      l.append((elem[1],elem[2],elem[0]))
  return l


def get_months(mat):
  l = []
  mois = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']
  db = get_db()
  entrees = db.execute('select id,date_publication,matricule from heures')
  for elem in entrees:
    if elem[2] == mat:
      s = elem[1].split("-")
      l.append((mois[int(s[1])-1], elem[0], s[0], s[1]))
  return l


def get_prev(date):
  ddj = date.split("-");
  annee = int(ddj[0])
  mois = int(ddj[1])
  jour = int(ddj[2])
  if(jour > 1):
    jour -= 1
  elif(jour == 1 and mois in [4, 6, 9, 11]):
    mois = mois-1
    jour = 31
  elif (jour == 1 and mois == 3):
    if is_leap(annee):
      mois = 2
      jour = 29
    else:
      mois = 2
      jour = 28
  elif (jour == 1 and mois == 1):
    annee -= 1
    mois = 12
    jour = 31
  else:
    mois -= 1
    jour = 30

  return str(annee)+"-"+str(mois)+"-"+str(jour)																		


def get_next(date):
  ddj = date.split("-");
  annee = int(ddj[0])
  mois = int(ddj[1])
  jour = int(ddj[2])
  if(mois == 2):
    if(is_leap(annee) and jour == 28):
      mois = 2
      jour = 29
    elif((not(is_leap(annee)) and jour == 28) or jour == 29):
      jour = 1
      mois = 3
    else:
			jour += 1
  elif(jour == 30 and mois in [4, 6, 9, 11]):
    mois +=1
    jour = 1
  elif (jour == 31 and mois in [1, 3, 5, 7, 8, 10]):
    jour = 1
    mois += 1
  elif (jour == 31 and mois == 12):
    annee += 1
    mois = 1
    jour = 1
  else:
    jour += 1

  return str(annee)+"-"+str(mois)+"-"+str(jour)			


def is_leap(annee):
  leap = False
  if annee % 400 == 0:
    leap = True
  elif annee % 100 == 0:
    leap = False
  elif annee % 4 == 0:
    leap = True

  return leap


def get_start_day(annee, mois):
  a = int(annee)
  m = int(mois)
  j = 1
  if m >= 3:
    day = (((23*m)/9) + j + 4 + a + (a/4) - (a/100) + (a/400) - 2 )%7
  else:
    day = (((23*m)/9) + j + 4 + a + ((a-1)/4) - ((a-1)/100) + ((a-1)/400)) % 7
  return day


def day_time_list(matricule, annee, mois):
  l = []
  db = get_db()
  entrees = db.execute('select duree,matricule,date_publication from heures')
  jour = str(annee)+"-"+str(mois)
  taille = len(jour)
  for elem in entrees:
    if elem[1] == matricule and ((elem[2])[0:taille] == jour):
      l.append((elem[2][-2:],elem[0]))
  return l


def get_data(matricule, mois):
  date = mois.split("-")
  debut = get_start_day(date[0], date[1]) #0 if sunday, 6 is saturday
  days = get_days(mois)  #how many days there are in a month
  hours = get_hours_per_day(matricule, mois) #hours per day
  return get_month_display(debut, days, hours)


def get_month_display(debut, days, hours):
  l = []
  l.append(debut)
  for elem in hours:	
    i = 1
    for i in range(days+1):
      if int(elem[0]) == i:
        l.append((i,elem[1])) #if there are hours, return the number of hours for that day
      else:
        l.append((i,'no data')) #if there arent any hours, return 0
  return l


def get_hours_per_day(mat, mois):
  date = mois.split("-")
  l = []
  db = get_db()
  data = db.execute('select matricule,date_publication,duree from heures')
  for elem in data:
    if elem[0] == mat:
      d = elem[1].split("-")
      if (d[0]==date[0] and d[1]==date[1]):
        l.append((d[2], elem[2]))
  return l
	

def get_days(mois):
  days = 999
  date = mois.split("-")
  if date[1] in ['4', '6', '9', '11']:
    days = 30
  elif date[1] in ['1', '3', '5', '7', '8', '10']:
    days = 31
  else:
    if is_leap(int(date[0])):
      days = 29
    else: 
      days = 28
  return days


def combine_hours(liste):
  l = get_solos(liste)
  d = {}
  for elem in l:
    if str(elem[0]) in d.keys():
      d[elem[0]] = (d[elem[0]] + elem[1])
    else:
      d[elem[0]] = elem[1]
  return calculate_hours(list(d.items()))


def get_dict_month(l):
  d = {}
  for elem in l[2:]:
    if str(elem[0]) not in d.keys():
      d[elem[0]] = elem[1]
  return list(d.items())


def get_solos(l):
  sl = []
  for elem in l[2:]:
    if elem[1] != 'no data':
      sl.append((str(elem[0]), elem[1]))
  return sl #REMOVE k = 0??


def calculate_hours(l):
  fl = []
  for item in l:
    if item[1] != 'no data':
      hour = int(item[1]) / 60
      fl.append((item[0], hour))
    else:
      fl.append((item[0], item[1]))
  #print(fl)
  return fl


def long_list(short, long):
  d = dict(long)
  for elem in short:
    d[int(elem[0])] = elem[1]
  if 0 in d.keys():
    del d[0]
  return list(d.items())

	
def get_single_list(l):
  d = {}
  sl = []
  #print(l)
  for elem in l:
    if elem[0] in d.keys():
      pass
    else:
      d[elem[0]] = elem[1]
      sl.append(elem)
  return sl


def get_single_month(month):
  mois = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']
  a = int(month)-1
  return mois[a]
	

	
def get_mo_prev(mois):
  date = mois.split("-")
  mm = date[1]
  print(type(mm))
  aa = date[0]
  if int(mm) == 1:
    annee = int(aa)-1
    ret = str(annee)+"-12"
  else:  
    mo = int(mm)-1
    ret = date[0]+"-"+str(mo)
  print(ret)
  return ret
		

	
def get_mo_next(mois):
  date = mois.split("-")
  mm = date[1]
  aa = date[0]
  if int(mm) == 12:
    annee = int(aa)+1
    ret = str(annee)+"-1"
  else:
    mo = int(mm)+1
    ret = date[0]+"-"+str(mo)
  return ret


def check_format(entry):
  ret = True
  print(entry)
  print(len(entry))
  data = entry.split("-")
  if len(entry) != 6:
    print("I am false!")
    ret = False
  return ret
