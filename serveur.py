import hashlib

from flask import Flask, render_template, request, jsonify
import pymysql, pymysql.cursors
from passlib.hash import sha256_crypt
from Database import getProductsFromDataBase, addNewClientToDB, verifUtilisateur, addProductToCartInDataBase

app = Flask(__name__)


@app.route("/")
def main():
    products = getProductsFromDataBase()
    return render_template("home.html", products=products)


@app.route("/panier", methods=["GET"])
def panier():
    return render_template("panier.html")


# @app.route("/Confirmation")
# def confirmatin():
#     return render_template("confirmation.html")


# @app.route("/commandes", methods=["GET"])
# def commandes():
#     return render_template("commades.html", )


@app.route("/panier", methods=["GET"])
def Panier():
    return render_template("panier.html")


@app.route("/signup", methods=["GET"])
def inscription():
    return render_template("signup.html")


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
    data = request.json

    email = data["email"]
    password = data["motdepasse"]

    # hasher = hashlib.sha3_224()
    # hasher.update(password.encode('utf-8'))
    # password = hasher.hexdigest()

    presentInDb = verifUtilisateur(email, password)
    print(presentInDb)

    if presentInDb:
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

    email = data["email"]
    quantite = data["quantite"]

    addProductToCartInDataBase(quantite, email)

    response = {
        "status": 200
    }
    return jsonify(response)



if __name__ == "__main__":
    app.run()
