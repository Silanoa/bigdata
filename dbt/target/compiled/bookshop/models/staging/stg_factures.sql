

SELECT
    ID::INTEGER as facture_id,
    CODE::VARCHAR(50) as reference,
    CUSTOMERS_ID::INTEGER as client_id,
    QTE_TOTALE::DECIMAL(10,2) as quantite_totale,
    TOTAL_AMOUNT::DECIMAL(12,2) as montant_ht,
    TOTAL_PAID::DECIMAL(12,2) as montant_ttc,
    TO_DATE(DATE_EDIT, 'YYYYMMDD')::DATE as date_facturation,
    CREATED_AT::TIMESTAMP as created_at
FROM BOOKSHOP.RAW.FACTURES