import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash 
import data_model

DBFILENAME = 'univ.sqlite'

def db_run(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()

def load(db_name=DBFILENAME):
  # possible improvement: do whole thing as a single transaction
  db_run('DROP TABLE IF EXISTS etablissement')
  db_run('DROP TABLE IF EXISTS password')
  db_run('DROP TABLE IF EXISTS user')
  db_run('DROP TABLE IF EXISTS objet')
  db_run('DROP TABLE IF EXISTS admis')

  db_run('CREATE TABLE etablissement(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,adress TEXT)')
  db_run('CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL,image TEXT,etid INTEGER,FOREIGN KEY (etid) REFERENCES etablissement(id))')
  db_run('CREATE TABLE password(id INTEGER PRIMARY KEY AUTOINCREMENT , userid INTEGER , password TEXT,FOREIGN KEY (userid) REFERENCES user(id) )' )
  db_run('CREATE TABLE objet (id INTEGER PRIMARY KEY AUTOINCREMENT,image TEXT,etid INTEGER,post TEXT,FOREIGN KEY (etid) REFERENCES etablissement(id))')
  db_run('CREATE TABLE admis(id INTEGER PRIMARY KEY AUTOINCREMENT,userid,password TEXT,FOREIGN KEY (userid) REFERENCES user(id))')
  


def main():

  load()

if __name__ == "__main__":
  main()




# load univ data