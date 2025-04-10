
  
    

        create or replace transient table BOOKSHOP.WAREHOUSE.dim_category
         as
        (

SELECT
    id,
    intitule,
    created_at
FROM BOOKSHOP.STAGGING.stg_category
        );
      
  