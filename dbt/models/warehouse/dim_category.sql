{{
    config(
        materialized='table'
    )
}}

SELECT
    id,
    intitule,
    created_at
FROM {{ ref('stg_category') }}