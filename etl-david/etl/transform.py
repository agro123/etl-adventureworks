import datetime
from datetime import date, datetime, timedelta
from typing import Any, Tuple

import holidays
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder
from pandas import DataFrame


def generate_dim_date(start_date="2005-01-01", end_date="2025-12-31") -> pd.DataFrame:
    """
    Genera un DataFrame con todas las columnas necesarias para la tabla public.dimdate.
    Compatible con la estructura de AdventureWorksDW.
    """
    # Crear rango de fechas
    dim_date = pd.DataFrame(
        {
            "fulldatealternatekey": pd.date_range(
                start=start_date, end=end_date, freq="D"
            )
        }
    )

    # Clave surrogate en formato YYYYMMDD
    dim_date["datekey"] = (
        dim_date["fulldatealternatekey"].dt.strftime("%Y%m%d").astype(int)
    )

    # Día de la semana (1=Lunes, 7=Domingo)
    dim_date["daynumberofweek"] = dim_date["fulldatealternatekey"].dt.weekday + 1
    dim_date["englishdaynameofweek"] = dim_date["fulldatealternatekey"].dt.day_name()

    try:
        dim_date["spanishdaynameofweek"] = dim_date["fulldatealternatekey"].dt.day_name(
            locale="es_ES.UTF-8"
        )
        dim_date["frenchdaynameofweek"] = dim_date["fulldatealternatekey"].dt.day_name(
            locale="fr_FR.UTF-8"
        )
    except Exception:
        dim_date["spanishdaynameofweek"] = dim_date["englishdaynameofweek"]
        dim_date["frenchdaynameofweek"] = dim_date["englishdaynameofweek"]

    # Día del mes / año / semana ISO
    dim_date["daynumberofmonth"] = dim_date["fulldatealternatekey"].dt.day
    dim_date["daynumberofyear"] = dim_date["fulldatealternatekey"].dt.day_of_year
    dim_date["weeknumberofyear"] = (
        dim_date["fulldatealternatekey"].dt.isocalendar().week.astype(int)
    )

    # Mes y nombres de mes
    dim_date["monthnumberofyear"] = dim_date["fulldatealternatekey"].dt.month
    dim_date["englishmonthname"] = dim_date["fulldatealternatekey"].dt.month_name()

    try:
        dim_date["spanishmonthname"] = dim_date["fulldatealternatekey"].dt.month_name(
            locale="es_ES.UTF-8"
        )
        dim_date["frenchmonthname"] = dim_date["fulldatealternatekey"].dt.month_name(
            locale="fr_FR.UTF-8"
        )
    except Exception:
        translator_es = GoogleTranslator(source="en", target="es")
        translator_fr = GoogleTranslator(source="en", target="fr")
        dim_date["spanishmonthname"] = dim_date["englishmonthname"].apply(
            lambda x: safe_translate(translator_es, x)
        )
        dim_date["frenchmonthname"] = dim_date["englishmonthname"].apply(
            lambda x: safe_translate(translator_fr, x)
        )

    # Trimestres, semestres y año calendario
    dim_date["calendarquarter"] = dim_date["fulldatealternatekey"].dt.quarter
    dim_date["calendaryear"] = dim_date["fulldatealternatekey"].dt.year
    dim_date["calendarsemester"] = dim_date["calendarquarter"].apply(
        lambda q: 1 if q < 3 else 2
    )

    # Fiscal = igual a calendario (puedes ajustar si tu empresa tiene año fiscal distinto)
    dim_date["fiscalquarter"] = dim_date["calendarquarter"]
    dim_date["fiscalyear"] = dim_date["calendaryear"]
    dim_date["fiscalsemester"] = dim_date["calendarsemester"]

    # Orden final de columnas según la tabla
    dim_date = dim_date[
        [
            "datekey",
            "fulldatealternatekey",
            "daynumberofweek",
            "englishdaynameofweek",
            "spanishdaynameofweek",
            "frenchdaynameofweek",
            "daynumberofmonth",
            "daynumberofyear",
            "weeknumberofyear",
            "englishmonthname",
            "spanishmonthname",
            "frenchmonthname",
            "monthnumberofyear",
            "calendarquarter",
            "calendaryear",
            "calendarsemester",
            "fiscalquarter",
            "fiscalyear",
            "fiscalsemester",
        ]
    ]

    return dim_date


