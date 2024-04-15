import datetime
import uuid

import pymysql


def establish_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="qwertyuiop",
            db="GLO2005_PROJECT",
            autocommit=True
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def getProductsFromDataBase():
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = "SELECT * FROM Article"
                cursor.execute(request)
                products = cursor.fetchall()
                return products
        except pymysql.Error as e:
            print(f"Error fetching products from the database: {e}")
        finally:
            connection.close()
    else:
        print("Database connection not established.")
        return []


def getProductsFromPanier(user_email):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Get the id_client from the Client table using the user_email
                cursor.execute("SELECT id_client FROM Client WHERE email=%s", (user_email,))
                client_id = cursor.fetchone()
                if client_id is None:
                    print("User not found.")
                    return []

                # Fetch products from the panier table for the given client_id
                request = """
                    SELECT p.quantite, p.prix_total, a.Nom_Article AS article_name
                    FROM panier p
                    INNER JOIN Article a ON p.id_Article = a.id_Article
                    WHERE p.id_client = %s
                """
                cursor.execute(request, (client_id[0],))
                products = cursor.fetchall()

                return [
                    {"quantity": row[0], "total_price": row[1], "article_name": row[2]}
                    for row in products
                ]
        except pymysql.Error as e:
            print(f"Error fetching products from panier table: {e}")
        finally:
            connection.close()
    else:
        print("Database connection not established.")
        return []


def addNewClientToDB(email, password, nom, prenom, genre, age, adresse):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = f'''INSERT INTO Client (email, password, nom, prenom, genre, age, adresse) 
                             VALUES ('{email}', '{password}', '{nom}', '{prenom}', '{genre}', {age}, '{adresse}');'''
                cursor.execute(request)
        except pymysql.Error as e:
            print("Error:", e)
        finally:
            connection.close()
    else:
        print("Database connection not established.")


def verifUtilisateur(email, password):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = """SELECT COUNT(*) FROM Client WHERE email = %s AND password = %s"""
                cursor.execute(request, (email, password))
                count = cursor.fetchone()[0]
                return count > 0
        except pymysql.Error as e:
            print("Error:", e)
            return False
        finally:
            connection.close()
    else:
        print("Database connection not established.")
        return False


def addProductToCartInDataBase(nom, quantite, email, prix):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_client FROM Client WHERE email=%s", (email,))
                client_id = cursor.fetchone()[0]
                print(client_id)

                cursor.execute("SELECT id_Article FROM Article WHERE Nom_Article=%s", (nom,))
                article_id = cursor.fetchone()[0]
                print(article_id)

                request = ("INSERT INTO panier (id_panier, id_Article, id_client, quantite, prix_total) VALUES (UUID("
                           "), %s, %s, %s, %s)")
                cursor.execute(request, (article_id, client_id, quantite, prix))

                connection.commit()
                return True

        except pymysql.Error as e:
            print("Error:", e)
            return False

        finally:
            connection.close()
    else:
        print("Database connection not established.")
        return False


