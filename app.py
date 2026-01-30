#! /usr/bin/python
# -*- coding:utf-8 -*-

import os
import pymysql.cursors
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from dotenv import load_dotenv

# Initialisation unique de l'application
app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

load_dotenv()

# Import des Blueprints APRES avoir créé 'app'
from controllers.auth_security import *
from controllers.fixtures_load import *
from controllers.client_ski import *
from controllers.client_panier import *
from controllers.client_commande import *
from controllers.client_commentaire import *
from controllers.client_coordonnee import *
from controllers.admin_ski import *
from controllers.admin_declinaison_ski import *
from controllers.admin_commande import *
from controllers.admin_type_ski import *
from controllers.admin_dataviz import *
from controllers.admin_commentaire import *
from controllers.client_liste_envies import *

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="serveurmysql.iut-bm.univ-fcomte.fr",
            user="educret", 
            password="TON_VRAI_MOT_DE_PASSE", # <--- VERIFIE BIEN CA
            database="BDD_educret_sae",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_accueil():
    if 'role' in session:
        if session['role'] == 'ROLE_admin':
            return redirect('/admin/commande/index')
        else:
            return redirect('/client/ski/show')
    return render_template('auth/layout.html')

@app.before_request
def before_request():
     if request.path.startswith('/admin') or request.path.startswith('/client'):
        if 'role' not in session:
            return redirect('/login')

app.register_blueprint(auth_security)
app.register_blueprint(fixtures_load)
app.register_blueprint(client_ski)
app.register_blueprint(client_commande)
app.register_blueprint(client_commentaire)
app.register_blueprint(client_panier)
app.register_blueprint(client_coordonnee)
app.register_blueprint(client_liste_envies)
app.register_blueprint(admin_ski)
app.register_blueprint(admin_declinaison_ski)
app.register_blueprint(admin_commande)
app.register_blueprint(admin_type_ski)
app.register_blueprint(admin_dataviz)
app.register_blueprint(admin_commentaire)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
