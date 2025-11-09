import pandas as pd
from datetime import date
import numpy as np
import holidays
from deep_translator import GoogleTranslator

from utils import parse_demographics

def transform_product_category(df_category: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de categorías de producto al formato DimProductCategory."""

    # Renombrar columnas al formato estándar
    dim_product_category = df_category.rename(columns={
        "productcategory_bk": "productcategoryalternatekey",
        "productcategory_name": "englishproductcategoryname"
    })

    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')

    # Función auxiliar para traducir de forma segura
    def safe_translate(translator, text):
        try:
            return translator.translate(text)
        except Exception:
            return text 

    # Aplicar traducciones
    dim_product_category["spanishproductcategoryname"] = dim_product_category['englishproductcategoryname'].apply(lambda x: safe_translate(translator_es, x))
    dim_product_category["frenchproductcategoryname"] = dim_product_category['englishproductcategoryname'].apply(lambda x: safe_translate(translator_fr, x))
    if "modifieddate" in dim_product_category.columns:
        dim_product_category.drop("modifieddate", axis=1, inplace=True)

    return dim_product_category

def transform_product_subcategory(df_subcat: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de subcategorías al formato DimProductSubCategory."""
    dim_product_subcat = df_subcat.rename(columns={
        "productsubcategory_bk": "productsubcategoryalternatekey",
        "productsubcategory_name": "englishproductsubcategoryname",
        "productcategory_bk": "productcategorykey"
    })
    dim_product_subcat["spanishproductsubcategoryname"] = dim_product_subcat["englishproductsubcategoryname"]
    dim_product_subcat["frenchproductsubcategoryname"] = dim_product_subcat["englishproductsubcategoryname"]
    dim_product_subcat["saved"] = date.today()
    return dim_product_subcat

def transform_product(df_product: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de productos al formato DimProduct."""
    dim_product = df_product.rename(columns={
        "product_bk": "productalternatekey",
        "product_name": "englishproductname",
        "productsubcategory_bk": "productsubcategorykey"
    })
    dim_product["spanishproductname"] = dim_product["englishproductname"]
    dim_product["frenchproductname"] = dim_product["englishproductname"]
    dim_product["finishedgoodsflag"] = True
    dim_product["saved"] = date.today()
    return dim_product

def transform_currency(df_currency: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de moneda al formato DimCurrency."""
    dim_currency = df_currency.rename(columns={
        "currency_bk": "currencyalternatekey",
        "currency_name": "currencyname"
    })
    dim_currency["saved"] = date.today()
    return dim_currency

def transform_promotion(df_promo: pd.DataFrame) -> pd.DataFrame:
    """Transforma las promociones al formato DimPromotion."""
    dim_promo = df_promo.rename(columns={
        "promotion_bk": "promotionalternatekey",
        "description": "englishpromotionname",
        "discountpct": "discountpct",
        "type": "englishpromotiontype",
        "category": "englishpromotioncategory",
    })
    dim_promo["spanishpromotionname"] = dim_promo["englishpromotionname"]
    dim_promo["frenchpromotionname"] = dim_promo["englishpromotionname"]
    dim_promo["spanishpromotiontype"] = dim_promo["englishpromotiontype"]
    dim_promo["frenchpromotiontype"] = dim_promo["englishpromotiontype"]
    dim_promo["spanishpromotioncategory"] = dim_promo["englishpromotioncategory"]
    dim_promo["frenchpromotioncategory"] = dim_promo["englishpromotioncategory"]
    dim_promo["saved"] = date.today()
    return dim_promo

def transform_sales_territory(df_territory: pd.DataFrame) -> pd.DataFrame:
    """Transforma territorios al formato DimSalesTerritory."""
    dim_territory = df_territory.rename(columns={
        "salesterritory_bk": "salesterritoryalternatekey",
        "salesterritory_name": "salesterritoryregion",
        "countryregioncode": "salesterritorycountry",
        "salesterritory_group": "salesterritorygroup"
    })
    dim_territory["saved"] = date.today()
    return dim_territory

def transform_geography(df_geo: pd.DataFrame) -> pd.DataFrame:
    """Transforma datos geográficos al formato DimGeography."""
    dim_geo = df_geo.rename(columns={
        "city": "city",
        "stateprovincecode": "stateprovincecode",
        "stateprovincename": "stateprovincename",
        "countryregioncode": "countryregioncode",
        "englishcountryregionname": "englishcountryregionname",
        "spanishcountryregionname": "spanishcountryregionname",
        "frenchcountryregionname": "frenchcountryregionname",
        "postalcode": "postalcode",
        "salesterritory_bk": "salesterritorykey",
        "ipaddresslocator": "ipaddresslocator"
    })
    dim_geo["saved"] = date.today()
    return dim_geo

def transform_customer(df_customer: pd.DataFrame) -> pd.DataFrame:
    if df_customer.empty:
        return df_customer

    # Parsear XML demographics en nuevas columnas
    demo_data = df_customer["demographics"].apply(lambda x: parse_demographics(x) if pd.notna(x) else {})
    demo_df = pd.DataFrame(list(demo_data))
    dim_customer = pd.concat([df_customer.reset_index(drop=True), demo_df], axis=1)

    # Renombrar campos para alinearlos con DimCustomer
    dim_customer = dim_customer.rename(columns={
        "customer_bk": "customeralternatekey",
        "firstname": "firstname",
        "middlename": "middlename",
        "lastname": "lastname",
        "title": "title",
        "namestyle": "namestyle",
        "emailaddress": "emailaddress",
        "addressline1": "addressline1",
        "addressline2": "addressline2",
        "territory_bk": "geographykey"
    })

    # Campos multilingües y nulos faltantes
    dim_customer["spanisheducation"] = dim_customer["englisheducation"]
    dim_customer["frencheducation"] = dim_customer["englisheducation"]
    dim_customer["spanishoccupation"] = dim_customer["englishoccupation"]
    dim_customer["frenchoccupation"] = dim_customer["englishoccupation"]
    dim_customer["saved"] = date.today()

    # Limpieza final
    dim_customer = dim_customer.replace({np.nan: None})
    return dim_customer

def transform_fact_internet_sales(df_fact: pd.DataFrame) -> pd.DataFrame:
    if df_fact.empty:
        print("DataFrame de ventas vacío. No hay nada para transformar.")
        return df_fact

    # Renombrar columnas según el modelo OLAP
    fact_sales = df_fact.rename(columns={
        "product_bk": "productkey",
        "customer_bk": "customerkey",
        "promotion_bk": "promotionkey",
        "currency_bk": "currencykey",
        "salesterritory_bk": "salesterritorykey",
        "salesordernumber": "salesordernumber",
        "salesorderlinenumber": "salesorderlinenumber",
        "revisionnumber": "revisionnumber",
        "orderquantity": "orderquantity",
        "unitprice": "unitprice",
        "extendedamount": "extendedamount",
        "unitpricediscountpct": "unitpricediscountpct",
        "discountamount": "discountamount",
        "productstandardcost": "productstandardcost",
        "totalproductcost": "totalproductcost",
        "salesamount": "salesamount",
        "taxamt": "taxamt",
        "freight": "freight",
        "carriertrackingnumber": "carriertrackingnumber",
        "customerponumber": "customerponumber",
        "orderdate": "orderdate",
        "duedate": "duedate",
        "shipdate": "shipdate"
    })

    num_cols = [
        "orderquantity", "unitprice", "extendedamount",
        "unitpricediscountpct", "discountamount", "productstandardcost",
        "totalproductcost", "salesamount", "taxamt", "freight"
    ]
    for col in num_cols:
        fact_sales[col] = pd.to_numeric(fact_sales[col], errors="coerce").fillna(0)

    fact_sales["revisionnumber"] = fact_sales["revisionnumber"].fillna(0).astype(int)
    fact_sales["salesorderlinenumber"] = fact_sales["salesorderlinenumber"].fillna(1).astype(int)

    def date_to_key(x):
        try:
            return int(x.strftime("%Y%m%d")) if pd.notna(x) else None
        except Exception:
            return None

    fact_sales["orderdatekey"] = fact_sales["orderdate"].apply(date_to_key)
    fact_sales["duedatekey"] = fact_sales["duedate"].apply(date_to_key)
    fact_sales["shipdatekey"] = fact_sales["shipdate"].apply(date_to_key)

    # Estas claves deben existir para mantener integridad en FactInternetSales
    fact_sales["productkey"] = fact_sales["productkey"].fillna(-1).astype(int)
    fact_sales["customerkey"] = fact_sales["customerkey"].fillna(-1).astype(int)
    fact_sales["promotionkey"] = fact_sales["promotionkey"].fillna(-1).astype(int)
    # fact_sales["currencykey"] = 0
    fact_sales["salesterritorykey"] = fact_sales["salesterritorykey"].fillna(-1).astype(int)

    fact_sales = fact_sales.dropna(subset=["orderdate", "salesordernumber"])
    fact_sales["saved"] = date.today()

    fact_sales = fact_sales.where(pd.notnull(fact_sales), None)

    return fact_sales

def transform_fact_internet_sales_reason(df_fact_reason: pd.DataFrame) -> pd.DataFrame:
    fact_reason = df_fact_reason.rename(columns={
        "salesordernumber": "salesordernumber",
        "salesorderlinenumber": "salesorderlinenumber",
        "salesreason_bk": "salesreasonkey"
    })
    fact_reason["saved"] = date.today()
    return fact_reason

def generate_dim_date(start_date='2005-01-01', end_date='2025-12-31') -> pd.DataFrame:
    """
    Genera un DataFrame con todas las columnas necesarias para la tabla public.dimdate.
    Compatible con la estructura de AdventureWorksDW.
    """
    # Crear rango de fechas
    dim_date = pd.DataFrame({"fulldatealternatekey": pd.date_range(start=start_date, end=end_date, freq='D')})
    
    # Clave surrogate en formato YYYYMMDD
    dim_date["datekey"] = dim_date["fulldatealternatekey"].dt.strftime("%Y%m%d").astype(int)
    
    # Día de la semana (1=Lunes, 7=Domingo)
    dim_date["daynumberofweek"] = dim_date["fulldatealternatekey"].dt.weekday + 1
    dim_date["englishdaynameofweek"] = dim_date["fulldatealternatekey"].dt.day_name()
    
    try:
        dim_date["spanishdaynameofweek"] = dim_date["fulldatealternatekey"].dt.day_name(locale="es_ES.UTF-8")
        dim_date["frenchdaynameofweek"] = dim_date["fulldatealternatekey"].dt.day_name(locale="fr_FR.UTF-8")
    except Exception:
        dim_date["spanishdaynameofweek"] = dim_date["englishdaynameofweek"]
        dim_date["frenchdaynameofweek"] = dim_date["englishdaynameofweek"]
    
    # Día del mes / año / semana ISO
    dim_date["daynumberofmonth"] = dim_date["fulldatealternatekey"].dt.day
    dim_date["daynumberofyear"] = dim_date["fulldatealternatekey"].dt.day_of_year
    dim_date["weeknumberofyear"] = dim_date["fulldatealternatekey"].dt.isocalendar().week.astype(int)
    
    # Mes y nombres de mes
    dim_date["monthnumberofyear"] = dim_date["fulldatealternatekey"].dt.month
    dim_date["englishmonthname"] = dim_date["fulldatealternatekey"].dt.month_name()
    
    try:
        dim_date["spanishmonthname"] = dim_date["fulldatealternatekey"].dt.month_name(locale="es_ES.UTF-8")
        dim_date["frenchmonthname"] = dim_date["fulldatealternatekey"].dt.month_name(locale="fr_FR.UTF-8")
    except Exception:
        dim_date["spanishmonthname"] = dim_date["englishmonthname"]
        dim_date["frenchmonthname"] = dim_date["englishmonthname"]
    
    # Trimestres, semestres y año calendario
    dim_date["calendarquarter"] = dim_date["fulldatealternatekey"].dt.quarter
    dim_date["calendaryear"] = dim_date["fulldatealternatekey"].dt.year
    dim_date["calendarsemester"] = dim_date["calendarquarter"].apply(lambda q: 1 if q < 3 else 2)
    
    # Fiscal = igual a calendario (puedes ajustar si tu empresa tiene año fiscal distinto)
    dim_date["fiscalquarter"] = dim_date["calendarquarter"]
    dim_date["fiscalyear"] = dim_date["calendaryear"]
    dim_date["fiscalsemester"] = dim_date["calendarsemester"]
    
    # Orden final de columnas según la tabla
    dim_date = dim_date[[
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
        "fiscalsemester"
    ]]
    
    return dim_date