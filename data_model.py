import sqlite3
from flask import Flask, app, current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash 
import os
from werkzeug.utils import secure_filename


DBFILENAME = 'univ.sqlite'




                      ######################
                      #   BASE DE DONNEE   #
                      ######################
# Utility functions
def db_fetch(query, args=(), all=False, db_name=DBFILENAME):
    try:
        with sqlite3.connect(db_name) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(query, args)
            
            if all:
                rows = cur.fetchall()
                return [dict(row) for row in rows] if rows else []
            else:
                row = cur.fetchone()
                return dict(row) if row else None
                
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        return None if not all else []
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return None if not all else []

def db_insert(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return cur.lastrowid


def db_run(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()


def db_update(query, args=(), db_name=DBFILENAME):
  with sqlite3.connect(db_name) as conn:
    cur = conn.execute(query, args)
    conn.commit()
    return cur.rowcount
  

class db_web():
  def __init__(self):
    pass

                      #######################
                      #   Gestion d'objet   #
                      #######################



  def detail_objet(self,id):
    found=db_fetch('SELECT * FROM objet WHERE id=?',(id,))
    return found

  def list_objets(self,etid):
    res= db_fetch('SELECT * FROM objet WHERE etid=?',(etid,),all=True)
    return res
  
  def update_objet(self,image,etid,post,id):
    res =db_update('UPDATE objet SET image = ?, etid = ?, post =? WHERE id = ?',(image,etid,post,id))
    return res
  
  def delete_obj(self,id):
    db_run('DELETE FROM objet WHERE id = ?', (id,))


  def add_objet(self,image,etid,post ) :
    res=db_insert('INSERT INTO objet(image,etid,post) VALUES(?,?,?)',(image,etid,post))
    return res
  
  def list_objet(self):
    try:
        res = db_fetch('SELECT * FROM objet ORDER BY id', all=True)
        if res is None:  
            print("Aucun résultat ou erreur de requête")
            return []
        return res
    except Exception as e:
        print(f"Erreur dans list_objet: {e}")
        return []



                      ###################
                      #   Gestion User  # 
                      ###################        


  def user_read(self,id):
    found =db_fetch('SELECT * FROM user WHERE id = ?', (id,))
    return found['id']

  
  def delete_user(self,id):
    db_run('DELETE FROM user WHERE id = ?', (id,))


  def user_password(self,id,password):
      result = db_fetch('SELECT * FROM password WHERE userid=?', (id,))
      if(not(check_password_hash(result['password'], password))):
        return None
      else:
        return id 
      

  def login(self,username, password ):
    result = db_fetch('SELECT * FROM user WHERE username=?', (username,))
    if (result is None):
      return None
    else :
      connect= self.user_password(result['id'],password)
      if not connect:
        return None
      return result['id']
    
    
  def user_existe(self,username):
    found = db_fetch('SELECT * FROM user WHERE username=?',(username,))
    return found is not None

  def user_insert(self,name,password,image,idet):
    hash=generate_password_hash(password)
    res =db_insert('INSERT INTO user(username,image,etid) VALUES(?,?,?)',(name,image,idet))
    if res is None:
          raise Exception("Erreur lors de l'insertion de l'utilisateur dans la table user.")
    user_id=res
    passeword=db_insert('INSERT INTO password(userid,password)VALUES(?,?)',(res,hash))
    return(self.user_read(user_id))
  
  def found_user(self,username):
     res =db_fetch('SELECT * FROM user WHERE username = ?', (username,))
     return res
  
                        ######################
                        #   Gestion d'admis  #
                        ######################   

  def admi_exist(self, userid):
    res = db_fetch('SELECT * FROM admis WHERE userid = ?', (userid,))
    return res is not None  

  def add_admi(self, username, password): 
    """Ajoute un administrateur"""
    admpass = "viny"  
  
    user = db_fetch('SELECT id FROM user WHERE username = ?', (username,))
  
    if self.admi_exist(user['id']):
        return -1  
    
    
    if password != admpass:  
        return -2  
    
    
    hash_pw = generate_password_hash(admpass) 
    res = db_insert('INSERT INTO admis(userid, password) VALUES(?,?)', 
                   (user['id'], hash_pw))
    return res  
      
  
  
                      ################################
                      #   Gestion d'etaablissement   #
                      ################################        
  def found_etablisement(self,name):
    res = db_fetch('SELECT * FROM etablissement WHERE name = ?', (name,))
    return res
  
  
  def liste_etablissement(self):
    res= db_fetch('SELECT * FROM etablissement order by id', all= True) 
    return res
  

  def get_etablissement_name(self, etid):
    """Récupère le nom complet de l'établissement"""
    etab = db_fetch("SELECT name FROM etablissement WHERE id = ?", (etid,))
    return etab['name'] if etab else "Inconnu"