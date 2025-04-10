
  
    

        create or replace transient table BOOKSHOP.WAREHOUSE.dim_customers
         as
        (

SELECT
    id,
    code,
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) as nom,
    created_at
FROM BOOKSHOP.STAGGING.stg_customers
        );
      
  