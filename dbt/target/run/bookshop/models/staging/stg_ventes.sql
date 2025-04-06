
  create or replace   view BOOKSHOP.STAGING_staging.stg_ventes
  
   as (
    

SELECT
    ID::INTEGER as vente_id,
    CODE::VARCHAR(50) as reference,
    FACTURES_ID::INTEGER as facture_id,
    BOOKS_ID::INTEGER as livre_id,
    QTE::INTEGER as quantite,
    PU::DECIMAL(10,2) as prix_unitaire,
    TO_DATE(DATE_EDIT, 'YYYYMMDD')::DATE as date_vente,
    CREATED_AT::TIMESTAMP as created_at
FROM BOOKSHOP.RAW.VENTES
  );

