import pandas as pd
import datetime
from datetime import date
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
import yaml

from utils import check_db_connection, has_new_fact_data, save_dataframe_to_csv
from extract import (
    extract_product,
    extract_product_subcategory,
    extract_product_category,
    extract_customer,
    extract_promotion,
    extract_currency,
    extract_salesterritory,
    extract_geography,
    extract_fact_internet_sales,
    extract_salesreason,
    extract_fact_internet_sales_reason
)
from transform import (
    transform_product_category,
    transform_product_subcategory,
    transform_product,
    transform_currency,
    transform_promotion,
    transform_sales_territory,
    transform_geography,
    transform_customer,
    transform_fact_internet_sales,
    transform_salesreason,
    transform_fact_internet_sales_reason,
    generate_dim_date
)
from load import load_table
import psycopg2

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

import sys

with open('../config.yml', 'r') as f:
    config = yaml.safe_load(f)
    config_co = config['CO_SA']
    config_olap = config['ETL_PRO']

# Construct the database URL
url_oltp = (f"{config_co['drivername']}://{config_co['user']}:{config_co['password']}@{config_co['host']}:"
          f"{config_co['port']}/{config_co['dbname']}")
url_olap = (f"{config_olap['drivername']}://{config_olap['user']}:{config_olap['password']}@{config_olap['host']}:"
           f"{config_olap['port']}/{config_olap['dbname']}")
# Create the SQLAlchemy Engine
oltp_conn = create_engine(url_oltp)
olap_conn = create_engine(url_olap)

#-----------------------
# Verify ETL DB connection before inspecting tables
if not check_db_connection(olap_conn, "OLAP") or not check_db_connection(oltp_conn, "OLTP"):
    print("Unable to connect to ETL database. Exiting.")
    sys.exit(1)
#-----------------------

""" inspector = inspect(olap_conn)
tnames = inspector.get_table_names() """
#DATE DIMENSION START ==============================
# Generar la dimensión de fecha
dim_date = generate_dim_date()
# Load dimDate
load_table(
    dim_date,
    olap_conn,
    "dimdate",
    key_columns=["datekey"],
)
#DATE DIMENSION END ==============================


