
  
    

        create or replace transient table BOOKSHOP.WAREHOUSE.fact_books_mois
         as
        (

SELECT
    b.id as book_id,
    b.code AS book_code,
    b.intitule AS book_title,
    v.annees,
    v.mois,
    COUNT(*) AS nombre_ventes,
    SUM(v.qte) AS quantite_totale,
    SUM(v.pu * v.qte) AS montant_total
FROM BOOKSHOP.WAREHOUSE.fact_ventes v
JOIN BOOKSHOP.WAREHOUSE.dim_books b ON v.livre_id = b.id
GROUP BY b.code, book_id, b.intitule, v.annees, v.mois
        );
      
  