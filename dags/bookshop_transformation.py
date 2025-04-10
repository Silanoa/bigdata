from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bookshop_transformation',
    default_args=default_args,
    description='Transformations des données Bookshop avec DBT',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 3, 11),
    catchup=False,
    tags=['bookshop', 'dbt'],
) as dag:

    # Staging transformations
    dbt_staging = BashOperator(
        task_id='dbt_staging',
        bash_command='cd /opt/airflow/dbt && mkdir -p /tmp/dbt_target && dbt run --models staging --no-partial-parse --target-path /tmp/dbt_target'
    )

    # Warehouse transformations
    dbt_warehouse = BashOperator(
        task_id='dbt_warehouse',
        bash_command='cd /opt/airflow/dbt && mkdir -p /tmp/dbt_target && dbt run --models warehouse --no-partial-parse --target-path /tmp/dbt_target',
    )

    # Marts transformations
    dbt_marts = BashOperator(
        task_id='dbt_marts',
        bash_command='cd /opt/airflow/dbt && mkdir -p /tmp/dbt_target && dbt run --models marts --no-partial-parse --target-path /tmp/dbt_target',
    )

    # Set dependencies
    dbt_staging >> dbt_warehouse >> dbt_marts 