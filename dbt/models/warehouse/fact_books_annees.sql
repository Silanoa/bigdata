{{
    config(
        materialized='table',
        schema='WAREHOUSE'
    )
}}

SELECT
--     b.code AS book_code,
    b.intitule AS book_title,
    v.annees,
    COUNT(*) AS nombre_ventes,
    SUM(v.qte) AS quantite_totale,
    SUM(v.pu * v.qte) AS montant_total
FROM {{ ref('fact_ventes') }} v
JOIN {{ ref('dim_books') }} b ON v.livre_id = b.id
GROUP BY b.code, b.intitule, v.annees
