CREATE DATABASE testdb;
USE testdb;

show tables;

SHOW DATABASES;

 -- Création de la base de donnée

CREATE DATABASE GLO2005_PROJECT;

USE GLO2005_PROJECT;

 -- Création des tables
DROP TABLE Client;
CREATE TABLE Client (id_client int AUTO_INCREMENT primary key, email varchar(40), password varchar(255), nom varchar(25), prenom varchar(20), genre varchar(25), age int, adresse varchar(100));
SELECT * FROM Client;

DROP TABLE IF EXISTS Article;
CREATE TABLE Article (id_Article int AUTO_INCREMENT primary key, image varchar(10000),quantite int, type varchar(25), prix int, Marque varchar(50), Nom_Article varchar(25), note_moyenne double);
SELECT * FROM Article;

ALTER TABLE Client
MODIFY COLUMN id_client INT AUTO_INCREMENT PRIMARY KEY;

DROP TABLE IF EXISTS Acheter;
CREATE TABLE Acheter (id_Achat VARCHAR(200) primary key REFERENCES Transaction(id_Transaction), id_client char(25) REFERENCES Client(id_client), id_Article char(15) REFERENCES Article(id_Article));
SELECT * FROM Acheter;

DROP TABLE IF EXISTS Transaction;
CREATE TABLE Transaction (id_Transaction VARCHAR(200) primary key, id_client char(25) REFERENCES Client(id_client), id_panier varchar(36) REFERENCES Panier(id_panier), prix int, date_transaction date, adresse_livraison varchar(55));
SELECT * FROM Transaction;

DROP TABLE IF EXISTS Avis;
CREATE TABLE Avis (id_Avis varchar(200) primary key, id_Article char(15) REFERENCES Article(id_Article), id_client char(25) REFERENCES Client(id_client), Note int, Commentaire varchar(55));
SELECT * FROM Avis;

DROP TABLE IF EXISTS Carte_de_crédit;
CREATE TABLE Carte_de_crédit (numero_carte varchar(30) primary key, type varchar(25), date_expiration date, code_sécurité int, nom varchar(60));
SELECT * FROM Carte_de_crédit;

DROP TABLE IF EXISTS panier;
CREATE TABLE panier (id_panier varchar(36) primary key , id_Article char(15) references Article(id_Article), id_client char(25) references Client(id_client), quantite int, prix_total int);
SELECT * FROM panier;

DROP TABLE IF EXISTS connexion_client;
CREATE TABLE connexion_client (id_connexion char(35), id_client char(25), connexion date, heure_navigation int);
SELECT * FROM connexion_client;

SHOW TABLES;

 -- fonction qui vérifie si l'adresse email figure dans la bd

delimiter //
CREATE FUNCTION emailExiste(le_mail varchar(50)) RETURNS integer
BEGIN
DECLARE EXISTE integer;
DECLARE compte integer;
    SELECT COUNT(U.email) INTO compte FROM client U WHERE email = le_mail;
    IF compte >= 1 THEN SET EXISTE := 1;
    ELSE
        SET EXISTE :=0;
        END IF;
    RETURN EXISTE;
END//

DELIMITER ;

 -- fonction qui retourne le mot de passe associé à l'adresse courriel

DELIMITER //
CREATE FUNCTION passwordUser(le_email varchar(50)) RETURNS varchar(400)
BEGIN
DECLARE password varchar(400);
    SELECT U.password INTO password FROM Client U WHERE email = le_email;
    RETURN password;
END//
DELIMITER ;

 -- Vérifier si un article possède une note déjà présente

DELIMITER //
CREATE FUNCTION note_presente(idarticle int) RETURNS INT
BEGIN
    DECLARE note_count INT;
    SELECT COUNT(*) into note_count FROM Avis where id_Article = id_Article;
    IF note_count > 0 THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
END//
DELIMITER ;

 -- une fonction qui calcule la note moyenne d'un article

DELIMITER //
CREATE FUNCTION average_note(article_id char) RETURNS DOUBLE
BEGIN
DECLARE total NUMERIC;
DECLARE nombre INT;
    SELECT SUM(note) INTO total FROM Avis WHERE id_Article = article_id;
    SELECT COUNT(*) INTO nombre FROM Avis WHERE id_Article = article_id;
    IF nombre > 0 THEN
        RETURN total / nombre;
    ELSE
        RETURN NULL;
    END IF;
END//
DELIMITER ;

 -- une gachette qui permet de savoir si les informations de la livraison sont valides

CREATE TRIGGER gachette_livraison
BEFORE INSERT ON transaction
FOR EACH ROW
BEGIN
    IF NEW.adresse_livraison IS NULL OR NEW.ville_livraison IS NULL OR NEW.postal_livraison IS NULL OR NEW.pays_livraison IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Les informations d''adresse de livraison doivent être complètes.';
    END IF;