# FACT INTERNET SALES ETL PROCESS ============================== START
print('Iniciando proceso ETL para FactInternetSales...')
# Verificar si hay nuevos datos y en ese caso iniciar la extracción
if has_new_fact_data(conne=olap_conn, fact_table="factinternetsales"):
    print('Se detectaron datos nuevos en el origen. Iniciando extracción...')

    if config['LOAD_DIMENSIONS']:
        print('Extrayendo dimensiones para FactInternetSales...')
        # Extract para DimProductCategory
        dim_product_category = extract_product_category(oltp_conn)
        # Extract para DimProductSubcategory
        dim_product_subcategory = extract_product_subcategory(oltp_conn)
        # Extract para DimProduct
        dim_product = extract_product(oltp_conn)
        # Extract para DimSalesTerritory
        dim_sales_territory = extract_salesterritory(oltp_conn)
        # Extract para DimGeography
        dim_geography = extract_geography(oltp_conn)
        # Extract para DimCustomer
        dim_customer = extract_customer(oltp_conn)
        # Extract para DimPromotion
        dim_promotion = extract_promotion(oltp_conn)
        # Extract para DimCurrency
        dim_currency = extract_currency(oltp_conn)

        print('Transformando dimensiones para FactInternetSales...')
        # Transform para dimProductCategory
        dim_product_category = transform_product_category(dim_product_category)
        # Transform para dimProductSubcategory
        dim_product_subcategory = transform_product_subcategory(dim_product_subcategory)
        # Transform para dimProduct
        dim_product = transform_product(dim_product)
        # Transform para dimSalesTerritory
        dim_sales_territory = transform_sales_territory(dim_sales_territory)
        # Transform para dimGeography
        dim_geography = transform_geography(dim_geography)
        # Transform para dimCustomer
        dim_customer = transform_customer(dim_customer)
        # Transform para dimPromotion
        dim_promotion = transform_promotion(dim_promotion)
        # Transform para dimCurrency
        dim_currency = transform_currency(dim_currency)

        print('Cargando dimensiones para FactInternetSales...')
        # Load dimProductCategory
        load_table(
            dim_product_category,
            olap_conn,
            "dimproductcategory",
            key_columns=["productcategoryalternatekey"],
        )
        # Load dimProductSubcategory
        load_table(
            dim_product_subcategory,
            olap_conn,
            "dimproductsubcategory",
            key_columns=["productsubcategoryalternatekey"],
        )
        # Load dimProduct
        load_table(
            dim_product,
            olap_conn,
            "dimproduct",
            key_columns=["productalternatekey"],
        )
        # Load dimSalesTerritory
        load_table(
            dim_sales_territory,
            olap_conn,
            "dimsalesterritory",
            key_columns=["salesterritoryalternatekey"],
        )
        # Load dimGeography
        load_table(
            dim_geography,
            olap_conn,
            "dimgeography",
            key_columns=["city", "postalcode"],
        )
        # Load dimCustomer
        load_table(
            dim_customer,
            olap_conn,
            "dimcustomer",
            key_columns=["customeralternatekey"],
        )
        # Load dimPromotion
        load_table(
            dim_promotion,
            olap_conn,
            "dimpromotion",
            key_columns=["promotionalternatekey"],
        )
        # Load dimCurrency
        load_table(
            dim_currency,
            olap_conn,
            "dimcurrency",
            key_columns=["currencyalternatekey"],
        )
        print('Fin carga de dimensiones para FactInternetSales...')

    print('Extrayendo información para hecho FactInternetSales...')
    fact_internet_sales = extract_fact_internet_sales(oltp_conn)
    print('Transformando información para hecho FactInternetSales...')
    fact_internet_sales = transform_fact_internet_sales(fact_internet_sales, olap_conn)
    print('Cargando hecho FactInternetSales...')
    #save_dataframe_to_csv(fact_internet_sales, 'fact_internet_sales.csv')
    load_table(
        fact_internet_sales,
        olap_conn,
        "factinternetsales",
        key_columns=["salesordernumber", "salesorderlinenumber"],
    )
else:
    print('No hay datos nuevos. Proceso finalizado.')
print('Finalizando proceso ETL para FactInternetSales...')
# FACT INTERNET SALES ETL PROCESS ============================== END 

# FACT INTERNET SALES REASONS ETL PROCESS ============================== START
print('Iniciando proceso ETL para FactInternetSalesReason...')
if has_new_fact_data(conne=olap_conn, fact_table="factinternetsales"):
    print('Se detectaron datos nuevos en el origen. Iniciando extracción...')

    if config['LOAD_DIMENSIONS']:
        print('Extrayendo dimensiones para FactInternetSalesReason...')
        # Extract para DimSalesReason
        dim_sales_reason = extract_salesreason(oltp_conn)

        print('Transformando dimensiones para FactInternetSalesReason...')
        # Transform para dimSalesReason
        dim_sales_reason = transform_salesreason(dim_sales_reason)

        print('Cargando dimensiones para FactInternetSalesReason...')
        # Load dimSalesReason
        load_table(
            dim_sales_reason,
            olap_conn,
            "dimsalesreason",
            key_columns=["salesreasonalternatekey"],
        )
        print('Fin carga de dimensiones para FactInternetSalesReason...')

    print('Extrayendo información para hecho FactInternetSalesReason...')
    fact_internet_sales_reason = extract_fact_internet_sales_reason(oltp_conn)
    print('Transformando información para hecho FactInternetSalesReason...')
    fact_internet_sales_reason = transform_fact_internet_sales_reason(fact_internet_sales_reason, olap_conn)
    print('Cargando hecho FactInternetSalesReason...')
    load_table(
        fact_internet_sales_reason,
        olap_conn,
        "factinternetsalesreason",
        key_columns=["salesordernumber", "salesorderlinenumber", "salesreasonkey"],
    )
else:
    print('No hay datos nuevos. Proceso finalizado.')
print('Finalizando proceso ETL para FactInternetSalesReason...')
# FACT INTERNET SALES REASONS ETL PROCESS ============================== END 