def addArticleToDB(quantite, nom, marque, prix, type, image, note_moyenne=None):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = """
                    INSERT INTO Article (quantite, image, type, nom_article, prix, note_moyenne, marque) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(request, (quantite, image, type, nom, prix, note_moyenne, marque))
                connection.commit()
                print("Article ajouté avec succès!")
                return True
        except pymysql.Error as err:
            print(f"Error adding article: {err}")
            return False
        finally:
            connection.close()
    else:
        print("Database connection not established.")
        return False


def dropCartInDataBase(id_client):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = f""" delete FROM panier where id_client = '{id_client}'"""
                cursor.execute(request)
                connection.commit()
                print("panier vidée avec succès!")
        except pymysql.Error as err:
            print(f"Error deleting panier: {err}")
        finally:
            if connection:
                connection.close()


def changerQuantiteArticle(id_panier):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Récupérer l'id de l'article associé à l'id du panier
                cursor.execute("SELECT id_Article, quantite FROM panier WHERE id_panier = %s", (id_panier,))
                result = cursor.fetchone()
                if result:
                    article_id, quantite_panier = result
                    # Récupérer la quantité actuelle de l'article dans la table Article
                    cursor.execute("SELECT quantite FROM Article WHERE id_Article = %s", (article_id,))
                    quantite_article = cursor.fetchone()[0]

                    if quantite_article >= quantite_panier:
                        # Réduire la quantité de l'article dans la table Article
                        nouvelle_quantite = quantite_article - quantite_panier
                        cursor.execute("UPDATE Article SET quantite = %s WHERE id_Article = %s",
                                       (nouvelle_quantite, article_id))
                        connection.commit()
                        print(f"Quantité de l'article {article_id} mise à jour avec succès.")
                        return True  # Indiquer que la mise à jour a réussi
                    else:
                        print("Quantité insuffisante dans le stock.")
                else:
                    print("Panier introuvable.")
        except pymysql.Error as err:
            print(f"Erreur lors de la mise à jour de la quantité de l'article: {err}")
        finally:
            if connection:
                connection.close()
    return False


def acheterCommandesDB(email, type, numero, code, date):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Insérer les données de la carte de crédit
                request_carte = """
                    INSERT INTO Carte_de_crédit (numero_carte, type, date_expiration, code_sécurité, nom)
                    VALUES (%s, %s, %s, %s, 'lol')
                """
                cursor.execute(request_carte, (numero, type, date, code))
                connection.commit()

                client_info = get_client_info(email)
                if client_info:
                    id_client, adresse_livraison = client_info

                    id_paniers = get_id_panier(id_client)  # Obtenez tous les ID de panier
                    if id_paniers:
                        for id_panier in id_paniers:
                            prix_total = getPrixTotal(id_client, id_paniers)
                            id_transaction = insert_transaction(id_client, id_panier, prix_total,
                                                                adresse_livraison,
                                                                cursor, connection)
                            print(f"Transaction pour le panier {id_panier} ajoutée avec succès!")
                            changerQuantiteArticle(id_panier)
                            articles_panier = get_articles_panier(id_client, id_panier)
                            if articles_panier:
                                for id_article in articles_panier:
                                    request_acheter = """
                                        INSERT INTO Acheter (id_Achat, id_client, id_Article)
                                        VALUES (%s, %s, %s)
                                    """
                                    cursor.execute(request_acheter, (id_transaction, id_client, id_article))
                                    connection.commit()
                                print(
                                    f"Articles achetés du panier {id_panier} ajoutés avec succès dans la table Acheter.")
                                return True  # Indique que l'opération s'est déroulée avec succès
                            else:
                                print(f"Aucun article trouvé dans le panier {id_panier}.")
                    else:
                        print("Aucun panier trouvé pour ce client.")
                else:
                    print("Aucun client trouvé avec cet email.")
        except pymysql.Error as err:
            print(f"Erreur lors de l'insertion des données: {err}")
        finally:
            if connection:
                connection.close()
    return False


def getPrixTotal(id_client, id_panier):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request_prix_total = """
                    SELECT id_Article, quantite FROM panier 
                    WHERE id_client = %s AND id_panier = %s
                """
                cursor.execute(request_prix_total, (id_client, id_panier))
                items = cursor.fetchall()
                prix_total = 0
                for item in items:
                    article_id, quantite = item
                    cursor.execute("SELECT prix FROM Article WHERE id_Article = %s", (article_id,))
                    prix_article = cursor.fetchone()[0]
                    prix_total += prix_article * quantite
                return prix_total

        except pymysql.Error as err:
            print(f"Erreur lors de la récupération du prix total: {err}")
        finally:
            if connection:
                connection.close()
    return None


def insert_transaction(id_client, id_panier, prix_total, adresse_livraison, cursor, connection):
    try:
        transaction_id = uuid.uuid4()
        current_datetime = datetime.datetime.now()
        print(prix_total)

        request_transaction = """
            INSERT INTO Transaction (id_Transaction, id_client, id_panier, prix, date_transaction, adresse_livraison)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(request_transaction, (
            transaction_id,
            id_client,
            id_panier,
            prix_total,
            current_datetime.date(),
            adresse_livraison
        ))
        connection.commit()

        return transaction_id

    except pymysql.Error as err:
        print(f"Erreur lors de l'insertion de la transaction: {err}")
        connection.rollback()  # Rollback on error
        return None


def get_client_info(email):
    connection = establish_connection()
    client_info = None
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_client, adresse FROM Client WHERE email = %s", (email,))
                client_info = cursor.fetchone()
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération des informations du client: {err}")
        finally:
            if connection:
                connection.close()
    return client_info


def get_id_panier(id_client):
    connection = establish_connection()
    paniers_info = []
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_panier FROM Panier WHERE id_client = %s", (id_client,))
                paniers_info = cursor.fetchall()  # Récupère tous les résultats au lieu d'un seul
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération des IDs de panier: {err}")
        finally:
            if connection:
                connection.close()
    return paniers_info


def get_articles_panier(id_client, id_panier):
    connection = establish_connection()
    articles_panier = []
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_Article FROM panier WHERE id_client = %s and id_Panier = %s",
                               (id_client, id_panier))
                articles_panier = cursor.fetchone()
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération des articles du panier: {err}")
        finally:
            if connection:
                connection.close()
    return articles_panier