END;

 -- une gachette qui permet de mettre à jours les prix des produits CHANGER POUR NOTE!!!!!!

CREATE TRIGGER mis_à_jour_note_article
AFTER UPDATE ON Avis
FOR EACH ROW
BEGIN
    UPDATE Avis SET total_amount = (NEW.prix * Article.quantite) WHERE id_Article = NEW.id_Article;
END;


 -- Une gachette qui permet d'avoir l'historique des transactions

CREATE TRIGGER transaction_historique_gachette
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    INSERT INTO transaction_historique (transaction_id, date_transaction, id_client, total_prix)
    VALUES (NEW.id_Transaction, NEW.date_transaction, NEW.id_client, NEW.prix);
END;

 -- Une procédure qui sert à ajouter un article dans la bd

# CREATE PROCEDURE ajouter_article(IN id_utilisateur INT,IN quantite_article INT, IN id_article_ajout varchar(25), IN prix_article int,IN type_article VARCHAR(25),IN titre_article VARCHAR(255), IN marque_article_ajoute VARCHAR(255))
# BEGIN
#     DECLARE id_article INT;
#
#     -- Vérifier si l'article existe déjà dans la base de données
#     SELECT id_article INTO id_article FROM Article WHERE titre_article = Article.Nom_Article AND marque_article_ajoute = Article.Marque;
#
#     IF id_article IS NULL THEN
#         INSERT INTO Article(id_Article, quantité, type, prix, Marque, Nom_Article) VALUES (id_article_ajout, quantite_article, type_article, prix_article, marque_article_ajoute, titre_article);
#         SET id_article = LAST_INSERT_ID();
#     END IF;
#
#     INSERT INTO possederArticle (id_client, id_article) VALUES (id_utilisateur, id_article_ajout);
# END;

 -- Une procédure qui sert à ajouter un article dans le panier du site
DROP PROCEDURE IF EXISTS AddProductToBasket;

DELIMITER //

CREATE PROCEDURE AddProductToBasket(
    IN p_id_client CHAR(15),
    IN p_id_article CHAR(15),
    IN p_quantite INT
)
BEGIN
    DECLARE basket_exists INT;
    DECLARE p_prix_total INT;
    DECLARE rem_quant INT;

    -- Check if the basket for the client already exists
    SELECT COUNT(*) INTO basket_exists FROM panier WHERE id_client = p_id_client and id_Article = p_id_article;

    -- Get the price of the article
    SELECT prix INTO p_prix_total FROM Article WHERE id_Article = p_id_article;

    -- Calculate the total price for the items being added to the basket
    SET p_prix_total = p_prix_total * p_quantite;

    IF basket_exists = 0 THEN
        -- If the basket doesn't exist, create one
        INSERT INTO panier (id_panier, id_Article, id_client, quantite, prix_total)
        VALUES (UUID(), p_id_article, p_id_client, p_quantite, p_prix_total);
    ELSE
        -- If the basket exists, update the quantity and total price
        UPDATE panier
        SET quantite = quantite + p_quantite,
            prix_total = prix_total + p_prix_total
        WHERE id_client = p_id_client;
    UPDATE Article SET quantite = quantite - p_quantite WHERE id_Article = p_id_article;
    END IF;
END //

DELIMITER ;



DROP PROCEDURE IF EXISTS RemoveProductfromBasket;
DELIMITER //
CREATE PROCEDURE RemoveProductfromBasket(
    IN p_id_client CHAR(15),
    IN p_id_article CHAR(15)
)
BEGIN
    DECLARE basket_exists INT;
    DECLARE p_quantite INT;

    -- Check if the basket for the client already exists
    SELECT COUNT(*) INTO basket_exists FROM panier WHERE id_client = p_id_client
                                                     AND id_Article = p_id_article;
    SELECT quantite into p_quantite from panier where id_Article = p_id_article;
    IF basket_exists = 0 THEN
        -- If the basket doesn't exist, create one
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No matching article found in your basket.';
    ELSE
        -- If the basket exists, update the quantity and total price
        DELETE from panier
        WHERE id_client = p_id_client and id_Article = p_id_article;
        UPDATE Article SET quantite = quantite + p_quantite WHERE id_Article = p_id_article;
    END IF;
END //

DELIMITER ;




-- Tests de recherche et d'ajout d'article dans le panier
CALL AddProductToBasket(10756,1204,1);
CALL AddProductToBasket(10756,1395,1);
CALL AddProductToBasket(10851,1395,2);
CALL AddProductToBasket(10756,1428,1);
CALL AddProductToBasket(11077,1428,3);
CALL AddProductToBasket(10851,1672,1);

CALL RemoveProductfromBasket(10756, 1204);



