#! /usr/bin/python
# -*- coding:utf-8 -*-
import os
from flask import Flask, request, render_template, redirect, url_for, flash, session, g
from dotenv import load_dotenv
import pymysql.cursors

# 1. Charger l'environnement en premier
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'une_cle_par_defaut_tres_longue')

# 2. Gestion de la base de données (unique source de vérité)
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=os.environ.get('MYSQLHOST'),
            user=os.environ.get('MYSQLUSER'),
            password=os.environ.get('MYSQLPASSWORD'),
            database=os.environ.get('MYSQLDATABASE'),
            port=int(os.environ.get('MYSQLPORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 3. Imports des Blueprints (APRES la définition de get_db pour éviter les erreurs d'import)
from controllers.auth_security import auth_security
# ... importez les autres ici ...

app.register_blueprint(auth_security)
# ... enregistrez les autres ici ...

@app.route('/')
def show_accueil():
    if 'role' in session:
        return redirect('/admin/commande/index') if session['role'] == 'ROLE_admin' else redirect('/client/ski/show')
    return render_template('auth/layout.html')

@app.before_request
def before_request():
    if request.path.startswith('/admin') or request.path.startswith('/client'):
        if 'role' not in session:
            return redirect('/login')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