def getAvisForUser(email):
    connection = establish_connection()
    id_user = get_client_id(email)
    avis_list = []

    if connection and id_user:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT Avis.id_Article, Avis.Note, Avis.Commentaire, Article.Nom_Article
                    FROM Avis
                    INNER JOIN Article ON Avis.id_Article = Article.id_Article
                    WHERE Avis.id_client = %s
                """, (id_user,))
                avis_rows = cursor.fetchall()

                for row in avis_rows:
                    avis = {
                        "nom_article": row[3],
                        "note": row[1],
                        "commentaire": row[2]
                    }
                    avis_list.append(avis)

        except pymysql.Error as err:
            print(f"Erreur lors de la récupération des avis: {err}")
        finally:
            if connection:
                connection.close()

    return avis_list


def get_client_id(email):
    connection = establish_connection()
    client_id = None
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_client FROM Client WHERE email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    client_id = result[0]
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération de l'ID du client: {err}")
        finally:
            if connection:
                connection.close()
    print(client_id)
    return client_id


def get_articles_purchased(email):
    connection = establish_connection()
    id_client = get_client_id(email)
    articles_info = []
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_Article FROM Acheter WHERE id_client = %s", (id_client,))
                results = cursor.fetchall()
                for row in results:
                    article_id = row[0]
                    cursor.execute("SELECT Nom_Article, Marque FROM Article WHERE id_Article = %s", (article_id,))
                    article_info = cursor.fetchone()
                    if article_info:
                        articles_info.append(article_info)
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération des articles achetés: {err}")
        finally:
            if connection:
                connection.close()
    print(articles_info)
    return articles_info


def ajouterUnAvis(email, avis_list):
    connection = establish_connection()
    id_client = get_client_id(email)
    if connection and id_client:
        try:
            with connection.cursor() as cursor:
                for avis_data in avis_list:
                    nom = avis_data["nom"]
                    marque = avis_data["marque"]
                    note = avis_data["note"]
                    avis_commentaire = avis_data["avis"]

                    id_article = get_article_id(nom, marque)
                    if id_article:
                        request_avis = """
                            INSERT INTO Avis (id_Avis, id_Article, id_client, Note, Commentaire)
                            VALUES (UUID(), %s, %s, %s, %s)
                        """
                        cursor.execute(request_avis, (id_article, id_client, note, avis_commentaire))
                        connection.commit()
                        print("Avis ajouté avec succès!")
                    else:
                        print(f"L'article {nom} de la marque {marque} n'a pas été trouvé.")
        except pymysql.Error as err:
            print(f"Erreur lors de l'insertion de l'avis: {err}")
        finally:
            if connection:
                connection.close()
    else:
        print("Impossible d'ajouter l'avis. Vérifiez l'ID client ou la connexion.")


def get_article_id(nom, marque):
    connection = establish_connection()
    article_id = None
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_Article FROM Article WHERE Nom_Article = %s AND Marque = %s", (nom, marque))
                result = cursor.fetchone()
                if result:
                    article_id = result[0]
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération de l'ID de l'article: {err}")
        finally:
            if connection:
                connection.close()
    return article_id


def addConnectionToDB(email):
    connection = establish_connection()
    client_id = get_client_id(email)
    if connection and client_id:
        try:
            with connection.cursor() as cursor:
                current_datetime = datetime.datetime.now()
                id_connexion = uuid.uuid4()
                cursor.execute("""
                    INSERT INTO connexion_client (id_connexion, id_client, connexion, heure_navigation)
                    VALUES (%s, %s, %s, %s)
                """, (id_connexion, client_id, current_datetime.date(), current_datetime.hour))
                connection.commit()
                return True

        except pymysql.Error as err:
            print(f"Erreur lors de l'ajout de la connexion à la base de données: {err}")
            return False
        finally:
            if connection:
                connection.close()
    else:
        print("Erreur lors de la connexion à la base de données ou de l'obtention de l'ID client.")
        return False


if __name__ == "__main__":
    total = getPrixTotal(1, "ac4df9f6-fad9-11ee-a5a0-62be92a17154")
    total2 = total + getPrixTotal(1, "acdfd3c6-fad9-11ee-a5a0-62be92a17154")

    lol = changerQuantiteArticle("f253a1c2-fad8-11ee-a5a0-62be92a17154")

    avis = getAvisForUser("abdellahhanane44@gmail.com")
    print(total2)  # Test fetching products
