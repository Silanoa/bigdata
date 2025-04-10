
  
    

        create or replace transient table BOOKSHOP.WAREHOUSE.dim_books
         as
        (

SELECT
    id,
    category_id,
    code,
    intitule,
    isbn_10,
    isbn_13,
    created_at
FROM BOOKSHOP.STAGGING.stg_books
        );
      
  