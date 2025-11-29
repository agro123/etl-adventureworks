import pandas as pd
from datetime import date
import xml.etree.ElementTree as ET
import numpy as np
import holidays
from deep_translator import GoogleTranslator
from sqlalchemy import text, Engine

from utils import parse_demographics, save_dataframe_to_csv

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
        "product_number": "productalternatekey",
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
    #dim_product["largephoto"] = 'NA' # hay una columna en production.productphoto con un nombre similar  se obtiene de ahi. pero quizas no es necesario.

    dim_product['color'] = dim_product['color'].fillna('NA')
    #dim_product['columna'] = dim_product['columna'].fillna(valor_defecto)

    dim_product["status"] = np.where(
    dim_product["enddate"].isna() | (dim_product["enddate"] == ""), 
        "Current", 
        "Discontinued"
    ) #cuando existe una fecha de sellenddate el valor es "null: y cuando no "Current".

    dim_product.drop(["product_bk", "discontinueddate"], axis=1, inplace=True)
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

    dim_promo["spanishpromotionname"] = dim_promo['englishpromotionname']#.apply(lambda x: safe_translate(translator_es, x))
    dim_promo["frenchpromotionname"] = dim_promo['englishpromotionname']#.apply(lambda x: safe_translate(translator_fr, x))
    dim_promo["spanishpromotiontype"] = dim_promo["englishpromotiontype"]#.apply(lambda x: safe_translate(translator_es, x))
    dim_promo["frenchpromotiontype"] = dim_promo["englishpromotiontype"]#.apply(lambda x: safe_translate(translator_fr, x))
    dim_promo["spanishpromotioncategory"] = dim_promo["englishpromotioncategory"]#.apply(lambda x: safe_translate(translator_es, x))
    dim_promo["frenchpromotioncategory"] = dim_promo["englishpromotioncategory"]#.apply(lambda x: safe_translate(translator_fr, x))
    dim_promo.drop("modifieddate", axis=1, inplace=True)

    print("DimPromotion transformado.")
    return dim_promo

def transform_salesreason(df_salesreason: pd.DataFrame) -> pd.DataFrame:
        """
        Transforma las razones de venta al formato de `public.dimsalesreason`.
        Espera las columnas (como devuelve `extract_salesreason`):
            - salesreason_bk
            - salesreason_name
            - salesreason_reasontype
            - modifieddate

        Devuelve un DataFrame con columnas:
            - salesreasonalternatekey
            - salesreasonname
            - salesreasonreasontype
        """
        print("Transformando DimSalesReason...")
        if df_salesreason is None or df_salesreason.empty:
                print("No hay datos en df_salesreason")
                return pd.DataFrame(columns=["salesreasonalternatekey", "salesreasonname", "salesreasonreasontype"])

        dim_salesreason = df_salesreason.rename(columns={
                "salesreason_bk": "salesreasonalternatekey",
                "salesreason_name": "salesreasonname",
                "salesreason_reasontype": "salesreasonreasontype"
        })

        dim_salesreason["salesreasonname"] = dim_salesreason["salesreasonname"].fillna("NA")
        dim_salesreason["salesreasonreasontype"] = dim_salesreason["salesreasonreasontype"].fillna("NA")

        if "modifieddate" in dim_salesreason.columns:
                dim_salesreason.drop(columns=["modifieddate"], inplace=True)

        dim_salesreason = dim_salesreason[["salesreasonalternatekey", "salesreasonname", "salesreasonreasontype"]]

        print("DimSalesReason transformado.")
        return dim_salesreason

def transform_sales_territory(df_territory: pd.DataFrame) -> pd.DataFrame:
    """Transforma territorios al formato DimSalesTerritory."""
    print("Transformando DimSalesTerritory...")
    dim_territory = df_territory.rename(columns={
        "salesterritory_bk": "salesterritoryalternatekey",
        "salesterritory_name": "salesterritoryregion",
        "countryregioncode": "salesterritorycountry",
        "salesterritory_group": "salesterritorygroup"
    })

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
    dim_geo["spanishcountryregionname"] = dim_geo["englishcountryregionname"] #.apply(lambda x: safe_translate(translator_es, x))
    dim_geo["frenchcountryregionname"] = dim_geo["englishcountryregionname"] #.apply(lambda x: safe_translate(translator_fr, x))
    dim_geo["ipaddresslocator"] = 'NA'  # Investigar su origen, por ahora lo dejamos vacío
    dim_geo.drop(["modifieddate", "address_bk"], axis=1, inplace=True)
    
    print("DimGeography transformado.")
    return dim_geo

