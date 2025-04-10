{{
    config(
        materialized='table'
    )
}}

SELECT
    id,
    code,
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) as nom,
    created_at
FROM {{ ref('stg_customers') }}