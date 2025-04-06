{{
    config(
        materialized='table',
        schema='STAGGING'
    )
}}

SELECT
    ID,
--     CODE,
    INTITULE,
    CREATED_AT
FROM {{ source('raw', 'CATEGORY') }}