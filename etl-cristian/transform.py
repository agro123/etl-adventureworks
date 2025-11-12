import pandas as pd
from datetime import date
import numpy as np
import holidays
from deep_translator import GoogleTranslator

from utils import parse_demographics

# Función auxiliar para traducir de forma segura
def safe_translate(translator, text):
        try:
            return translator.translate(text)
        except Exception:
            return text 

def transform_product_category(df_category: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de categorías de producto al formato DimProductCategory."""
    print("Transformando DimProductCategory...")
    # Renombrar columnas al formato estándar
    dim_product_category = df_category.rename(columns={
        "productcategory_bk": "productcategoryalternatekey",
        "productcategory_name": "englishproductcategoryname"
    })

    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')

    # Aplicar traducciones
    dim_product_category["spanishproductcategoryname"] = dim_product_category['englishproductcategoryname'].apply(lambda x: safe_translate(translator_es, x))
    dim_product_category["frenchproductcategoryname"] = dim_product_category['englishproductcategoryname'].apply(lambda x: safe_translate(translator_fr, x))

    if "modifieddate" in dim_product_category.columns:
        dim_product_category.drop("modifieddate", axis=1, inplace=True)
    print("DimProductCategory transformado.")
    return dim_product_category

def transform_product_subcategory(df_subcat: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de subcategorías al formato DimProductSubCategory."""
    print("Transformando DimProductSubCategory...")
    dim_product_subcat = df_subcat.rename(columns={
        "productsubcategory_bk": "productsubcategoryalternatekey",
        "productsubcategory_name": "englishproductsubcategoryname",
        "productcategory_bk": "productcategorykey"
    })
    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')

    # Aplicar traducciones
    dim_product_subcat["spanishproductsubcategoryname"] = dim_product_subcat['englishproductsubcategoryname'].apply(lambda x: safe_translate(translator_es, x))
    dim_product_subcat["frenchproductsubcategoryname"] = dim_product_subcat['englishproductsubcategoryname'].apply(lambda x: safe_translate(translator_fr, x))

    if "modifieddate" in dim_product_subcat.columns:
        dim_product_subcat.drop("modifieddate", axis=1, inplace=True)
    print("DimProductSubCategory transformado.")
    return dim_product_subcat

def transform_product(df_product: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de productos al formato DimProduct."""
    print("Transformando DimProduct...")
    dim_product = df_product.rename(columns={
        "productnumber": "productalternatekey",
        "product_name": "englishproductname",
        "productsubcategory_bk": "productsubcategorykey",
        "sellstartdate": "startdate",#Es la fecha de inicio de venta, pero algunos datos no concuerdan en el origen y otros tienen un día de mas.
        "sellenddate": "enddate",# Es la fecha de final de venta, pero algunos datos no concuerdan en el origen y otros tienen un día de mas.
    })
    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')
     # Aplicar traducciones
    dim_product["spanishproductname"] = dim_product['englishproductname'].apply(lambda x: safe_translate(translator_es, x))
    dim_product["frenchproductname"] = dim_product['englishproductname'].apply(lambda x: safe_translate(translator_fr, x))
    dim_product["sizerange"] = 'NA' #investigar, No se define los rangos en el origen,  no hay documentación al respecto, buscar en la olap de ejemplo agrupando por esta columna. 
    dim_product["modelname"] = 'NA' #No hay datos en el origen.
    dim_product["largephoto"] = 'NA' # hay una columna en production.productphoto con un nombre similar  se obtiene de ahi. pero quizas no es necesario.

    dim_product["status"] = np.where(
    dim_product["enddate"].isna() | (dim_product["enddate"] == ""), 
        "Current", 
        "Discontinued"
    ) #cuando existe una fecha de sellenddate el valor es "null: y cuando no "Current".

    dim_product.drop("product_bk", axis=1, inplace=True)
    print("DimProduct transformado.")
    return dim_product

def transform_currency(df_currency: pd.DataFrame) -> pd.DataFrame:
    """Transforma los datos de moneda al formato DimCurrency."""
    print("Transformando DimCurrency...")
    dim_currency = df_currency.rename(columns={
        "currency_bk": "currencyalternatekey",
        "currency_name": "currencyname"
    })
    dim_currency.drop("modifieddate", axis=1, inplace=True)
    print("DimCurrency transformado.")
    return dim_currency

def transform_promotion(df_promo: pd.DataFrame) -> pd.DataFrame:
    """Transforma las promociones al formato DimPromotion."""
    print("Transformando DimPromotion...")
    dim_promo = df_promo.rename(columns={
        "promotion_bk": "promotionalternatekey",
        "description": "englishpromotionname",
        "discountpct": "discountpct",
        "type": "englishpromotiontype",
        "category": "englishpromotioncategory",
    })

    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')

    dim_promo["spanishpromotionname"] = dim_promo['englishpromotionname'].apply(lambda x: safe_translate(translator_es, x))
    dim_promo["frenchpromotionname"] = dim_promo['englishpromotionname'].apply(lambda x: safe_translate(translator_fr, x))
    dim_promo["spanishpromotiontype"] = dim_promo["englishpromotiontype"].apply(lambda x: safe_translate(translator_es, x))
    dim_promo["frenchpromotiontype"] = dim_promo["englishpromotiontype"].apply(lambda x: safe_translate(translator_fr, x))
    dim_promo["spanishpromotioncategory"] = dim_promo["englishpromotioncategory"].apply(lambda x: safe_translate(translator_es, x))
    dim_promo["frenchpromotioncategory"] = dim_promo["englishpromotioncategory"].apply(lambda x: safe_translate(translator_fr, x))
    dim_promo.drop("modifieddate", axis=1, inplace=True)

    print("DimPromotion transformado.")
    return dim_promo

def transform_sales_territory(df_territory: pd.DataFrame) -> pd.DataFrame:
    """Transforma territorios al formato DimSalesTerritory."""
    print("Transformando DimSalesTerritory...")
    dim_territory = df_territory.rename(columns={
        "salesterritory_bk": "salesterritoryalternatekey",
        "salesterritory_name": "salesterritoryregion",
        "countryregioncode": "salesterritorycountry",
        "salesterritory_group": "salesterritorygroup"
    })
    dim_territory.drop("modifieddate", axis=1, inplace=True)

    print("DimSalesTerritory transformado.")
    return dim_territory

def transform_geography(df_geo: pd.DataFrame) -> pd.DataFrame:
    """Transforma datos geográficos al formato DimGeography."""
    print("Transformando DimGeography...")
    dim_geo = df_geo.rename(columns={
        "city": "city",
        "stateprovincecode": "stateprovincecode",
        "stateprovincename": "stateprovincename",
        "countryregioncode": "countryregioncode",
        "englishcountryregionname": "englishcountryregionname",
        "postalcode": "postalcode",
        "salesterritory_bk": "salesterritorykey",
        "ipaddresslocator": "ipaddresslocator"
    })
    # Agregamos columnas para los nombres multilingües que DimGeography requiere
    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')
    dim_geo["spanishcountryregionname"] = dim_geo["englishcountryregionname"].apply(lambda x: safe_translate(translator_es, x))
    dim_geo["frenchcountryregionname"] = dim_geo["englishcountryregionname"].apply(lambda x: safe_translate(translator_fr, x))
    dim_geo["ipaddresslocator"] = 'NA'  # Investigar su origen, por ahora lo dejamos vacío
    dim_geo.drop("modifieddate", axis=1, inplace=True)
    print("DimGeography transformado.")
    return dim_geo

def transform_customer(df_customer: pd.DataFrame) -> pd.DataFrame:
    """Transforma datos de clientes al formato DimCustomer."""
    print("Transformando DimCustomer...")
    if df_customer.empty:
        return df_customer

    # Parsear XML demographics en nuevas columnas
    demo_data = df_customer["demographics"].apply(lambda x: parse_demographics(x) if pd.notna(x) else {})
    demo_df = pd.DataFrame(list(demo_data))
    dim_customer = pd.concat([df_customer.reset_index(drop=True), demo_df], axis=1)

    # Todos las filas que  tengan los campos de demographics nulos se eliminan
    dim_customer.dropna(subset=["birthdate", "maritalstatus","yearlyincome","totalchildren","numberchildrenathome"], inplace=True)

    # Para el yearlyincome viene un rango de valores en formato string, se toma el valor medio del rango [0-25000, 25001-50000, 50001-75000, 75001-100000, greater than 100000] para la última categoria se coloca 130000.
    def parse_income(value):
        if pd.isna(value):
            return None
        value = value.strip().lower()
        if value.startswith("greater than"):
            return 130000
        elif "-" in value:
            parts = value.replace("$", "").replace(",", "").split("-")
            try:
                low, high = int(parts[0]), int(parts[1])
                return (low + high) / 2
            except:
                return None
        else:
            return None

    dim_customer["yearlyincome"] = dim_customer["yearlyincome"].apply(parse_income)


    # Renombrar campos para alinearlos con DimCustomer
    dim_customer = dim_customer.rename(columns={
        "accountnumber": "customeralternatekey",
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
    
    translator_es = GoogleTranslator(source='en', target='es')
    translator_fr = GoogleTranslator(source='en', target='fr')
    # Campos multilingües y nulos faltantes
    dim_customer["spanisheducation"] = dim_customer["englisheducation"].apply(lambda x: safe_translate(translator_es, x))
    dim_customer["frencheducation"] = dim_customer["englisheducation"].apply(lambda x: safe_translate(translator_fr, x))
    dim_customer["spanishoccupation"] = dim_customer["englishoccupation"].apply(lambda x: safe_translate(translator_es, x))
    dim_customer["frenchoccupation"] = dim_customer["englishoccupation"].apply(lambda x: safe_translate(translator_fr, x))
    dim_customer.drop(["demographics", "englisheducation", "englishoccupation", "modifieddate"], axis=1, inplace=True)

    dim_customer.drop(["accountNumber", "person_bk", "person_type", "email_promotion", "additionalcontactinfo","demographics", "emailpromotion", "modifieddate","city", "postalcode",""], axis=1, inplace=True)

    # Limpieza final
    dim_customer = dim_customer.replace({np.nan: None})
    print("DimCustomer transformado.")
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