
  
    

        create or replace transient table BOOKSHOP.STAGGING.stg_category
         as
        (

SELECT
    ID,
--     CODE,
    INTITULE,
    CREATED_AT
FROM BOOKSHOP.RAW.CATEGORY
        );
      
  