-- Recherche de la dernière connexion d'un utilisateur
SELECT MAX(connexion) AS derniere_connexion
FROM connexion_client
WHERE utilisateur = 'nom_utilisateur';

-- Recherche de la disponibilté des articles selon la marque et la categorie
SELECT *
FROM stock_article
WHERE stock > 0
ORDER BY categorie ASC, marque ASC;


-- Enregistrer si un article est en rupture de stock

UPDATE stock_article
SET prix = :nouveau_prix, stock = :nouveau_stock, rupture_stock = :rupture
WHERE id = :produit_id;


-- Récupérer les articles achetées par un client donné

SELECT c.nom, c.adresse
FROM client c
INNER JOIN acheter a on c.id_client = a.id_client
INNER JOIN article a2 on a.id_Article = a2.id_Article
WHERE c.id_client = :client_id;


-- curseur qui sert à récupérer les données d'articles de sport à partir de la table accessoire

DECLARE @id INT, @nom VARCHAR(50), @categorie VARCHAR(50)

DECLARE cursorAccessoiresSport CURSOR FOR
SELECT id_accessoire, nom_accessoire, categorie
FROM accessoires_sport

OPEN cursorAccessoiresSport

FETCH NEXT FROM cursorAccessoiresSport INTO @id, @nom, @categorie

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Faire quelque chose avec les données récupérées
    -- Par exemple, afficher le nom et la catégorie de chaque article
    PRINT 'Nom: ' + @nom + ', Catégorie: ' + @categorie

    FETCH NEXT FROM cursorAccessoiresSport INTO @id, @nom, @categorie
END

CLOSE cursorAccessoiresSport

-- curseur qui sert à récupérer les données concernant les accessoires "chaussures de sport"

DECLARE @id INT, @nom VARCHAR(50), @categorie VARCHAR(50)

DECLARE cursorAccessoiresSport CURSOR FOR
SELECT id_accessoire, nom_accessoire, categorie
FROM accessoires_sport
WHERE categorie = 'chaussures de sport'

OPEN cursorAccessoiresSport

FETCH NEXT FROM cursorAccessoiresSport INTO @id, @nom, @categorie

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Faire quelque chose avec les données récupérées
    -- Par exemple, afficher le nom et la catégorie de chaque chaussure de sport
    PRINT 'Nom: ' + @nom + ', Catégorie: ' + @categorie

    FETCH NEXT FROM cursorAccessoiresSport INTO @id, @nom, @categorie
END
-- Tests d'insertion

# insert into Vendre(id_vente, id_client, id_Article) VALUES ('AFAFACACAGF', 'ezhbzjev85', 'zeguekkazeyf');
# insert into possederArticle(id_Article, id_client) values ('AYAFETVEH485', 'ALYXCV89');
# INSERT INTO panier(id_panier, id_Article, id_client, quantite, prix_total) VALUES ('ARATFEV', 'UABZYEB', 'GAGZVEHE45', 5, 145);
# INSERT INTO Client(id_client, email, password, nom, prenom, genre, age, adresse) VALUES ('ALUV45', 'ali.45@gmail.com', 'cours', 'Boustta', 'Ali', 'Homme', 25, '2220 Avenue BouleBAleBile');
# INSERT INTO Avis(id_Avis, id_Article, id_client, Note, Commentaire) values
#     ('uiezaeu', 'zaeze', 'bveve', 6.5, 'Larticle est bien mais pas trés top quand même.'),
#     ('ghjerfe', 'MERCCR7NK', 'ALUV45', 6.5, 'Larticle est bien mais pas trés top quand même.');
# INSERT INTO Acheter(id_Achat, id_client, id_Article) VALUES ('zaee', 'ezrjr', 'erzrr');
INSERT INTO Article(id_Article, quantite, type, prix, Marque, Nom_Article, note_moyenne) values
    (id_Article, "https://cdn.shopify.com/s/files/1/0295/2563/9247/products/YeezySlidesRed_800x.png", 4, 'Complément alimentaire', 45, 'Venum', 'Gants de boxe Venum', 3),
    (id_Article, "https://image.goat.com/1000/attachments/product_template_pictures/images/075/054/238/original/952291_00.png.png",3, 'Crampons de foot', 100, 'Nike', 'Mercurial CR7 Edition', 5);
# INSERT INTO Carte_de_crédit(numero_carte, type, date_expiration, code_sécurité, nom) VALUES (45401202, 'Visa', 12-01-2023, 459, 'Mirabel', 'Paul');
# insert into Transaction(id_Transaction, id_client, id_Article, date_transaction, adresse_livraison, ville_livraison, postal_livraison, pays_livraison, prix)  values ('zaeezaze', 'ALUXC78', 'HGTRDG45', 30-10-2005, '2220 Avenue Sainte-foy', 'Québec', 'G1V F74', 'Canada', 450);

CLOSE cursorAccessoiresSport


