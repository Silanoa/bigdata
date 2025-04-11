\c bookshop;

-- ---------------------------------------------------------
-- 1. Insertion des catégories
-- ---------------------------------------------------------
-- On définit 10 catégories fixes
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

-- ---------------------------------------------------------
-- 2. Insertion de 500 livres avec des titres réalistes
-- ---------------------------------------------------------
-- Pour chaque livre, la catégorie est générée aléatoirement (entre 1 et 10)
-- et on utilise un CASE pour quelques titres connus sinon "Livre <id>"
INSERT INTO books (id, category_id, code, intitule, isbn_10, isbn_13, created_at)
SELECT
    g AS id,
    (floor(random() * 10)::int + 1) AS category_id,  -- valeur garantie entre 1 et 10
    'BK' || LPAD(g::text, 4, '0') AS code,
    CASE
        WHEN (g % 10) = 0 THEN 'Les Misérables'
        WHEN (g % 10) = 1 THEN 'Dune'
        WHEN (g % 10) = 2 THEN 'Le Comte de Monte-Cristo'
        WHEN (g % 10) = 3 THEN '1984'
        WHEN (g % 10) = 4 THEN 'L''Étranger'
        WHEN (g % 10) = 5 THEN 'La Peste'
        WHEN (g % 10) = 6 THEN 'Le Petit Prince'
        WHEN (g % 10) = 7 THEN 'Harry Potter à l''école des sorciers'
        WHEN (g % 10) = 8 THEN 'Le Seigneur des Anneaux'
        WHEN (g % 10) = 9 THEN 'Sherlock Holmes'
        ELSE 'Livre ' || g
        END AS intitule,
    LPAD((floor(random() * 1000000000))::text, 10, '0') AS isbn_10,
    LPAD((floor(random() * 10000000000000))::text, 13, '0') AS isbn_13,
    NOW() AS created_at
FROM generate_series(1,500) g;

-- ---------------------------------------------------------
-- 3. Insertion de 200 clients avec des noms réalistes
-- ---------------------------------------------------------
-- On utilise des tableaux de prénoms et noms pour attribuer des valeurs réalistes.
INSERT INTO customers (id, code, first_name, last_name, created_at)
SELECT
    g AS id,
    'CUS' || LPAD(g::text, 4, '0') AS code,
    names.first_names[((g - 1) % cardinality(names.first_names)) + 1] AS first_name,
    names.last_names[((g - 1) % cardinality(names.last_names)) + 1] AS last_name,
    NOW() AS created_at
FROM generate_series(1,200) g,
    LATERAL (
    SELECT
    ARRAY['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Claire', 'Antoine', 'Camille', 'Julien', 'Isabelle', 'Alain', 'Nathalie', 'Céline', 'Philippe', 'Sandrine'] AS first_names,
    ARRAY['Dupont', 'Martin', 'Bernard', 'Lefevre', 'Moreau', 'Durand', 'Dubois', 'Laurent', 'Garcia', 'Petit', 'Rousseau', 'Fournier', 'Morel', 'Girard', 'André'] AS last_names
    ) names;

-- ---------------------------------------------------------
-- 4. Insertion de 300 factures
-- ---------------------------------------------------------
-- Chaque facture est attribuée à un client de manière cyclique (1 à 200)
-- La date d'édition est générée en ajoutant un décalage allant jusqu'à 29 jours
INSERT INTO factures (id, code, date_edit, customers_id, qte_totale, total_amount, total_paid, created_at)
SELECT
    g AS id,
    'FAC' || LPAD(g::text, 4, '0') AS code,
    to_char(NOW() + (((g % 30)::text || ' days')::interval), 'YYYYMMDD') AS date_edit,
    ((g - 1) % 200 + 1) AS customers_id,
    (floor(random() * 5) + 1)::int AS qte_totale,
    round((random() * 100 + 20)::numeric, 2) AS total_amount,
    round((random() * 100 + 20)::numeric, 2) AS total_paid,
    NOW() AS created_at
FROM generate_series(1,300) g;

-- ---------------------------------------------------------
-- 5. Insertion de 1000 ventes
-- ---------------------------------------------------------
-- Chaque vente est associée à une facture (1 à 300) et à un livre (1 à 500)
INSERT INTO ventes (id, code, date_edit, factures_id, books_id, pu, qte, created_at)
SELECT
    g AS id,
    'VEN' || LPAD(g::text, 4, '0') AS code,
    to_char(NOW() + (((g % 30)::text || ' days')::interval), 'YYYYMMDD') AS date_edit,
    ((g - 1) % 300 + 1) AS factures_id,
    ((g - 1) % 500 + 1) AS books_id,
    round((random() * 50 + 5)::numeric, 2) AS pu,
    (floor(random() * 5) + 1)::int AS qte,
    NOW() AS created_at
FROM generate_series(1,1000) g;
