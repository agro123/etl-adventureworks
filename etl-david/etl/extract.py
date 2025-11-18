from datetime import datetime

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.sql import schema


def extract(tables: list, conection: Engine) -> pd.DataFrame:
    """
    :param conection: the conectionnection to the database
    :param tables: the tables to extract
    :return: a list of tables in df format
    """
    a = []
    for i in tables:
        aux = pd.read_sql_table(i, conection)
        a.append(aux)
    return a


# names of the department groups without repetition
def extract_department(conection: Engine):
    group_name = pd.read_sql_query(
        "select distinct groupname from humanresources.department", conection
    )
    return group_name


# Only the name of the regions is extracted from the sales territories
def extract_territories(conection: Engine) -> pd.DataFrame:
    df_territories = pd.read_sql_query(
        'SELECT DISTINCT "group", name, countryregioncode FROM sales.salesterritory',
        conection,
    )
    return df_territories


def extract_region_currency(conection: Engine):
    df_region_currency = pd.read_sql_query(
        "select countryregioncode, currencycode as currency_bk from sales.countryregioncurrency",
        conection,
    )
    return df_region_currency


def extract_currency(
    source_engine: Engine, fecha: datetime | None = None
) -> pd.DataFrame:
    """
    Extrae monedas desde sales.currency.
    Si se pasa una fecha, filtra las modificadas desde esa fecha hasta hoy.
    """
    q_base = """
        SELECT
            currencycode AS currency_bk,
            name AS currency_name,
            modifieddate
        FROM sales.currency
    """
    if fecha:
        q_base += " WHERE modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(
                text(q_base), conn, params={"fecha": fecha} if fecha else None
            )
    except Exception as e:
        print(f"Error en extract_currency: {e}")
        return pd.DataFrame()
