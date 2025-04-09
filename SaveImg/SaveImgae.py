import os
from werkzeug.utils import secure_filename

def post_data_to_entreprise(form_data, file_data):
    """
    form_data : request.form (données texte)
    file_data : request.files (fichier image)
    """
    services = parse_user_list(form_data['services']) if 'services' in form_data else []

  
    logo_file = file_data.get('logo')
    if logo_file and logo_file.filename != '':
        filename = secure_filename(logo_file.filename)
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logo_file.save(logo_path)
    else:
        logo_path = ''  

    return {
        'nom_entreprise': form_data['nom_entreprise'],
        'adresse': form_data['adresse'],
        'telephone': form_data['telephone'],
        'description': form_data['description'],
        'logo': logo_path,  # Chemin relatif sauvegardé
        'user_id': session['id'],
        'services': services
    }

@app.post('/create')
@login_required
def create_post():
    user_id = session.get('id')
    existing = model.get_enterprise_by_user_id(user_id)
    if existing:
        return "Vous avez déjà créé une entreprise. Veuillez utiliser la page de modification pour la mettre à jour."

    # Utilise la fonction corrigée avec form ET files
    enterprise_data = post_data_to_entreprise(request.form, request.files)
    
    id = model.create(enterprise_data)
    return redirect(url_for('read', id=str(id)))


@app.get('/read/<id>')
def read(id):
  entreprise = model.read(int(id))
  if(session['role']=='admin'):
     admin=True
  
  else :
     admin=False

  return render_template('read.html',isLogin=True, entreprise=entreprise, admin=admin)


