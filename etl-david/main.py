import datetime
from datetime import date

import pandas as pd
import psycopg2
import yaml
from etl import extract, load, transform, utils_etl
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 100)

# Opening the config file
with open("config_fill.yml", "r") as f:
    config = yaml.safe_load(f)
    config_adventure = config["ADVENTURE_DB"]
    config_etl = config["ADVENTURE_DW"]

# Construct the database URL
url_database = (
    f"{config_adventure['drivername']}://{config_adventure['user']}:{config_adventure['password']}@{config_adventure['host']}:"
    f"{config_adventure['port']}/{config_adventure['dbname']}"
)

url_etl = (
    f"{config_etl['drivername']}://{config_etl['user']}:{config_etl['password']}@{config_etl['host']}:"
    f"{config_etl['port']}/{config_etl['dbname']}"
)

# Create the SQLAlchemy engine
database_connect = create_engine(url_database)
etl_connect = create_engine(url_etl)

inspector = inspect(etl_connect)
tnames = inspector.get_table_names()

if not tnames:
    conn = psycopg2.connect(
        dbname=config_etl["dbname"],
        user=config_etl["user"],
        password=config_etl["password"],
        host=config_etl["host"],
        port=config_etl["port"],
    )
    cur = conn.cursor()
    with open("sqlScripts.yml", "r") as f:
        sql = yaml.safe_load(f)
        for key, val in sql.items():
            cur.execute(val)
            conn.commit()

    # Reading data

if config["LOAD_DIMENSIONS"]:
    dim_department_group = extract.extract_department(database_connect)
    dim_organization = extract.extract_territories(database_connect)
    dim_currency = extract.extract_currency(database_connect)
    dim_region_currency = extract.extract_region_currency(database_connect)

    # Transform
    dim_department_group = transform.transform_dim_department(dim_department_group)
    dim_organization = transform.transform_organization(
        dim_organization, dim_currency, dim_region_currency
    )
    dim_date = transform.generate_dim_date()
    dim_currency = transform.transform_currency(dim_currency)
    dim_scenario = transform.generate_dim_scenario()
    dim_account = transform.generate_dim_account()

    # load tables
    # Load dimDate
    load.load_table(
        dim_date,
        etl_connect,
        "dimdate",
        key_columns=["datekey"],
    )

    load.load_table(
        dim_scenario,
        etl_connect,
        "dimscenario",
        key_columns=["scenariokey"],
    )

    load.load_table(
        dim_department_group,
        etl_connect,
        "dimdepartmentgroup",
        key_columns=["departmentgroupkey"],
    )

    load.load_table(
        dim_organization,
        etl_connect,
        "dimorganization",
        key_columns=["datekey"],
    )

    load.load_table(
        dim_currency,
        etl_connect,
        "dimcurrency",
        key_columns=["currencyalternatekey"],
    )

    load.load_table(
        dim_account,
        etl_connect,
        "dimaccount",
        key_columns=["accountalternateKey"],
    )
