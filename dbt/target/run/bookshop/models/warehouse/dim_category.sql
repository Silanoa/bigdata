
  
    

        create or replace transient table BOOKSHOP.STAGING_WAREHOUSE.dim_category
         as
        (

SELECT
    id,
    intitule,
    created_at
FROM BOOKSHOP.STAGING_STAGGING.stg_category
        );
      
  