#EM PAIN

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


day_ref_time_ref = []
start = 0


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
  init_db()
  print('databse ready to go')
    
#ROUTE DEFINITIONS:    
@app.route('/', methods=['GET','POST'])
def landing():
  error = None
  mat_list = get_mat_list()
  date_du_jour = get_date()
  if request.method == 'POST':
    if request.form['matricule'] not in mat_list:
      error = "Invalid employee number (Ensure format follows XXX-99)"
    else:
      flash('Bonday_ref %s' %request.form['matricule'])
      x = request.form['matricule']
      return redirect(url_for('day', matricule=request.form['matricule'], date_du_jour=date_du_jour, error=error))
  return render_template('landing.html', error=error)


@app.route('/<matricule>/<date_du_jour>/', methods=['GET', 'POST'])
def day(matricule, date_du_jour):
  a = get_worked_hours(matricule, date_du_jour)
  return render_template('day.html', matricule=matricule, date_du_jour=date_du_jour, entries=a, prev=get_prev(date_du_jour), next=get_next(date_du_jour))


@app.route('/<matricule>/delete/<id_>/', methods=['POST'])
def delete(matricule, id_):
  db = get_db()
  db.execute('delete from heures where id = ?', (id_, ))
  db.commit()
  date_du_jour = get_date()
  return redirect(url_for('day', matricule=matricule, date_du_jour=date_du_jour))


@app.route('/<matricule>/update/<date_du_jour>/<id_>', methods=['GET', 'POST'])
def update(matricule, date_du_jour, id_):
  error = None
  if request.method == 'POST':
    time_ref = request.form['nombreMinutes']
    if int(time_ref) > 1440 or int(time_ref) < 1:
       error = "Enter a valid time (must be between 1 and 1440 minutes)"
    else:
      db = get_db()   
      db. execute('update heures set duree = ? where id = ?', (time_ref, id_, ))
      db.commit()
      return redirect(url_for('day', matricule=matricule, date_du_jour=date_du_jour))
  return render_template('update.html', matricule=matricule, date_du_jour=date_du_jour, id_=id_, error=error)


@app.route('/<matricule>/<date>/add/', methods=['GET','POST'])
def add(matricule, date):
  error=None
  if request.method == 'POST':
    error = None
    mat = matricule
    date = date
    project = request.form['numeroproject']
    time_ref = request.form['nombreMinutes']
    if int(time_ref) > 1440 or int(time_ref) < 1:
       error = "Enter a valid time (must be between 1 and 1440 minutes)"
    else:
      db = get_db()
      db.execute('insert into heures (matricule, code_de_projet, date_publication, duree) values(?, ?, ?, ?)', (mat, project, date, time_ref, ))
      db.commit()
      return redirect(url_for('day', matricule=matricule, date_du_jour=date))
  return render_template('add.html', matricule=matricule, date=date, error=error)


@app.route('/<matricule>/', methods=['GET', 'POST'])
def list2(matricule):
  entry_ref = get_months(matricule)
  l = get_single_list(entry_ref)
  if request.method == 'POST':
    month_ref = request.form['month_ref_number']
    year_ref = request.form['year_ref']
    month_ref_url = str(year_ref)+"-"+str(month_ref)
    return redirect(url_for('month2', matricule=matricule, month_ref=month_ref_url))
  return render_template('list2.html', matricule=matricule, entry_ref=l)


@app.route('/<matricule>/overview/<month_ref>/', methods=['GET', 'POST'])
def month2(matricule, month_ref):
  list_ref = get_data(matricule, month_ref)  
  unique_days_list = get_dict_month(list_ref)
  date = month_ref.split("-")
  short_list = combine_hours(list_ref)
  entries_ref = long_list(short_list, unique_days_list)
  return render_template('month2.html', matricule=matricule, month_ref=month_ref, start=list_ref[0], entries_ref=entries_ref, year_ref=date[0], month_ref_lettre=get_single_month(date[1]), month_ref_prev=get_mo_prev(month_ref), month_ref_next=get_mo_next(month_ref))

 
#METHODS TO DEFINE ROUTES' VARIABLES
 

#returns a list of matricules
def get_mat_list():
  l = []
  db = get_db()
  entries_ref = db.execute('select matricule from heures')
  for elem in entries_ref:
    l.append(elem[0])
  return l


#returns today's date
def get_date():
  now = datetime.datetime.now()
  year = now.year
  month = now.month 
  day = now.day 
  l = [str(year), str(month), str(day)]
  return "-".join((l))


#returns hours worked for a given date  
def get_worked_hours(mat, day_ref):
  l = []
  db = get_db()
  entries_ref = db.execute('select id,code_de_projet,duree,matricule,date_publication from heures')
  for elem in entries_ref:
    if elem[3] == mat and elem[4] == day_ref:
      l.append((elem[1],elem[2],elem[0]))
  return l


#returns a list containing the month in alpha, the year, the month in digit and the id
def get_months(mat):
  l = []
  month_ref = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
  db = get_db()
  entries_ref = db.execute('select id,date_publication,matricule from heures')
  for elem in entries_ref:
    if elem[2] == mat:
      s = elem[1].split("-")
      l.append((month_ref[int(s[1])-1], elem[0], s[0], s[1]))
  return l


#returns previous day
def get_prev(date):
  ddj = date.split("-");
  year_ref = int(ddj[0])
  month_ref = int(ddj[1])
  day_ref = int(ddj[2])
  if(day_ref > 1):
    day_ref -= 1
  elif(day_ref == 1 and month_ref in [4, 6, 9, 11]):
    month_ref = month_ref-1
    day_ref = 31
  elif (day_ref == 1 and month_ref == 3):
    if is_leap(year_ref):
      month_ref = 2
      day_ref = 29
    else:
      month_ref = 2
      day_ref = 28
  elif (day_ref == 1 and month_ref == 1):
    year_ref -= 1
    month_ref = 12
    day_ref = 31
  else:
    month_ref -= 1
    day_ref = 30

  return str(year_ref)+"-"+str(month_ref)+"-"+str(day_ref)                                                                     


