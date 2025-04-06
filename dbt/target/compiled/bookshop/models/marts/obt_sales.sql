

WITH ventes AS (
    SELECT * FROM BOOKSHOP.STAGING_WAREHOUSE.fact_ventes
),
factures AS (
    SELECT * FROM BOOKSHOP.STAGING_WAREHOUSE.fact_factures
),
category AS (
    SELECT * FROM BOOKSHOP.STAGING_WAREHOUSE.dim_category
),
books AS (
    SELECT * FROM BOOKSHOP.STAGING_WAREHOUSE.dim_books
),
customers AS (
    SELECT * FROM BOOKSHOP.STAGING_WAREHOUSE.dim_customers
)

SELECT
    v.id,
    v.annees,
    v.mois,
    v.jour,
    v.pu,
    v.qte,
    f.facture_id as facture_id,
    f.code as facture_code,
    f.qte_totale,
    f.total_amount,
    f.total_paid,
    c.intitule as category_intitule,
    b.code as book_code,
    b.intitule as book_intitule,
    b.isbn_10,
    b.isbn_13,
    cu.code as customer_code,
    cu.nom as customer_nom
FROM ventes v
JOIN factures f ON v.facture_id = f.facture_id
JOIN books b ON v.livre_id = b.id
JOIN category c ON b.category_id = c.id
JOIN customers cu ON f.client_id = cu.id