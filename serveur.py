import hashlib

from flask import Flask, render_template, request, jsonify, session
import pymysql, pymysql.cursors
from passlib.hash import sha256_crypt
from Database import getProductsFromDataBase, addNewClientToDB, verifUtilisateur, addProductToCartInDataBase, \
    addArticleToDB, getProductsFromPanier, acheterCommandesDB, get_articles_purchased, ajouterUnAvis, get_client_id, \
    dropCartInDataBase, getAvisForUser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Variable globale pour stocker l'email de l'utilisateur connecté
user_email = None


@app.route("/")
def main():
    global user_email
    products = getProductsFromDataBase()
    return render_template("home.html", user_email=user_email, products=products)


@app.route("/panier", methods=["GET"])
def panier():
    global user_email

    print(user_email)

    if user_email:
        products = getProductsFromPanier(user_email)  # Récupère les produits du panier de l'utilisateur
        return render_template("panier.html", products=products, user_email=user_email)
    else:
        return "Utilisateur non connecté", 401


@app.route("/donnerAvis", methods=["GET"])
def voirAvis():
    global user_email

    if user_email:
        achat = get_articles_purchased(user_email)  # Récupère les produits du panier de l'utilisateur
        return render_template("donnerAvis.html", achats=achat, user_email=user_email)
    else:
        return "Utilisateur non connecté", 401


@app.route("/voirAvis", methods=["GET"])
def voirAvisDonne():
    global user_email

    if user_email:
        avis = getAvisForUser(user_email)
        print(avis)
        return render_template("voirAvis.html", avis=avis, user_email=user_email)
    else:
        return "Utilisateur non connecté", 401


@app.route("/donnerAvis", methods=["POST"])
def donnerAvis():
    global user_email  # Si vous utilisez une variable globale pour stocker l'email de l'utilisateur

    data = request.json
    email = data["email"]
    avis_list = data["rowsData"]  # Assurez-vous de récupérer les données correctement

    presentInDb = ajouterUnAvis(email, avis_list)  # Assurez-vous d'avoir cette fonction

    if presentInDb:
        user_email = email  # Mettez à jour l'email de l'utilisateur si nécessaire
        response = {"status": 200, "message": "Avis ajoutés avec succès"}
    else:
        response = {
            "status": 403,
            "message": "Échec de l'ajout des avis. Veuillez réessayer plus tard."
        }

    return jsonify(response)


@app.route("/commandes", methods=["GET"])
def commandes():
    return render_template("commandes.html")


@app.route("/signup", methods=["GET"])
def inscription():
    return render_template("signup.html")


@app.route("/logout", methods=["GET"])
def deconnexion():
    global user_email
    user_email = None
    return render_template("home.html")


@app.route("/login", methods=["GET"])
def connexion():
    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def createNewUsers():
    try:
        data = request.get_json()

        prenom = data["prenom"]
        nom = data["nom"]
        email = data["email"]
        adresse = data["adresse"]
        age = data["age"]
        genre = data["genre"]
        password = data["password"]

        # hashed_password = sha256_crypt.encrypt(password)  # Implement hashing if needed

        new_user_id = addNewClientToDB(email, password, nom, prenom, genre, age, adresse)

        if new_user_id:
            message = "Compte créé avec succès!"
            message_type = "success"
        else:
            message = "Une erreur est survenue lors de la création du compte."
            message_type = "error"

        signup_notice = {
            "message": message,
            "type": message_type
        }
        return jsonify(signup_notice)

    except Exception as e:
        print("Error:", e)
        message = "Une erreur est survenue lors de la création du compte."
        message_type = "error"
        signup_notice = {
            "message": message,
            "type": message_type
        }
        return jsonify(signup_notice), 500


@app.route("/login", methods=["POST"])
def connection():
    global user_email
    data = request.json

    email = data["email"]
    password = data["motdepasse"]

    presentInDb = verifUtilisateur(email, password)

    if presentInDb:
        user_email = email
        print(user_email)
        response = {
            "status": 200
        }
    else:
        response = {
            "status": 403,
            "reason": "L’adresse e-mail ou le mot de passe que vous avez saisi(e) n’est pas associé(e) à un compte"
        }

    return jsonify(response)


@app.route("/addProductToCart", methods=["POST"])
def addProductToCart():
    data = request.json

    nom = data["nom"]
    email = data["email"]
    quantite = data["quantite"]
    prix = data["prix"]

    addProductToCartInDataBase(nom, quantite, email, prix)

    response = {
        "status": 200
    }
    return jsonify(response)


@app.route("/viderPanier", methods=["POST"])
def viderCart():
    data = request.json

    email = data["email"]
    client_id = get_client_id(email)
    dropCartInDataBase(client_id)
    response = {
        "status": 200
    }
    return jsonify(response)


@app.route("/addArticle", methods=["POST"])
def addArticle():
    data = request.json

    nom = data["nom"]
    prix = data["prix"]
    quantite = data["quantite"]
    marque = data["marque"]

    added = addArticleToDB(quantite, nom, marque, prix)

    if added:
        response = {
            "status": 200,
            "message": "Article ajouté avec succès!"
        }
    else:
        response = {
            "status": 500,
            "message": "Erreur lors de l'ajout de l'article."
        }

    return jsonify(response)


@app.route("/commandes", methods=["POST"])
def acheterCommandes():
    data = request.json

    email = data["email"]
    type = data["type"]
    numero = data["numero"]
    code = data["code"]
    date = data["date"]

    added = acheterCommandesDB(email, type, numero, code, date)

    if added:
        client_id = get_client_id(email)
        if client_id:
            dropCartInDataBase(client_id)

        response = {
            "status": 200,
            "message": "Panier Acheté avec succès!"
        }
    else:
        response = {
            "status": 500,
            "message": "Erreur lors de l'achat."
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run()