#returns next day
def get_next(date):
  ddj = date.split("-");
  year_ref = int(ddj[0])
  month_ref = int(ddj[1])
  day_ref = int(ddj[2])
  if(month_ref == 2):
    if(is_leap(year_ref) and day_ref == 28):
      month_ref = 2
      day_ref = 29
    elif((not(is_leap(year_ref)) and day_ref == 28) or day_ref == 29):
      day_ref = 1
      month_ref = 3
    else:
      day_ref += 1
  elif(day_ref == 30 and month_ref in [4, 6, 9, 11]):
    month_ref +=1
    day_ref = 1
  elif (day_ref == 31 and month_ref in [1, 3, 5, 7, 8, 10]):
    day_ref = 1
    month_ref += 1
  elif (day_ref == 31 and month_ref == 12):
    year_ref += 1
    month_ref = 1
    day_ref = 1
  else:
    day_ref += 1

  return str(year_ref)+"-"+str(month_ref)+"-"+str(day_ref)         


#validates if leap year or not
def is_leap(year_ref):
  leap = False
  if year_ref % 400 == 0:
    leap = True
  elif year_ref % 100 == 0:
    leap = False
  elif year_ref % 4 == 0:
    leap = True

  return leap


#returns an int [0-6] to represent on which day a given month starts
def get_start_day(year_ref, month_ref):
  a = int(year_ref)
  m = int(month_ref)
  j = 1
  if m >= 3:
    day = (((23*m)/9) + j + 4 + a + (a/4) - (a/100) + (a/400) - 2 )%7
  else:
    day = (((23*m)/9) + j + 4 + a + ((a-1)/4) - ((a-1)/100) + ((a-1)/400)) % 7
  return int(day)


#returns a list with the starting day, and tuples for day,hours worked
def get_data(matricule, month_ref):
  date = month_ref.split("-")
  start = get_start_day(date[0], date[1]) 
  days = get_days(month_ref) 
  hours = get_hours_per_day(matricule, month_ref) 
  return get_month_display(start, days, hours)


#retrieves and sends the tuples of day,hours to get_data. Sorts the list.
def get_month_display(start, days, hours):
  l = []
  l.append(start)
  for elem in hours:    
    i = 1
    for i in range(days+1):
      if int(elem[0]) == i:
        #if there are hours, return the number of hours for that day
        l.append((i,elem[1])) 
      else:
        #if there arent any hours, add 'no data'
        l.append((i,'no data')) 
  return l


#returns hours per day
def get_hours_per_day(mat, month_ref):
  date = month_ref.split("-")
  l = []
  db = get_db()
  data = db.execute('select matricule,date_publication,duree from heures')
  for elem in data:
    if elem[0] == mat:
      d = elem[1].split("-")
      if (d[0]==date[0] and d[1]==date[1]):
        l.append((d[2], elem[2]))
  return l
    

#returns how many days there are in a month    
def get_days(month_ref):
  days = 999
  date = month_ref.split("-")
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

  
#adds hours if more than 1 entry per day
def combine_hours(list_ref):
  l = get_solos(list_ref)
  d = {}
  for elem in l:
    if str(elem[0]) in d.keys():
      d[elem[0]] = (d[elem[0]] + elem[1])
    else:
      d[elem[0]] = elem[1]
  return calculate_hours(list(d.items()))


#returns a dictionary of unique data found
def get_dict_month(l):
  d = {}
  for elem in l[2:]:
    if str(elem[0]) not in d.keys():
      d[elem[0]] = elem[1]
  return list(d.items())


#returns a list with only days that have hours saved
def get_solos(l):
  sl = []
  for elem in l[2:]:
    if elem[1] != 'no data':
      sl.append((str(elem[0]), elem[1]))
  return sl 


#transforms minutes to hours to display in calendar
def calculate_hours(l):
  fl = []
  for item in l:
    if item[1] != 'no data':
      hour = int(item[1]) / 60
      fl.append((item[0], hour))
    else:
      fl.append((item[0], item[1]))
  return fl


#Takes a list of all possible days and affixes correct data for days worked
def long_list(short, long):
  d = dict(long)
  for elem in short:
    d[int(elem[0])] = elem[1]
  if 0 in d.keys():
    del d[0]
  return list(d.items())


#returns a list of unique months  
def get_single_list(l):
  d = {}
  sl = []
  for elem in l:
    if elem[0] in d.keys():
      pass
    else:
      d[elem[0]] = elem[1]
      sl.append(elem)
  return sl


#returns a month in alpha to be displayed
def get_single_month(month):
  month_ref = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
  a = int(month)-1
  return month_ref[a]
    

#returns the previous month    
def get_mo_prev(month_ref):
  date = month_ref.split("-")
  mm = date[1]
  aa = date[0]
  if int(mm) == 1:
    year_ref = int(aa)-1
    ret = str(year_ref)+"-12"
  else:  
    mo = int(mm)-1
    ret = date[0]+"-"+str(mo)
  return ret
        

#returns the following month    
def get_mo_next(month_ref):
  date = month_ref.split("-")
  mm = date[1]
  aa = date[0]
  if int(mm) == 12:
    year_ref = int(aa)+1
    ret = str(year_ref)+"-1"
  else:
    mo = int(mm)+1
    ret = date[0]+"-"+str(mo)
  return ret
