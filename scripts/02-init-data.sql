\c bookshop;

---------------------------
-- 1. Insertion des catégories
---------------------------
-- On définit ici 10 catégories fixes.
INSERT INTO category (id, intitule, created_at) VALUES
(1, 'Roman', NOW()),
(2, 'Science-Fiction', NOW()),
(3, 'Biographie', NOW()),
(4, 'Philosophie', NOW()),
(5, 'Histoire', NOW()),
(6, 'Poésie', NOW()),
(7, 'Essai', NOW()),
(8, 'Théâtre', NOW()),
(9, 'Policier', NOW()),
(10, 'Documentaire', NOW());

---------------------------
-- 2. Insertion de 500 livres
---------------------------
-- Chaque livre se voit attribuer une catégorie aléatoire entre 1 et 10.
-- Les codes et titres sont générés de manière séquentielle.
INSERT INTO books (id, category_id, code, intitule, isbn_10, isbn_13, created_at)
SELECT
    g AS id,
    ((random() * 10)::int + 1) AS category_id,
    'BOOK' || LPAD(g::text, 4, '0') AS code,
    'Titre du Livre ' || g AS intitule,
    LPAD((floor(random() * 1000000000))::text, 10, '0') AS isbn_10,
    LPAD((floor(random() * 10000000000000))::text, 13, '0') AS isbn_13,
    NOW()
FROM generate_series(1,500) g;

---------------------------
-- 3. Insertion de 200 clients
---------------------------
-- Les clients auront des prénoms et noms générés de façon séquentielle.
INSERT INTO customers (id, code, first_name, last_name, created_at)
SELECT
    g AS id,
    'CUS' || LPAD(g::text, 4, '0') AS code,
    'Prenom' || g AS first_name,
    'Nom' || g AS last_name,
    NOW()
FROM generate_series(1,200) g;

---------------------------
-- 4. Insertion de 300 factures
---------------------------
-- La date d'édition est générée en ajoutant un décalage (modulo 30 jours) à la date actuelle.
-- Chaque facture est associée à un client (cyclique de 1 à 200).
INSERT INTO factures (id, code, date_edit, customers_id, qte_totale, total_amount, total_paid, created_at)
SELECT
    g AS id,
    'FAC' || LPAD(g::text, 4, '0') AS code,
    to_char(NOW() + (((g % 30)::text || ' days')::interval), 'YYYYMMDD') AS date_edit,
    ((g - 1) % 200 + 1) AS customers_id,
    (floor(random() * 5) + 1)::int AS qte_totale,
    round((random() * 100 + 20)::numeric, 2) AS total_amount,
    round((random() * 100 + 20)::numeric, 2) AS total_paid,
    NOW()
FROM generate_series(1,300) g;

---------------------------
-- 5. Insertion de 1000 ventes
---------------------------
-- Chaque vente est associée à une facture et à un livre.
-- Le prix unitaire et la quantité sont générés aléatoirement.
INSERT INTO ventes (id, code, date_edit, factures_id, books_id, pu, qte, created_at)
SELECT
    g AS id,
    'VEN' || LPAD(g::text, 4, '0') AS code,
    to_char(NOW() + (((g % 30)::text || ' days')::interval), 'YYYYMMDD') AS date_edit,
    ((g - 1) % 300 + 1) AS factures_id,
    ((g - 1) % 500 + 1) AS books_id,
    round((random() * 50 + 5)::numeric, 2) AS pu,
    (floor(random() * 5) + 1)::int AS qte,
    NOW()
FROM generate_series(1,1000) g;
