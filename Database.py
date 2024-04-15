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


def addArticleToDB(quantite, nom, marque, prix, note_moyenne=None):  # Allow optional note_moyenne
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = """INSERT INTO Article (quantite, type, nom_article, prix, note_moyenne, marque) 
                             VALUES (%s, %s, %s, %s, %s, %s);"""
                cursor.execute(request, (quantite, '{"nom"}', nom, prix, note_moyenne, marque))

                connection.commit()
                print("Article ajouté avec succès!")
        except pymysql.Error as err:
            print(f"Error adding article: {err}")
        finally:
            if connection:
                connection.close()


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
                            id_transaction = insert_transaction(id_client, id_panier, prix_total, date,
                                                                adresse_livraison,
                                                                cursor, connection)
                            print(f"Transaction pour le panier {id_panier} ajoutée avec succès!")
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


def getPrixTotal(id_client, id_panier):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request_prix_total = """
                    SELECT prix_total FROM panier 
                    WHERE id_client = %s AND id_panier = %s
                """
                cursor.execute(request_prix_total, (id_client, id_panier))
                result = cursor.fetchone()
                if result:
                    prix_total = result[0]
                    return prix_total
                else:
                    print("Aucun prix total trouvé pour ces identifiants.")
                    return None

        except pymysql.Error as err:
            print(f"Erreur lors de la récupération du prix total: {err}")
            return None
        finally:
            connection.close()


def insert_transaction(id_client, id_panier, prix_total, date, adresse_livraison, cursor, connection):
    try:
        transaction_id = uuid.uuid4()

        request_transaction = """
            INSERT INTO Transaction (id_Transaction, id_client, id_panier, prix, date_transaction, adresse_livraison)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(request_transaction, (
            transaction_id,
            id_client,
            id_panier,
            prix_total,
            date,
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
                    article_id = result[0]  # L'ID de l'article est le premier élément du résultat
        except pymysql.Error as err:
            print(f"Erreur lors de la récupération de l'ID de l'article: {err}")
        finally:
            if connection:
                connection.close()
    return article_id


if __name__ == "__main__":
    avis = getAvisForUser("abdellahhanane44@gmail.com")
    print(avis)  # Test fetching products
