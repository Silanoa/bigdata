
  
    

        create or replace transient table BOOKSHOP.STAGING_STAGGING.stg_customers
         as
        (

SELECT
    ID,
    CODE,
    FIRST_NAME,
    LAST_NAME,
--     EMAIL,
    CREATED_AT
FROM BOOKSHOP.RAW.CUSTOMERS
        );
      
  