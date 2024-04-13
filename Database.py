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


def addProductToCartInDataBase(quantite, email):
    connection = establish_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                request = f""" INSERT into Paniers(id_Produit, email) value ('{id}','{email}')"""
                cursor.execute(request)
        except pymysql.Error as e:
            print("Error:", e)
        finally:
            connection.close()
    else:
        print("Database connection not established.")
        return False


if __name__ == "__main__":
    products = getProductsFromDataBase()
    print(products)  # Test fetching products