def transform_employee(df_employee: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    """
    Transforma el extract de empleados al layout esperado por public.dimemployee.
    Realiza lookups para obtener surrogate keys (salesterritory).
    """
    print("Transformando DimEmployee...")
    if df_employee is None or df_employee.empty:
        print("No hay datos en df_employee")
        # Devolver columnas esperadas vacías
        cols = [
            "parentemployeekey",
            "parentemployeenationalidalternatekey",
            "salesterritorykey",
            "firstname",
            "lastname",
            "middlename",
            "namestyle",
            "title",
            "hiredate",
            "birthdate",
            "loginid",
            "emailaddress",
            "phone",
            "maritalstatus",
            "emergencycontactname",
            "emergencycontactphone",
            "salariedflag",
            "gender",
            "payfrequency",
            "baserate",
            "vacationhours",
            "sickleavehours",
            "currentflag",
            "salespersonflag",
            "departmentname",
            "startdate",
            "enddate",
            "status",
            "employeephoto",
            "employeenationalidalternatekey"
        ]
        return pd.DataFrame(columns=cols)

    df = df_employee.copy()

    # Lookup dim salesterritory to get surrogate key
    try:
        dim_territory = pd.read_sql("SELECT salesterritorykey, salesterritoryalternatekey FROM public.dimsalesterritory", target_engine)
    except Exception:
        dim_territory = pd.DataFrame(columns=["salesterritorykey", "salesterritoryalternatekey"])

    if "salesterritory_bk" in df.columns and not dim_territory.empty:
        df = df.merge(dim_territory, how="left", left_on="salesterritory_bk", right_on="salesterritoryalternatekey")
        df.rename(columns={"salesterritorykey": "salesterritorykey"}, inplace=True)
    else:
        df["salesterritorykey"] = None

    # Construir columnas finales
    df_out = pd.DataFrame()
    df_out["parentemployeekey"] = None
    df_out["parentemployeenationalidalternatekey"] = None
    df_out["salesterritorykey"] = df.get("salesterritorykey")
    df_out["firstname"] = df.get("firstname")
    df_out["lastname"] = df.get("lastname")
    df_out["middlename"] = df.get("middlename")
    df_out["namestyle"] = df.get("namestyle").fillna(False) if "namestyle" in df.columns else False
    df_out["title"] = df.get("title")
    df_out["hiredate"] = pd.to_datetime(df.get("hiredate"), errors="coerce")
    df_out["birthdate"] = pd.to_datetime(df.get("birthdate"), errors="coerce")
    df_out["loginid"] = df.get("loginid")
    df_out["emailaddress"] = df.get("emailaddress")
    df_out["phone"] = df.get("phone")
    df_out["maritalstatus"] = df.get("maritalstatus")
    df_out["salariedflag"] = df.get("salariedflag")
    df_out["gender"] = df.get("gender")
    df_out["currentflag"] = df.get("salariedflag").notna() if "salariedflag" in df.columns else True
    df_out["status"] = df.get("status")
    df_out["employeephoto"] = None
    df_out["employeenationalidalternatekey"] = df.get("employeenationalidalternatekey")
    df_out["emergencycontactname"] = df.get("emergencycontactname")
    df_out["emergencycontactphone"] = df.get("emergencycontactphone")
    df_out["payfrequency"] = df.get("payfrequency")
    df_out["baserate"] = df.get("baserate")
    df_out["vacationhours"] = df.get("vacationhours")
    df_out["sickleavehours"] = df.get("sickleavehours")
    df_out["salespersonflag"] = df.get("salespersonflag")
    df_out["departmentname"] = df.get("departmentname")
    df_out["startdate"] = pd.to_datetime(df.get("startdate"), errors="coerce")
    df_out["enddate"] = pd.to_datetime(df.get("enddate"), errors="coerce")

    # Reemplazar NaN por None para facilitar inserts
    df_out = df_out.where(pd.notnull(df_out), None)

    print("DimEmployee transformado.")
    return df_out


def transform_factsalesquota(df_quota: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    """
    Transforma el extract de cuotas (salespersonquotahistory) al layout de public.factsalesquota.
    Resuelve surrogate key de empleado (employeekey) a partir de public.dimemployee (employeenationalidalternatekey).
    Genera datekey (YYYYMMDD), calendaryear y calendarquarter.
    """
    if df_quota is None or df_quota.empty:
        print("No hay datos en df_quota")
        return pd.DataFrame(columns=["employeekey", "datekey", "calendaryear", "calendarquarter", "salesamountquota", "date"])

    print("Transformando FactSalesQuota...")
    df = df_quota.copy()

    # Normalizar fecha
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["datekey"] = df["date"].dt.strftime("%Y%m%d").astype('Int64')
    df["calendaryear"] = df["date"].dt.year.astype('Int64')
    df["calendarquarter"] = df["date"].dt.quarter.astype('Int64')

    # lookup employeekey desde dimemployee
    try:
        dim_emp = pd.read_sql("SELECT employeekey, employeenationalidalternatekey FROM public.dimemployee", target_engine)
    except Exception:
        dim_emp = pd.DataFrame(columns=["employeekey", "employeenationalidalternatekey"])

    if not dim_emp.empty and "employeenationalidalternatekey" in df.columns:
        df = df.merge(dim_emp, how="left", left_on="employeenationalidalternatekey", right_on="employeenationalidalternatekey")
        # employeekey column from dim_emp
        df["employeekey"] = df["employeekey"]
    else:
        df["employeekey"] = None

    # Seleccionar y renombrar columnas al layout de factsalesquota
    df_out = df[["employeekey", "datekey", "calendaryear", "calendarquarter", "salesquota", "date"]].copy()
    df_out = df_out.rename(columns={"salesquota": "salesamountquota"})

    # Quitar filas sin employeekey o datekey
    df_out = df_out.dropna(subset=["employeekey", "datekey"]).reset_index(drop=True)

    # Convertir tipos
    df_out["employeekey"] = df_out["employeekey"].astype(int)
    df_out["datekey"] = df_out["datekey"].astype(int)
    df_out["calendaryear"] = df_out["calendaryear"].astype(int)
    df_out["calendarquarter"] = df_out["calendarquarter"].astype(int)

    print("FactSalesQuota transformado con surrogate keys.")
    return df_out

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
    dim_customer["spanisheducation"] = dim_customer["englisheducation"]#.apply(lambda x: safe_translate(translator_es, x))
    dim_customer["frencheducation"] = dim_customer["englisheducation"]#.apply(lambda x: safe_translate(translator_fr, x))
    dim_customer["spanishoccupation"] = dim_customer["englishoccupation"]#.apply(lambda x: safe_translate(translator_es, x))
    dim_customer["frenchoccupation"] = dim_customer["englishoccupation"]#.apply(lambda x: safe_translate(translator_fr, x))

    dim_customer.drop(["customer_bk", "person_bk", "additionalcontactinfo","demographics", "modifieddate","city", "postalcode","persontype","emailpromotion"], axis=1, inplace=True)

    # Limpieza final
    dim_customer = dim_customer.replace({np.nan: None})
    print("DimCustomer transformado.")
    return dim_customer


def transform_reseller(df_reseller: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    """
    Transforma el extract de vendedores (purchasing.vendor) al layout de `public.dimreseller`.
    Se mapean los campos disponibles y se rellenan columnas faltantes con None o valores por defecto.
    """
    print("Transformando DimReseller...")
    # Columnas objetivo según olap.sql (sin el surrogate key `resellerkey`)
    cols = [
        "geographykey",
        "reselleralternatekey",
        "phone",
        "businesstype",
        "resellername",
        "numberemployees",
        "orderfrequency",
        "ordermonth",
        "firstorderyear",
        "lastorderyear",
        "productline",
        "addressline1",
        "addressline2",
        "annualsales",
        "bankname",
        "minpaymenttype",
        "minpaymentamount",
        "annualrevenue",
        "yearopened",
    ]

    if df_reseller is None or df_reseller.empty:
        print("No hay datos en df_reseller")
        return pd.DataFrame(columns=cols)

    df = df_reseller.copy()

    # Normalizar nombres de columnas
    lower_map = {c.lower(): c for c in df.columns}
    acct_col = lower_map.get("reseller_accountnumber") or lower_map.get("accountnumber")
    name_col = lower_map.get("reseller_name") or lower_map.get("name")
    demo_col = lower_map.get("demographics_xml") or lower_map.get("demographics")
    addr1_col = lower_map.get("addressline1")
    addr2_col = lower_map.get("addressline2")
    city_col = lower_map.get("city")
    postal_col = lower_map.get("postalcode")

    # Crear df_out con el mismo índice que el DF de entrada para evitar problemas de alignment
    df_out = pd.DataFrame(index=df.index)
    # Inicialmente geographykey será None; intentaremos resolverlo luego mediante lookup
    df_out["geographykey"] = None
    df_out["reselleralternatekey"] = df[acct_col].values if acct_col in df.columns else None

    # Parsear XML de demographics para obtener varios campos
    def parse_demo(xml_text: str) -> dict:
        out = {
            "annualrevenue": None,
            "yearopened": None,
            "bankname": None,
            "annualsales": None,
            "numberemployees": None,
            "productline": None,
            "businesstype_raw": None,
        }
        if not xml_text or pd.isna(xml_text):
            return out
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return out

        # Buscar por etiquetas conocidas (case-insensitive)
        for child in root.iter():
            tag = child.tag.lower()
            text = child.text.strip() if child.text else None
            if not text:
                continue
            if tag.endswith("annualrevenue"):
                try:
                    out["annualrevenue"] = float(text.replace("$", "").replace(",", ""))
                except Exception:
                    out["annualrevenue"] = None
            elif tag.endswith("yearopened") or tag.endswith("yearopened"):
                try:
                    out["yearopened"] = int(text)
                except Exception:
                    out["yearopened"] = None
            elif tag.endswith("bankname"):
                out["bankname"] = text
            elif tag.endswith("annualsales"):
                try:
                    out["annualsales"] = float(text.replace("$", "").replace(",", ""))
                except Exception:
                    out["annualsales"] = None
            elif tag.endswith("numberemployees"):
                try:
                    out["numberemployees"] = int(text)
                except Exception:
                    out["numberemployees"] = None
            elif tag.endswith("specialty") or tag.endswith("productline"):
                out["productline"] = text
            elif tag.endswith("businesstype"):
                out["businesstype_raw"] = text

        return out

    demo_parsed = df[demo_col].apply(lambda x: parse_demo(x) if demo_col in df.columns else {
        "annualrevenue": None,
        "yearopened": None,
        "bankname": None,
        "annualsales": None,
        "numberemployees": None,
        "productline": None,
        "businesstype_raw": None,
    })
    demo_df = pd.DataFrame(list(demo_parsed))

    # Mapear business type codes
    bt_map = {"OS": "Warehouse", "BS": "Specialty Bike Shop", "BM": "Value Added Reseller"}

    df_out["businesstype"] = demo_df["businesstype_raw"].map(lambda v: bt_map.get(v.strip(), v) if isinstance(v, str) else None)
    df_out["resellername"] = df[name_col] if name_col in df.columns else None

    # Mapear order frecuency codes
    of_map = {
        'BM': 'S',
        'BS': 'A',
        'OS': 'Q'
    }

    # Mapear campos extraídos del XML
    df_out["numberemployees"] = demo_df["numberemployees"].astype(object)
    df_out["orderfrequency"] = df_out['businesstype'].map(of_map)
    df_out["ordermonth"] = df_reseller['ordermonth']
    df_out["firstorderyear"] = df_reseller['firstorderyear']
    df_out["lastorderyear"] = df_reseller['lastorderyear']
    df_out["productline"] = demo_df["productline"]
    df_out["addressline1"] = df[addr1_col] if addr1_col in df.columns else None
    df_out["addressline2"] = df[addr2_col] if addr2_col in df.columns else None
    df_out["annualsales"] = demo_df["annualsales"].astype(object)
    df_out["bankname"] = demo_df["bankname"]
    df_out["minpaymenttype"] = None
    df_out["minpaymentamount"] = None
    df_out["annualrevenue"] = demo_df["annualrevenue"].astype(object)
    df_out["yearopened"] = demo_df["yearopened"].astype(object)
    df_out['phone'] = df_reseller['phone']
    
    # Resolver geographykey a partir de city+postalcode (si están disponibles)
    if city_col in df.columns and postal_col in df.columns:
        df_addr = df[[city_col, postal_col]].copy()
        df_addr = df_addr.rename(columns={city_col: "city", postal_col: "postalcode"})
        # Normalizar para matching
        df_addr["city"] = df_addr["city"].astype(str).str.strip().str.lower()
        df_addr["postalcode"] = df_addr["postalcode"].astype(str).str.strip()

        # Cargar dimgeography para lookup y normalizar
        try:
            dim_geo = pd.read_sql("SELECT geographykey, city, postalcode FROM public.dimgeography", target_engine)
            dim_geo["city"] = dim_geo["city"].astype(str).str.strip().str.lower()
            dim_geo["postalcode"] = dim_geo["postalcode"].astype(str).str.strip()
        except Exception:
            dim_geo = pd.DataFrame(columns=["geographykey", "city", "postalcode"])

        if not dim_geo.empty:
            # Deduplicar la dimensión a una sola fila por (city, postalcode)
            dim_geo_unique = dim_geo.drop_duplicates(subset=["city", "postalcode"], keep="first")[["city", "postalcode", "geographykey"]]
            # Hacer un merge left que no expandirá filas (dim_geo_unique tiene keys únicas)
            merged = df_addr.merge(dim_geo_unique, how="left", on=["city", "postalcode"])
            # Asignar geographykey garantizando la misma longitud que df
            df_out["geographykey"] = merged["geographykey"].values
        else:
            df_out["geographykey"] = None
    else:
        df_out["geographykey"] = None

    # Asegurar orden y reemplazar NaN por None
    df_out = df_out[cols]
    df_out = df_out.where(pd.notnull(df_out), None)

    print("DimReseller transformado.")
    return df_out

def transform_fact_internet_sales(df_fact: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    if df_fact.empty:
        print("DF de ventas vacío.")
        return df_fact
    
    df_fact["currency_bk"] = df_fact["currency_bk"].fillna("USD")

    # ============================
    # 1. Cargar DIM para lookups
    # ============================
    dim_product = pd.read_sql("SELECT productkey, productalternatekey FROM public.dimproduct", target_engine)
    dim_customer = pd.read_sql("SELECT customerkey, customeralternatekey FROM public.dimcustomer", target_engine)
    dim_promotion = pd.read_sql("SELECT promotionkey, promotionalternatekey FROM public.dimpromotion", target_engine)
    dim_currency = pd.read_sql("SELECT currencykey, currencyalternatekey FROM public.dimcurrency", target_engine)
    dim_territory = pd.read_sql("SELECT salesterritorykey, salesterritoryalternatekey FROM public.dimsalesterritory", target_engine)

    # ============================
    # 2. LOOKUP de surrogate keys
    # ============================

    # PRODUCT
    df_fact = df_fact.merge(dim_product,
                            how="left",
                            left_on="product_bk",
                            right_on="productalternatekey")
    df_fact.rename(columns={"productkey_x": "productalternatekey",
                            "productkey_y": "productkey"}, inplace=True)

    # CUSTOMER
    df_fact = df_fact.merge(dim_customer,
                            how="left",
                            left_on="customer_bk",
                            right_on="customeralternatekey")
    df_fact.rename(columns={"customerkey_y": "customerkey"}, inplace=True)

    # PROMOTION
    df_fact = df_fact.merge(dim_promotion,
                            how="left",
                            left_on="promotion_bk",
                            right_on="promotionalternatekey")
    df_fact.rename(columns={"promotionkey_y": "promotionkey"}, inplace=True)

    # CURRENCY
    df_fact = df_fact.merge(dim_currency,
                            how="left",
                            left_on="currency_bk",
                            right_on="currencyalternatekey")
    df_fact.rename(columns={"currencykey_y": "currencykey"}, inplace=True)

    # TERRITORY
    df_fact = df_fact.merge(dim_territory,
                            how="left",
                            left_on="salesterritory_bk",
                            right_on="salesterritoryalternatekey")
    df_fact.rename(columns={"salesterritorykey_y": "salesterritorykey"}, inplace=True)

    df_fact["salesorderlinenumber"] = (
    df_fact.sort_values(["salesordernumber"])       # ordena por orden de venta
      .groupby("salesordernumber")
      .cumcount() + 1
    )

    # ======================
    # 3. Limpiar columnas
    # ======================
    cols_to_keep = [
        "productkey",
        "orderdatekey",
        "duedatekey",
        "shipdatekey",
        "customerkey",
        "promotionkey",
        "currencykey",
        "salesterritorykey",
        "salesordernumber",
        "salesorderlinenumber",
        "revisionnumber",
        "orderquantity",
        "unitprice",
        "extendedamount",
        "unitpricediscountpct",
        "discountamount",
        "productstandardcost",
        "totalproductcost",
        "salesamount",
        "taxamt",
        "freight",
        "carriertrackingnumber",
        "customerponumber",
        "orderdate",
        "duedate",
        "shipdate",
        "saved"
    ]
    df_fact["saved"] = date.today()

    df_fact = df_fact[cols_to_keep]

    df_fact.dropna(subset=[
        "productkey",
        "orderdatekey",
        "duedatekey",
        "shipdatekey",
        "customerkey",
        "promotionkey",
        "currencykey",
        "salesterritorykey",
        "salesordernumber",
        "revisionnumber",
        "orderquantity",
        "unitprice",
        "extendedamount",
        "unitpricediscountpct",
        "discountamount",
        "productstandardcost",
        "totalproductcost",
        "salesamount",
        "taxamt",
        "freight"
        ], inplace=True)

    print("FactInternetSales transformado con surrogate keys.")
    return df_fact


def transform_fact_internet_sales_reason(df_fact_reason: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    if df_fact_reason.empty:
        print("DF de ventas vacío.")
        return df_fact_reason
    print("Transformando FactInternetSalesReason...")

    # Cargar dimensiones necesarias para lookups
    dim_salesreason = pd.read_sql("SELECT salesreasonkey, salesreasonalternatekey FROM public.dimsalesreason", target_engine)

    # LOOKUP SALESREASON
    df_fact_reason = df_fact_reason.merge(dim_salesreason,
                            how="left",
                            left_on="salesreason_bk",
                            right_on="salesreasonalternatekey")
    df_fact_reason.rename(columns={"salesreasonkey_x": "salesreasonalternatekey",
                            "salesreasonkey_y": "salesreasonkey"}, inplace=True)

    df_fact_reason["salesorderlinenumber"] = df_fact_reason.sort_values(["salesordernumber", "salesreasonkey"]).groupby(["salesordernumber", "salesreasonkey"]).cumcount() + 1

    # Seleccionar columnas finales
    cols_to_keep = [
        "salesordernumber",
        "salesorderlinenumber",
        "salesreasonkey"
    ]

    df_fact_reason = df_fact_reason[cols_to_keep]
    df_fact_reason["saved"] = date.today()

    print("FactInternetSalesReason transformado con surrogate keys.")

    return df_fact_reason


def transform_fact_resellers(df_fact: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    """
    Transforma el extract `extract_fact_resellers` al layout de `public.factresellersales`.
    Realiza lookups a dimensiones: product, reseller (dimreseller), employee (dimemployee), promotion,
    currency y salesterritory para resolver surrogate keys.
    """
    if df_fact is None or df_fact.empty:
        print("DF de ventas de reseller vacío.")
        return pd.DataFrame()

    df = df_fact.copy()

    # Cargar dimensiones para lookups
    try:
        dim_product = pd.read_sql("SELECT productkey, productalternatekey FROM public.dimproduct", target_engine)
    except Exception:
        dim_product = pd.DataFrame(columns=["productkey", "productalternatekey"])

    try:
        dim_reseller = pd.read_sql("SELECT resellerkey, reselleralternatekey FROM public.dimreseller", target_engine)
    except Exception:
        dim_reseller = pd.DataFrame(columns=["resellerkey", "reselleralternatekey"])

    try:
        dim_emp = pd.read_sql("SELECT employeekey, employeenationalidalternatekey FROM public.dimemployee", target_engine)
    except Exception:
        dim_emp = pd.DataFrame(columns=["employeekey", "employeenationalidalternatekey"])

    try:
        dim_promo = pd.read_sql("SELECT promotionkey, promotionalternatekey FROM public.dimpromotion", target_engine)
    except Exception:
        dim_promo = pd.DataFrame(columns=["promotionkey", "promotionalternatekey"])

    try:
        dim_currency = pd.read_sql("SELECT currencykey, currencyalternatekey FROM public.dimcurrency", target_engine)
    except Exception:
        dim_currency = pd.DataFrame(columns=["currencykey", "currencyalternatekey"])

    try:
        dim_terr = pd.read_sql("SELECT salesterritorykey, salesterritoryalternatekey FROM public.dimsalesterritory", target_engine)
    except Exception:
        dim_terr = pd.DataFrame(columns=["salesterritorykey", "salesterritoryalternatekey"])

    # LOOKUP PRODUCT
    if not dim_product.empty and "product_bk" in df.columns:
        df = df.merge(dim_product, how="left", left_on="product_bk", right_on="productalternatekey")
        # rename productkey column to expected name
        df.rename(columns={"productkey": "productkey"}, inplace=True)
    else:
        df["productkey"] = None

    # LOOKUP RESELLER (match accountnumber -> reselleralternatekey)
    if not dim_reseller.empty and "resellerkey" in df.columns:
        df = df.merge(dim_reseller, how="left", left_on="resellerkey", right_on="reselleralternatekey")
        df.rename(columns={"resellerkey": "resellerkey"}, inplace=True)
        # after merge we have column `resellerkey` from dim and original `resellerkey` from extract; keep dim's
        if "resellerkey_y" in df.columns:
            df["resellerkey"] = df["resellerkey_y"]
    else:
        df["resellerkey"] = None

    # LOOKUP EMPLOYEE (employeenationalidalternatekey)
    if not dim_emp.empty and "employeekey" in df.columns:
        df = df.merge(dim_emp, how="left", left_on="employeekey", right_on="employeenationalidalternatekey")
        if "employeekey_y" in df.columns:
            df["employeekey"] = df["employeekey_y"]
    else:
        df["employeekey"] = None

    # LOOKUP PROMOTION
    if not dim_promo.empty and "promotion_bk" in df.columns:
        df = df.merge(dim_promo, how="left", left_on="promotion_bk", right_on="promotionalternatekey")
        if "promotionkey_y" in df.columns:
            df["promotionkey"] = df["promotionkey_y"]
    else:
        df["promotionkey"] = None

    # LOOKUP CURRENCY
    if not dim_currency.empty and "currency_bk" in df.columns:
        df = df.merge(dim_currency, how="left", left_on="currency_bk", right_on="currencyalternatekey")
        if "currencykey_y" in df.columns:
            df["currencykey"] = df["currencykey_y"]
    else:
        df["currencykey"] = None

    # LOOKUP TERRITORY
    if not dim_terr.empty and "salesterritory_bk" in df.columns:
        df = df.merge(dim_terr, how="left", left_on="salesterritory_bk", right_on="salesterritoryalternatekey")
        if "salesterritorykey_y" in df.columns:
            df["salesterritorykey"] = df["salesterritorykey_y"]
    else:
        df["salesterritorykey"] = None

    # Generar salesorderlinenumber por orden
    df["salesorderlinenumber"] = (
        df.sort_values(["salesordernumber"]) 
          .groupby("salesordernumber")
          .cumcount() + 1
    )

    # columnas finales esperadas
    cols_to_keep = [
        "productkey",
        "orderdatekey",
        "duedatekey",
        "shipdatekey",
        "resellerkey",
        "employeekey",
        "promotionkey",
        "currencykey",
        "salesterritorykey",
        "salesordernumber",
        "salesorderlinenumber",
        "revisionnumber",
        "orderquantity",
        "unitprice",
        "extendedamount",
        "unitpricediscountpct",
        "discountamount",
        "productstandardcost",
        "totalproductcost",
        "salesamount",
        "taxamt",
        "freight",
        "carriertrackingnumber",
        "customerponumber",
        "orderdate",
        "duedate",
        "shipdate",
        "saved"
    ]

    df["saved"] = date.today()

    # Seleccionar columnas (asegurar que existan)
    for c in cols_to_keep:
        if c not in df.columns:
            df[c] = None

    df_out = df[cols_to_keep].copy()

    # Eliminar filas sin surrogate keys críticas
    df_out.dropna(subset=[
        "productkey",
        "orderdatekey",
        "resellerkey",
        "employeekey",
        "currencykey"
    ], inplace=True)

    # Convertir tipos cuando aplique
    try:
        df_out["productkey"] = df_out["productkey"].astype(int)
    except Exception:
        pass
    try:
        df_out["resellerkey"] = df_out["resellerkey"].astype(int)
    except Exception:
        pass
    try:
        df_out["employeekey"] = df_out["employeekey"].astype(int)
    except Exception:
        pass
    try:
        df_out["currencykey"] = df_out["currencykey"].astype(int)
    except Exception:
        pass

    df_out = df_out.where(pd.notnull(df_out), None)

    print("FactResellerSales transformado con surrogate keys.")
    return df_out

def transform_factsurveyresponse(df_survey: pd.DataFrame, target_engine: Engine) -> pd.DataFrame:
    """
    Transforma el extract de survey response al layout de public.factsurveyresponse
    - Resuelve surrogate keys para customer, productcategory y productsubcategory
    - Genera datekey a partir de la fecha de orden (orderdate)
    """
    if df_survey is None or df_survey.empty:
        print("No hay datos en df_survey")
        return pd.DataFrame(columns=[
            "datekey",
            "customerkey",
            "productcategorykey",
            "englishproductcategoryname",
            "productsubcategorykey",
            "englishproductsubcategoryname",
            "date"
        ])

    print("Transformando FactSurveyResponse...")

    # Cargar dimensiones necesarias para lookups
    dim_customer = pd.read_sql("SELECT customerkey, customeralternatekey FROM public.dimcustomer", target_engine)
    dim_cat = pd.read_sql("SELECT productcategorykey, productcategoryalternatekey, englishproductcategoryname FROM public.dimproductcategory", target_engine)
    dim_sub = pd.read_sql("SELECT productsubcategorykey, productsubcategoryalternatekey, englishproductsubcategoryname FROM public.dimproductsubcategory", target_engine)

    df = df_survey.copy()

    # LOOKUP CUSTOMER
    df = df.merge(dim_customer, how="left", left_on="customer_bk", right_on="customeralternatekey")
    # LOOKUP PRODUCT CATEGORY
    df = df.merge(dim_cat, how="left", left_on="productcategory_bk", right_on="productcategoryalternatekey")
    # LOOKUP PRODUCT SUBCATEGORY
    df = df.merge(dim_sub, how="left", left_on="productsubcategory_bk", right_on="productsubcategoryalternatekey")

    # Normalizar fecha y generar datekey
    #df["date"] = pd.to_datetime(df["orderdate"]) if "orderdate" in df.columns else pd.to_datetime(df.get("date", None))
    #df["datekey"] = df["date"].dt.strftime("%Y%m%d").astype(float).astype('Int64')

    df = df.rename(columns={
        "englishproductcategoryname_y": "englishproductcategoryname",
        "englishproductsubcategoryname_y": "englishproductsubcategoryname",
        "orderdate": "date"
    })

    # Seleccionar columnas finales en el orden esperado
    cols_to_keep = [
        "datekey",
        "customerkey",
        "productcategorykey",
        "englishproductcategoryname",
        "productsubcategorykey",
        "englishproductsubcategoryname",
        "date"
    ]

    df = df[cols_to_keep]
    # Eliminar filas con claves faltantes (no tienen surrogate keys)
    df = df.dropna(subset=["datekey", "customerkey", "productcategorykey", "productsubcategorykey"]).reset_index(drop=True)

    # Convertir tipos a enteros cuando aplique
    df["datekey"] = df["datekey"].astype(int)
    df["customerkey"] = df["customerkey"].astype(int)
    df["productcategorykey"] = df["productcategorykey"].astype(int)
    df["productsubcategorykey"] = df["productsubcategorykey"].astype(int) 

    print("FactSurveyResponse transformado con surrogate keys.")
    return df

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
        translator_es = GoogleTranslator(source='en', target='es')
        translator_fr = GoogleTranslator(source='en', target='fr')
        dim_date["spanishmonthname"] = dim_date["englishmonthname"].apply(lambda x: safe_translate(translator_es, x))
        dim_date["frenchmonthname"] = dim_date["englishmonthname"].apply(lambda x: safe_translate(translator_fr, x))
    
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