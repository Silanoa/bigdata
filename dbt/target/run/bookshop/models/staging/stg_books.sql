
  
    

        create or replace transient table BOOKSHOP.STAGGING.stg_books
         as
        (

SELECT
    ID,
    CODE,
    INTITULE,
    ISBN_10,
    ISBN_13,
    CATEGORY_ID,
    CREATED_AT
FROM BOOKSHOP.RAW.BOOKS
        );
      
  