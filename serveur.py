import hashlib

from flask import Flask, render_template, request, jsonify
import pymysql, pymysql.cursors
from passlib.hash import sha256_crypt
from Database import getProductsFromDataBase, addNewClientToDB

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

        hasher = hashlib.sha3_224()
        hasher.update(password.encode('utf-8'))

        print(hasher)
        print(hasher.update(password.encode('utf-8')))
        print(hasher.hexdigest())

        addNewClientToDB(email, password, nom, prenom, genre, age, adresse)
        response = {
            "status": 200
        }
        return jsonify(response)
    except Exception as e:
        print("Error", e)
        reponse = {
            "status": 500,
            "message": "erreur pendant requete"
        }
        return jsonify(reponse), 500


if __name__ == "__main__":
    app.run()
