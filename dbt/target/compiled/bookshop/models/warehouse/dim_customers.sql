

SELECT
    id,
    code,
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) as nom,
    created_at
FROM BOOKSHOP.STAGING_STAGGING.stg_customers