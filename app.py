#! /usr/bin/python
# -*- coding:utf-8 -*-
import os
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from dotenv import load_dotenv
import pymysql.cursors

# Charger les variables d'environnement
load_dotenv()

# Import des blueprints
from controllers.auth_security import auth_security
from controllers.fixtures_load import fixtures_load
from controllers.client_ski import client_ski
from controllers.client_panier import client_panier
from controllers.client_commande import client_commande
from controllers.client_commentaire import client_commentaire
from controllers.client_coordonnee import client_coordonnee
from controllers.client_liste_envies import client_liste_envies
from controllers.admin_ski import admin_ski
from controllers.admin_declinaison_ski import admin_declinaison_ski
from controllers.admin_commande import admin_commande
from controllers.admin_type_ski import admin_type_ski
from controllers.admin_dataviz import admin_dataviz
from controllers.admin_commentaire import admin_commentaire

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'


# Fonction de connexion à la base de données
def get_db():
    """Connexion à la base de données MySQL"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.environ.get('MYSQLHOST'),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            database=os.environ.get('MYSQLDATABASE'),
            port=int(os.environ.get('MYSQLPORT', 3306)),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


# Fermeture de la connexion à la fin de chaque requête
@app.teardown_appcontext
def teardown_db(exception):
    """Ferme la connexion DB à la fin de chaque requête"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Route d'accueil
@app.route('/')
def show_accueil():
    """Page d'accueil - redirige selon le rôle de l'utilisateur"""
    if 'role' in session:
        if session['role'] == 'ROLE_admin':
            return redirect('/admin/commande/index')
        else:
            return redirect('/client/ski/show')
    return render_template('auth/layout.html')


# Middleware de sécurité
@app.before_request
def before_request():
    """Vérifie les autorisations avant chaque requête admin/client"""
    if request.path.startswith('/admin') or request.path.startswith('/client'):
        print('session start with /admin or /client')
        
        # Vérification de la présence d'un rôle
        if 'role' not in session:
            return redirect('/login')
        
        # Vérification de l'autorisation selon le rôle
        print('role', session['role'])
        if (request.path.startswith('/client') and session['role'] != 'ROLE_client') or \
           (request.path.startswith('/admin') and session['role'] != 'ROLE_admin'):
            print('pb de route : ', session['role'], request.path.title(), ' => deconnexion')
            session.pop('login', None)
            session.pop('role', None)
            flash("PB route / rôle / autorisation", "alert-warning")
            return redirect('/logout')


# Enregistrement des blueprints
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


# Point d'entrée de l'application
if __name__ == "__main__":
    # Railway fournit automatiquement le port via la variable PORT
    port = int(os.environ.get("PORT", 5000))
    # Écoute sur 0.0.0.0 pour accepter les connexions externes
    app.run(host='0.0.0.0', port=port, debug=False)
