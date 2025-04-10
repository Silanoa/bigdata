{{
    config(
        materialized='table'
    )
}}

SELECT
    ID,
--     CODE,
    INTITULE,
    CREATED_AT
FROM {{ source('raw', 'CATEGORY') }}