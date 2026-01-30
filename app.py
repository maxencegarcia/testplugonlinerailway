#! /usr/bin/python
# -*- coding:utf-8 -*-
"""
Application Flask - E-commerce Ski
Déploiement Railway
"""

import os
import pymysql.cursors
from flask import Flask, request, render_template, redirect, url_for, flash, session, g
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'


# ============================================================================
# CONFIGURATION BASE DE DONNÉES
# ============================================================================

def get_db():
    """Connexion à la base de données MySQL"""
    if 'db' not in g:
        try:
            g.db = pymysql.connect(
                host=os.environ.get('MYSQLHOST'),
                user=os.environ.get('MYSQLUSER'),
                password=os.environ.get('MYSQLPASSWORD'),
                database=os.environ.get('MYSQLDATABASE'),
                port=int(os.environ.get('MYSQLPORT', 3306)),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print(f"❌ ERREUR CONNEXION MYSQL: {e}")
            raise
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    """Ferme la connexion DB à la fin de chaque requête"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ============================================================================
# IMPORT DES CONTROLLERS
# ============================================================================

try:
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
    
    print("✅ Tous les controllers importés avec succès")
    
except ImportError as e:
    print(f"❌ ERREUR D'IMPORT DES CONTROLLERS: {e}")
    print("⚠️  L'application va démarrer mais certaines routes ne fonctionneront pas")


# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.route('/')
def show_accueil():
    """Page d'accueil - redirige selon le rôle de l'utilisateur"""
    if 'role' in session:
        if session['role'] == 'ROLE_admin':
            return redirect('/admin/commande/index')
        else:
            return redirect('/client/ski/show')
    return render_template('auth/layout.html')


# ============================================================================
# MIDDLEWARE DE SÉCURITÉ
# ============================================================================

@app.before_request
def before_request():
    """Vérifie les autorisations avant chaque requête admin/client"""
    if request.path.startswith('/admin') or request.path.startswith('/client'):
        
        # Vérification de la présence d'un rôle
        if 'role' not in session:
            return redirect('/login')
        
        # Vérification de l'autorisation selon le rôle
        if (request.path.startswith('/client') and session['role'] != 'ROLE_client') or \
           (request.path.startswith('/admin') and session['role'] != 'ROLE_admin'):
            session.pop('login', None)
            session.pop('role', None)
            flash("Problème de route / rôle / autorisation", "alert-warning")
            return redirect('/logout')


# ============================================================================
# ENREGISTREMENT DES BLUEPRINTS
# ============================================================================

try:
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
    
    print("✅ Tous les blueprints enregistrés avec succès")
    
except NameError as e:
    print(f"❌ ERREUR D'ENREGISTREMENT DES BLUEPRINTS: {e}")
    print("⚠️  Certains blueprints n'ont pas pu être enregistrés")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    # Railway fournit automatiquement le port via la variable PORT
    port = int(os.environ.get("PORT", 5000))
    
    # Afficher les informations de démarrage
    print("=" * 60)
    print("🚀 DÉMARRAGE DE L'APPLICATION FLASK")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Host: 0.0.0.0")
    print(f"MySQL Host: {os.environ.get('MYSQLHOST', 'NOT SET')}")
    print(f"MySQL Database: {os.environ.get('MYSQLDATABASE', 'NOT SET')}")
    print("=" * 60)
    
    # Démarrer l'application
    app.run(host='0.0.0.0', port=port, debug=False)
