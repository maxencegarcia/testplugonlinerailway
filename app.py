#! /usr/bin/python
# -*- coding:utf-8 -*-
"""
SCRIPT DE DIAGNOSTIC - À utiliser temporairement sur Railway
Ce script affiche les erreurs exactes au démarrage
"""

import os
import sys
import traceback
from flask import Flask

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'

# Afficher les informations de diagnostic
print("=" * 80)
print("🔍 DIAGNOSTIC DE DÉMARRAGE")
print("=" * 80)

# 1. Vérifier les variables d'environnement
print("\n📋 VARIABLES D'ENVIRONNEMENT:")
env_vars = ['MYSQLHOST', 'MYSQLUSER', 'MYSQLPASSWORD', 'MYSQLDATABASE', 'MYSQLPORT', 'PORT']
for var in env_vars:
    value = os.environ.get(var)
    if 'PASSWORD' in var and value:
        print(f"  ✅ {var}: ***")
    elif value:
        print(f"  ✅ {var}: {value}")
    else:
        print(f"  ❌ {var}: NON DÉFINIE")

# 2. Vérifier le répertoire courant et les fichiers
print("\n📂 STRUCTURE DU PROJET:")
print(f"  Répertoire courant: {os.getcwd()}")
print(f"  Contenu:")
try:
    for item in sorted(os.listdir('.')):
        if os.path.isdir(item):
            print(f"    📁 {item}/")
            if item == 'controllers':
                try:
                    controllers_files = os.listdir(item)
                    print(f"       → {len(controllers_files)} fichiers trouvés")
                    for cf in sorted(controllers_files)[:5]:  # Afficher les 5 premiers
                        print(f"         • {cf}")
                except Exception as e:
                    print(f"       → ERREUR: {e}")
            elif item == 'templates':
                try:
                    templates_files = os.listdir(item)
                    print(f"       → {len(templates_files)} fichiers/dossiers trouvés")
                except Exception as e:
                    print(f"       → ERREUR: {e}")
        else:
            print(f"    📄 {item}")
except Exception as e:
    print(f"  ❌ ERREUR lors de la lecture du répertoire: {e}")

# 3. Tester les imports un par un
print("\n🔌 TEST DES IMPORTS:")

print("  Testing: import pymysql...")
try:
    import pymysql
    print("  ✅ pymysql OK")
except Exception as e:
    print(f"  ❌ pymysql ERREUR: {e}")

print("  Testing: from dotenv import load_dotenv...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("  ✅ dotenv OK")
except Exception as e:
    print(f"  ❌ dotenv ERREUR: {e}")

print("  Testing: import controllers (structure)...")
try:
    import controllers
    print("  ✅ package 'controllers' trouvé")
except Exception as e:
    print(f"  ❌ package 'controllers' non trouvé: {e}")

# 4. Tester chaque import de controller
controllers_to_test = [
    'auth_security',
    'fixtures_load',
    'client_ski',
    'client_panier',
    'client_commande',
    'client_commentaire',
    'client_coordonnee',
    'client_liste_envies',
    'admin_ski',
    'admin_declinaison_ski',
    'admin_commande',
    'admin_type_ski',
    'admin_dataviz',
    'admin_commentaire'
]

print("\n🔌 TEST DES CONTROLLERS:")
failed_imports = []
for controller in controllers_to_test:
    try:
        exec(f"from controllers.{controller} import *")
        print(f"  ✅ controllers.{controller}")
    except Exception as e:
        print(f"  ❌ controllers.{controller}: {str(e)[:60]}")
        failed_imports.append((controller, str(e)))

# 5. Tester la connexion MySQL
print("\n🔌 TEST CONNEXION MYSQL:")
try:
    from flask import g
    import pymysql.cursors
    
    connection = pymysql.connect(
        host=os.environ.get('MYSQLHOST'),
        user=os.environ.get('MYSQLUSER'),
        password=os.environ.get('MYSQLPASSWORD'),
        database=os.environ.get('MYSQLDATABASE'),
        port=int(os.environ.get('MYSQLPORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("  ✅ Connexion MySQL réussie")
    
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"  ✅ Version MySQL: {version}")
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"  ✅ Nombre de tables: {len(tables)}")
    
    connection.close()
    
except Exception as e:
    print(f"  ❌ Connexion MySQL ÉCHOUÉE:")
    print(f"     {traceback.format_exc()}")

# 6. Afficher le résumé
print("\n" + "=" * 80)
print("📊 RÉSUMÉ DU DIAGNOSTIC")
print("=" * 80)

if failed_imports:
    print(f"\n❌ {len(failed_imports)} CONTROLLERS ÉCHOUÉS:")
    for controller, error in failed_imports:
        print(f"\n  • {controller}:")
        print(f"    {error[:200]}")
    print("\n⚠️  L'APPLICATION NE PEUT PAS DÉMARRER CAR DES IMPORTS ÉCHOUENT")
else:
    print("\n✅ TOUS LES CONTROLLERS IMPORTÉS AVEC SUCCÈS")
    print("✅ SI VOUS VOYEZ CE MESSAGE, LE PROBLÈME EST AILLEURS")

print("\n" + "=" * 80)

# Route de test
@app.route('/')
def home():
    return """
    <html>
    <head><title>Diagnostic App</title></head>
    <body style="font-family: Arial; padding: 50px; background: #f0f0f0;">
        <h1>✅ L'application Flask démarre !</h1>
        <p>Consultez les logs Railway pour voir le diagnostic complet.</p>
        <p>Si vous voyez cette page, Gunicorn et Flask fonctionnent.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Application running'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Démarrage de l'application sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
