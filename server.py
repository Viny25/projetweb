from functools import wraps
from werkzeug.utils import secure_filename
import os
import uuid
from flask import Flask, current_app, flash, session, Response, request, redirect, url_for, render_template
import data_model as data_model
import itertools

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file( file):
    """Sauvegarde un fichier uploadé et retourne uniquement le nom du fichier"""
    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        return None

    try:
      
        filename = secure_filename(file.filename)
        if not filename:
            return None

       
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)

        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(upload_path, filename)
            counter += 1

       
        file.save(file_path)
       
        return filename

    except Exception as e:
        app.logger.error(f"Erreur sauvegarde fichier: {str(e)}")
        return None



model=data_model.db_web()
app.secret_key = b'0a1078efe8aacfd516ee04234c087d78059c77e463b88b9c5ead55c05f2fa06b'


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)

@app.get('/')
def page_accueille():
    session.clear()
    return render_template('accueille.html',session = session)

                                ######################
                                #   USER and LOGIN   #
                                ######################

@app.post('/login')
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    error = None
    
    
    if not username or not password:
        error = "Username et password requis"
        return render_template('login.html', error=error)
    
    
    res = model.login(username, password)
    
    if res is None:
        error = "Username ou password incorrect"
        return render_template('login.html', error=error)
    else:
        session.clear()  
        session['username'] = username
        return redirect(url_for('index')) 
                                 
@app.get('/newuser')
def newuserf():
    liste = model.liste_etablissement()
    error = None
    return(render_template('newuser.html', session=session, liste = liste,error = error ))


@app.post('/newuser')
def newuser():
    etablissements = model.liste_etablissement()
    error= None
    if not all([request.files['image'],request.form['username'],request.form['password'],request.form['etablissement']]):
        error=('Tous les champs sont obligatoires', 'error')
        return render_template('newuser.html',session=session,etablissements=etablissements,error=error)
    image_file = request.files['image']
    etablissement_name = request.form['etablissement']
    password=request.form['password']
    username= request.form['username']

    if model.user_existe(username):
        error=("ce nom d'itilisateur existe déjà")
        return render_template('newuser.html',session=session,etablissements=etablissements,error=error)
    etablissement= model.found_etablisement(etablissement_name)
    if etablissement is None:
        error =('Établissement invalide', 'error')
        return render_template('newuser.html',session=session,etablissements=etablissements,error=error)
    image_filename=save_uploaded_file(image_file)
    res=model.user_insert(username,password,image_filename,etablissement['id'])
    if res:
        error ="compte creer connectez-vous"
        return render_template('login.html',session=session,error = error)
    
    
@app.get('/profil')
def profil():
    username=session['username']
    profil = model.found_user(username)
    etablissement = model.get_etablissement_name(profil['etid'])
    return render_template('profil.html', session=session,profil=profil, etablissement=etablissement)
    
    


@app.get('/login')
def page_login():
    return render_template('login.html',session=session,error = None)



    
@app.get('/logout')
def log_out(): #Rammene à la page d'acceil en suppriment la session 
   session.clear()
   return redirect(url_for('page_accueille'))



                            ###################
                            # Gestion  OBJECT #
                            ###################
       
@app.get('/index')
def index():
    res = model.list_objet()
    etablissements = model.liste_etablissement() or []  # Toujours défini
    error = None
    liste = None

    if not res:  
        error = "Soyez la première personne..."
        return render_template('index.html', 
            session=session, 
            liste=liste,  # Utilise `liste` si défini, sinon `res`
            error=error, 
            etablissements=etablissements
            )
    if (error is None):
        #dico_res = dict(list(res.items())[:10]) if len(res) > 10 else res.copy()

        return render_template('index.html', 
            session=session, 
            liste=res,  # Utilise liste si défini, sinon res
            error=error, 
            etablissements=etablissements
            )