def transform_currency(df_currency: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de moneda al formato DimCurrency."""
    print("Transformando DimCurrency...")
    dim_currency = df_currency.rename(
        columns={"currency_bk": "currencyalternatekey", "currency_name": "currencyname"}
    )
    dim_currency.drop("modifieddate", axis=1, inplace=True)
    print("DimCurrency transformado.")
    return dim_currency


def transform_organization(
    df_organization: pd.DataFrame,
    df_currency: pd.DataFrame,
    df_region_currency: pd.DataFrame,
):
    parent_orgs = df_organization.merge(
        df_region_currency[["countryregioncode", "currency_bk"]],
        on="countryregioncode",
        how="left",
    )

    # parent_orgs = parent_orgs.merge(
    #     df_currency[["currency_bk", "currencykey"]], on="currency_bk", how="left"
    # )

    # we make the groupnames according to the organization
    # parent_orgs = parent_orgs.to_frame()
    parent_orgs = df_organization.rename(
        columns={"name": "organizationName", "group": "ParentGroup"}
    )
    parent_orgs["name"] = parent_orgs["organizationName"] + " Division"

    # Step 2: Assign surrogate keys
    parent_orgs["OrganizationKey"] = range(1, len(parent_orgs) + 1)
    parent_orgs["ParentOrganizationKey"] = None

    # Step 3: Create child organizations from territory names
    child_orgs = df_organization.rename(columns={"name": "organizationName"})

    # Map child to parent
    child_orgs["ParentOrganizationKey"] = child_orgs["OrganizationName"].map(
        parent_orgs.set_index("organizationName")["OrganizationKey"]
    )

    # Reassign Child Keys after parent keys
    start_key = parent_orgs["OrganizationKey"].max() + 1
    child_orgs["OrganizationKey"] = range(start_key, start_key + len(child_orgs))

    parent_orgs["percentageofownership"] = np.random.random(size=len(parent_orgs))

    # Step 4: Cleanup final structure
    parent_orgs["ParentGroup"] = None
    child_orgs = child_orgs[
        ["OrganizationKey", "ParentOrganizationKey", "OrganizationName"]
    ]

    parent_orgs = parent_orgs[
        [
            "organizationkey",
            "parentorganizationkey",
            "percentageofownership",
            "organizationName",
            "currencykey",
        ]
    ]

    dim_organization = pd.concat([parent_orgs, child_orgs], ignore_index=True)

    return dim_organization


def transform_dim_department(df_department):
    # Copy original
    df_dim = df_department.copy()

    # Add synthetic parent
    corporate_row = pd.DataFrame({"departmentname": ["Corporate"]})
    df_dim = pd.concat([corporate_row, df_dim], ignore_index=True)

    # Add surrogate key
    df_dim["departmentkey"] = range(1, len(df_dim) + 1)

    # Get corporate key
    corporate_key = df_dim.loc[
        df_dim["departmentname"] == "Corporate", "departmentkey"
    ].iloc[0]

    # Assign parents
    df_dim["parentdepartmentkey"] = corporate_key
    df_dim.loc[df_dim["departmentname"] == "Corporate", "parentdepartmentkey"] = None

    return df_dim


def generate_dim_scenario() -> pd.DataFrame:
    data = [(1, "Actual"), (2, "Budget"), (3, "Forecast")]
    columns = ["scenariokey", "scenarioname"]

    df_scenario = pd.DataFrame(data, columns=columns)

    return df_scenario


def generate_dim_account() -> pd.DataFrame:
    """
    Extract synthetic DimAccount dimension.
    This mimics an extract stage for a conformed dimension
    that does not exist in the OLTP AdventureWorks database.
    """

    data = [
        (1, None, "1000", "Cash", "Asset", "Actual", "Current Assets"),
        (2, 1, "1010", "Checking Account", "Asset", "Actual", "Current Assets"),
        (3, 1, "1020", "Savings Account", "Asset", "Actual", "Current Assets"),
        (4, None, "1100", "Accounts Receivable", "Asset", "Actual", "Current Assets"),
        (5, 4, "1110", "Trade Receivables", "Asset", "Actual", "Current Assets"),
        (
            6,
            None,
            "2000",
            "Accounts Payable",
            "Liability",
            "Actual",
            "Current Liabilities",
        ),
        (7, 6, "2010", "Vendor Payables", "Liability", "Actual", "Current Liabilities"),
        (8, None, "3000", "Operating Expenses", "Expense", "Actual", "Expenses"),
        (9, 8, "3100", "Salaries Expense", "Expense", "Actual", "Expenses"),
        (10, 8, "3200", "Rent Expense", "Expense", "Actual", "Expenses"),
        (11, None, "4000", "Sales Revenue", "Revenue", "Actual", "Revenue"),
        (12, 11, "4100", "Online Sales Revenue", "Revenue", "Actual", "Revenue"),
    ]

    columns = [
        "AccountKey",
        "ParentAccountKey",
        "AccountAlternateKey",
        "AccountDescription",
        "AccountType",
        "ValueType",
        "AccountGroup",
    ]

    df_account = pd.DataFrame(data, columns=columns)

    return df_account
