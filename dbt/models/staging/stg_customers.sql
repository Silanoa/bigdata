{{
    config(
        materialized='table'
    )
}}

SELECT
    ID,
    CODE,
    FIRST_NAME,
    LAST_NAME,
--     EMAIL,
    CREATED_AT
FROM {{ source('raw', 'CUSTOMERS') }}