@app.get('/list')
def list_objet():
    try:
        res = model.list_objet()
        etablissement_name = request.args.get('etablissement', '').strip()
        
        if not etablissement_name:
            error=("Veuillez sélectionner un établissement", "warning")
            return redirect(url_for('index', error = error))

        etablissement = model.found_etablisement(etablissement_name)
        if not etablissement:
            error=("Établissement non trouvé", "error")
            return  redirect(url_for('index', error = error))


        objets = model.list_objets(etablissement['id'])
        etablissements = model.liste_etablissement()

        return render_template(
            'liste.html',
            session=session,
            liste=objets,
            etablissements=etablissements,
            current_etablissement=etablissement_name,
            etablissement_id=etablissement['id']  # passe l'ID au template
        )

    except Exception as e:
        current_app.logger.error(f"Erreur dans list_objet: {str(e)}", exc_info=True)
        flash("Une erreur est survenue lors de la récupération des données", "error")
        return redirect(url_for('index'))

@app.get('/newobjet')
def newobjet():
    etablissement = model.liste_etablissement() or []

    return render_template('creatobjet.html',session=session,etablissements=etablissement)

@app.get('/Detail/<id>')
def detail(id): #donne les detaille d'un objet
   res=model.detail_objet(int(id))
   name = session['username']
   current_et=model.get_etablissement_name(res['etid'])
   user =model.found_user(name)
   if not(model.admi_exist(user['id'])):
      return render_template('detail.html',session=session,courant=current_et, objet=res, admi=False)
   else:
      return render_template('detail.html',session=session,courant=current_et, objet=res, admi=True)

@app.get('/remove_obj/<id>')  
def remove_obj(id): #permet de supprimeer un objet de la  liste 
   model.delete_obj(id)
   return(redirect(url_for('list_objet')))


@app.post('/newobjet')
def add_objet():
    error = None
    if not all([request.files['image'], request.form['etablissement'], request.form['post']]):
        error=('Tous les champs sont obligatoires', 'error')
        return render_template('creatobjet.html',session=session,etablissements=etablissement,error=error)

    image_file = request.files['image']
    etablissement_name = request.form['etablissement']
    post_text = request.form['post']
    etablissement= model.found_etablisement(etablissement_name)
    if etablissement is None:
        error =('Établissement invalide', 'error')
        return render_template('creatobjet.html',session=session,etablissements=etablissement,error=error)

    filename = save_uploaded_file(image_file)

            # Enregistrement en base
    model.add_objet(
        image=filename,  
        etid=etablissement['id'],  
        post=post_text
        )

    flash('Objet ajouté avec succès!', 'success')
    return redirect(url_for('index'))

    
    
@app.route('/modifier_obj/<int:id>', methods=['GET'])
def modifier_obj(id):
    objet = model.detail_objet(id)
    courant = model.get_etablissement_name(objet['etid'])
    
    etablissements = model.liste_etablissement()
    
    return render_template('updateobjet.html', 
                         objet=objet,
                         courant=courant, 
                         etablissements=etablissements)


@app.route('/modifier_obj/<int:id>', methods=['post'])
def updateobj(id):
    objet = model.detail_objet(id)
    courant = model.get_etablissement_name(objet['etid'])
    error = None
    etablissements = model.liste_etablissement()

    objet = model.detail_objet(id)
    image = objet['image']
    image_file= request.files['image']
    post=request.form['post']
    etablissement = request.form['etablissement']

    etid=model.found_etablisement(etablissement) 
    if not etid:
        error = "Nous n'avont pas trouver cet etablissement" 
        return render_template('updateobjet.html', 
                         objet=objet,
                         courant=courant, 
                         etablissements=etablissements,error=error)
    
    if image==image_file.filename or not image_file:
        res = model.update_objet(image,etid['id'],post,id)
        return redirect(url_for('detail',id=id))
    
    filname= save_uploaded_file(image_file)
    res = model.update_objet(filname,etid['id'],post,id)

    return redirect(url_for('detail',id=id))


                                        ######################
                                        #   administrateur   #
                                        ######################


@app.get('/admi')
def  admi():
    error=None
    return render_template('admi.html', session = session,error=error)
    
@app.post('/admi')
def add_admi():
    error = None
    password= request.form['password']
    res = model.add_admi(session['username'],password)
    if res == -1:
        error = "vous étes déjà administrateur"
        return render_template('admi.html', session = session,error=error)
    elif res==-2:
        error = "mots de passe incorect "
        return render_template('admi.html', session = session,error=error)

    else:
        return redirect(url_for('index'))

