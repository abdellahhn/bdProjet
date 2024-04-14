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

                request = ("INSERT INTO panier (id_Article, id_client, quantite, prix_total) VALUES (%s, %s, %s, %s)")
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


if __name__ == "__main__":
    products = getProductsFromPanier("abdellahhanane44@gmail.com")
    print(products)  # Test fetching products
