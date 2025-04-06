

SELECT
--     b.id as book_id,
    b.code AS book_code,
    b.intitule AS book_title,
    v.annees,
    v.mois,
    v.jour,
    COUNT(*) AS nombre_ventes,
    SUM(v.qte) AS quantite_totale,
    SUM(v.pu * v.qte) AS montant_total
FROM BOOKSHOP.STAGING_WAREHOUSE.fact_ventes v
JOIN BOOKSHOP.STAGING_WAREHOUSE.dim_books b ON v.livre_id = b.id
GROUP BY b.id, b.code, b.intitule, v.annees, v.mois, v.jour