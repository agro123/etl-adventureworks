import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from datetime import datetime

#df_prod_recent = extract_product(source_engine, fecha=datetime(2025, 10, 1))

# INTERNET SALES EXTRACTION FUNCTIONS
def extract_product(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """Extrae productos desde production.product junto con categoría y subcategoría.
       Si se pasa una fecha, filtra productos modificados desde esa fecha hasta hoy."""
    q_base = '''
        SELECT 
            p.productid AS product_bk,
            p.name AS product_name,
            p.productnumber AS product_number,
            p.listprice,
            p.color,
            p.size,
            p.weight,
            p.weightunitmeasurecode,
            p.sizeunitmeasurecode,
            p.standardcost,
            p.finishedgoodsflag,
            p.safetystocklevel,
            p.reorderpoint,
            p.daystomanufacture,
            p.productline,
            p.class,
            p.style,
            p.sellstartdate,
            p.sellenddate,
            p.discontinueddate,
            psc.productsubcategoryid AS productsubcategory_bk
        FROM production.product p
        LEFT JOIN production.productsubcategory psc 
            ON p.productsubcategoryid = psc.productsubcategoryid
    '''
    # Agregamos filtro si hay fecha
    if fecha:
        q_base += " WHERE p.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_product: {e}")
        return pd.DataFrame()


def extract_product_subcategory(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """Extrae subcategorías desde production.productsubcategory.
       Si se pasa una fecha, filtra las modificadas desde esa fecha hasta hoy."""
    q_base = '''
        SELECT 
            psc.productsubcategoryid AS productsubcategory_bk,
            psc.name AS productsubcategory_name,
            psc.productcategoryid AS productcategory_bk,
            psc.modifieddate
        FROM production.productsubcategory psc
    '''
    if fecha:
        q_base += " WHERE psc.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_product_subcategory: {e}")
        return pd.DataFrame()


def extract_product_category(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """Extrae categorías desde production.productcategory.
       Si se pasa una fecha, filtra las modificadas desde esa fecha hasta hoy."""
    q_base = '''
        SELECT 
            pc.productcategoryid AS productcategory_bk,
            pc.name AS productcategory_name,
            pc.modifieddate
        FROM production.productcategory pc
    '''
    if fecha:
        q_base += " WHERE pc.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_product_category: {e}")
        return pd.DataFrame()

def extract_customer(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    q_base = '''
        SELECT 
            c.accountnumber AS customer_bk,
            c.accountnumber,
            c.territoryid AS territory_bk,
            p.businessentityid AS person_bk,
            p.persontype,
            p.namestyle,
            p.title,
            p.firstname,
            p.middlename,
            p.lastname,
            p.suffix,
            p.emailpromotion,
            p.additionalcontactinfo,
            p.demographics,
            ea.emailaddress,
            a.addressline1,
            a.addressline2,
            a.city,
            a.postalcode,
            c.modifieddate
        FROM sales.customer c
        LEFT JOIN person.person p ON c.personid = p.businessentityid
        LEFT JOIN person.emailaddress ea ON p.businessentityid = ea.businessentityid
        LEFT JOIN person.address a ON a.addressid = c.customerid
        WHERE p.demographics IS NOT NULL
    '''
    if fecha:
        q_base += " WHERE c.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_customer: {e}")
        return pd.DataFrame()


def extract_promotion(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae promociones desde sales.specialoffer.
    Si se pasa una fecha, filtra las modificadas desde esa fecha hasta hoy.
    """
    q_base = '''
        SELECT 
            specialofferid AS promotion_bk,
            description,
            discountpct,
            type,
            category,
            startdate,
            enddate,
            minqty,
            maxqty,
            modifieddate
        FROM sales.specialoffer
    '''
    if fecha:
        q_base += " WHERE modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_promotion: {e}")
        return pd.DataFrame()

def extract_currency(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae monedas desde sales.currency.
    Si se pasa una fecha, filtra las modificadas desde esa fecha hasta hoy.
    """
    q_base = '''
        SELECT 
            currencycode AS currency_bk,
            name AS currency_name,
            modifieddate
        FROM sales.currency
    '''
    if fecha:
        q_base += " WHERE modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_currency: {e}")
        return pd.DataFrame()

def extract_salesreason(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae las razones de venta desde sales.salesreason.
    Si se pasa una fecha, filtra las filas modificadas desde esa fecha.
    Retorna columnas con alias consistentes para el ETL:
      - salesreason_bk
      - salesreason_name
      - salesreason_reasontype
      - modifieddate
    """
    q_base = '''
        SELECT
            salesreasonid AS salesreason_bk,
            name AS salesreason_name,
            reasontype AS salesreason_reasontype,
            modifieddate
        FROM sales.salesreason
    '''
    if fecha:
        q_base += " WHERE modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_salesreason: {e}")
        return pd.DataFrame()

def extract_salesterritory(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae territorios de ventas desde sales.salesterritory.
    Si se pasa una fecha, filtra los registros modificados desde esa fecha hasta hoy.
    """
    q_base = '''
        SELECT 
            st.territoryid AS salesterritory_bk,
            st.name AS salesterritory_name,
            st.countryregioncode,
            st."group" AS salesterritory_group
        FROM sales.salesterritory st
    '''
    if fecha:
        q_base += " WHERE st.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_salesterritory: {e}")
        return pd.DataFrame()

def extract_geography(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae información geográfica desde person.address, person.stateprovince,
    person.countryregion y sales.salesterritory.
    Si se pasa una fecha, filtra las direcciones modificadas desde esa fecha hasta hoy.
    """
    q_base = '''
        SELECT 
            a.addressid AS address_bk,
            a.city,
            sp.stateprovincecode,
            sp.name AS stateprovincename,
            cr.countryregioncode,
            cr.name AS englishcountryregionname,
            a.postalcode,
            sp.territoryid AS salesterritory_bk,
            a.modifieddate
        FROM person.address a
        INNER JOIN person.stateprovince sp ON a.stateprovinceid = sp.stateprovinceid
        INNER JOIN person.countryregion cr ON sp.countryregioncode = cr.countryregioncode
        INNER JOIN sales.salesterritory st ON sp.territoryid = st.territoryid
    '''
    if fecha:
        q_base += " WHERE a.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            df = pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
            return df
    except Exception as e:
        print(f"Error en extract_geography: {e}")
        return pd.DataFrame()
    
def extract_employee(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae información de empleados desde humanresources.employee
    y tablas relacionadas (person.person, person.emailaddress, person.personphone, sales.salesperson).
    Retorna un DataFrame con columnas alineadas para la transformación de dimEmployee.
    """
    q_base = '''
        SELECT
            e.businessentityid AS employee_bk,
            e.nationalidnumber AS employeenationalidalternatekey,
            concat(firstname, ' ', lastname) AS emergencycontactname,
            pp.phonenumber AS emergencycontactphone,
            p.firstname,
            p.middlename,
            p.lastname,
            p.namestyle,
            e.jobtitle as title,
            e.hiredate,
            e.birthdate,
            e.loginid,
            ea.emailaddress,
            pp.phonenumber AS phone,
            e.maritalstatus,
            e.salariedflag,
            e.gender,
            sp.territoryid AS salesterritory_bk,
            edh.rate AS baserate,
            edh.payfrequency,
            e.vacationhours,
            e.sickleavehours,
            d.name AS departmentname,
            edh2.startdate,
            edh2.enddate,
            (CASE WHEN edh2.enddate IS NOT NULL THEN 'Current' ELSE Null END) AS status,
            (sp.businessentityid IS NOT NULL) AS salespersonflag,
            e.modifieddate
        FROM humanresources.employee e
        LEFT JOIN person.person p ON e.businessentityid = p.businessentityid
        LEFT JOIN person.emailaddress ea ON p.businessentityid = ea.businessentityid
        LEFT JOIN person.personphone pp ON p.businessentityid = pp.businessentityid
        LEFT JOIN sales.salesperson sp ON e.businessentityid = sp.businessentityid
        LEFT JOIN humanresources.employeepayhistory edh ON e.businessentityid = edh.businessentityid
        LEFT JOIN humanresources.employeedepartmenthistory edh2 ON e.businessentityid = edh2.businessentityid
        LEFT JOIN humanresources.department d ON edh2.departmentid = d.departmentid
    '''
    if fecha:
        q_base += " WHERE e.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_employee: {e}")
        return pd.DataFrame()

def extract_fact_internet_sales(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    q_base = '''
        SELECT 
            soh.salesorderid,
            soh.salesordernumber,
            -- sod.salesorderdetailid AS salesorderlinenumber,
            (1) AS revisionnumber,
            sod.orderqty AS orderquantity,
            sod.unitprice,
            sod.linetotal AS extendedamount,
            sod.unitpricediscount AS unitpricediscountpct,
            (sod.unitprice * sod.orderqty * sod.unitpricediscount) AS discountamount,
            p.standardcost AS productstandardcost,
            (p.standardcost * sod.orderqty) AS totalproductcost,
            sod.linetotal AS salesamount,
            soh.taxamt,
            soh.freight,
            sod.carriertrackingnumber,
            soh.purchaseordernumber AS customerponumber,
            TO_CHAR(soh.orderdate::date, 'YYYYMMDD')::integer AS orderdatekey,
            TO_CHAR(soh.duedate::date, 'YYYYMMDD')::integer AS duedatekey,
            TO_CHAR(soh.shipdate::date, 'YYYYMMDD')::integer AS shipdatekey,
            soh.orderdate,
            soh.duedate,
            soh.shipdate,
            c.accountnumber AS customer_bk,
            p.productnumber AS product_bk,
            sod.specialofferid AS promotion_bk,
            cr.tocurrencycode AS currency_bk,
            soh.territoryid AS salesterritory_bk,
            soh.modifieddate
        FROM sales.salesorderheader soh
        INNER JOIN sales.salesorderdetail sod 
            ON soh.salesorderid = sod.salesorderid
        LEFT JOIN production.product p 
            ON sod.productid = p.productid
        LEFT JOIN sales.currencyrate cr 
            ON soh.currencyrateid = cr.currencyrateid
        LEFT JOIN sales.customer c 
            ON soh.customerid = c.customerid
        LEFT JOIN sales.specialoffer so 
            ON sod.specialofferid = so.specialofferid
    '''
    if fecha:
        q_base += " WHERE soh.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_fact_internet_sales: {e}")
        return pd.DataFrame()

def extract_fact_internet_sales_reason(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    q_base = '''
        SELECT 
            soh.salesordernumber,
            sor.salesreasonid AS salesreason_bk,
            soh.modifieddate
        FROM sales.salesorderheader soh
        INNER JOIN sales.salesorderdetail sod 
            ON soh.salesorderid = sod.salesorderid
        INNER JOIN sales.salesorderheadersalesreason sohsr 
            ON soh.salesorderid = sohsr.salesorderid
        INNER JOIN sales.salesreason sor 
            ON sohsr.salesreasonid = sor.salesreasonid
    '''
    if fecha:
        q_base += " WHERE soh.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_fact_internet_sales_reason: {e}")
        return pd.DataFrame()


def extract_factsurveyresponse(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    """
    Extrae una fila por cliente con la información de su última compra (categoria/subcategoria)
    y la fecha de la orden. Esta vista se usa como proxy del 'survey response' en AW.
    Si se pasa una fecha, filtra las órdenes modificadas desde esa fecha.

    Retorna columnas:
      - customer_bk
      - productcategory_bk
      - englishproductcategoryname
      - productsubcategory_bk
      - englishproductsubcategoryname
      - orderdate
    """
    q_base = '''
        SELECT 
			TO_CHAR(soh.orderdate::date, 'YYYYMMDD')::integer AS datekey,
			c.accountnumber AS customer_bk,
			p3.productcategoryid as productcategory_bk,
			p3."name" as englishproductcategoryname,
			p2.productsubcategoryid as productsubcategory_bk,
			p2."name" as englishproductsubcategoryname,
			soh.orderdate
        FROM sales.salesorderheader soh
        LEFT JOIN sales.salesorderdetail sod 
            ON soh.salesorderid = sod.salesorderid
        INNER JOIN production.product p 
            ON sod.productid = p.productid
        INNER JOIN sales.customer c 
            ON soh.customerid = c.customerid
        INNER JOIN person.person pn
            ON c.personid = pn.businessentityid AND pn.demographics IS NOT NULL
       INNER JOIN production.productsubcategory p2
            ON p.productsubcategoryid  = p2.productsubcategoryid
       INNER JOIN production.productcategory p3
            ON p2.productcategoryid  = p3.productcategoryid 
       GROUP BY soh.orderdate, c.accountnumber, p3.productcategoryid, p2.productsubcategoryid
    '''

    # Aplicar filtro por fecha sobre orderdate si se indica
    if fecha:
        q_base += " WHERE e.modifieddate >= :fecha;"
    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_factsurveyresponse: {e}")
        return pd.DataFrame()

def extract_salesquota(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
        """
        Extrae el histórico de cuotas de ventas desde sales.salespersonquotahistory.
        Devuelve columnas mínimas necesarias para transformar a public.factsalesquota:
          - employee_bk (businessentityid)
          - employeenationalidalternatekey (joined from humanresources.employee)
          - date (quotadate)
          - salesquota
          - modifieddate
        """
        q_base = '''
            SELECT
                sq.businessentityid AS employee_bk,
                e.nationalidnumber AS employeenationalidalternatekey,
                sq.quotadate AS date,
                sq.salesquota::numeric AS salesquota,
                sq.modifieddate
            FROM sales.salespersonquotahistory sq
            LEFT JOIN humanresources.employee e ON sq.businessentityid = e.businessentityid
        '''
        if fecha:
            q_base += " WHERE sq.modifieddate >= :fecha;"
        else:
            q_base += ";"

        try:
            with source_engine.connect() as conn:
                return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
        except Exception as e:
            print(f"Error en extract_salesquota: {e}")
            return pd.DataFrame()


def extract_reseller(source_engine: Engine, fecha: datetime | None = None) -> pd.DataFrame:
    # Ahora obtenemos la información desde sales.customer + sales.store
    # - reseller_accountnumber: sales.customer.accountnumber
    # - reseller_name: sales.store.name (join via storeid)
    # - demographics (XML) desde sales.store.demographics
    # - dirección: person.businessentityaddress -> person.address (join usando store.businessentityid)
    q_base = '''
        WITH ranked AS (
            SELECT
                c.storeid,
                c.accountnumber AS reseller_accountnumber,
                s.businessentityid AS store_bk,
                s.name AS reseller_name,
                s.demographics AS demographics_xml,
                a.addressline1,
                a.addressline2,
                p.phonenumber AS phone,
                a.city,
                a.postalcode,
                c.modifieddate,
                ROW_NUMBER() OVER (
                    PARTITION BY c.accountnumber
                    ORDER BY c.modifieddate ASC
                ) AS rn
            FROM sales.customer c
            LEFT JOIN sales.store s ON c.storeid = s.businessentityid
            LEFT JOIN person.businessentityaddress bea ON s.businessentityid = bea.businessentityid
            LEFT JOIN person.address a ON bea.addressid = a.addressid
            LEFT JOIN person.businessentitycontact bec ON s.businessentityid = bec.businessentityid
            LEFT JOIN person.personphone p ON bec.personid = p.businessentityid
            WHERE c.personid IS NULL
        ),
        orders AS (
            SELECT  
                c.storeid,
                EXTRACT(MONTH FROM MAX(sh.orderdate)) AS ordermonth,
                EXTRACT(YEAR  FROM MIN(sh.orderdate)) AS firstorderyear,
                EXTRACT(YEAR  FROM MAX(sh.orderdate)) AS lastorderyear
            FROM sales.salesorderheader sh 
            INNER JOIN sales.customer c ON sh.customerid = c.customerid
            GROUP BY c.storeid
        )
        SELECT 
            r.*,
            o.ordermonth,
            o.firstorderyear,
            o.lastorderyear
        FROM ranked r
        LEFT JOIN orders o ON r.storeid = o.storeid
        WHERE r.rn = 1;
    '''
    if fecha:
        q_base += " WHERE c.modifieddate >= :fecha;"
    else:
        q_base += ";"

    try:
        with source_engine.connect() as conn:
            return pd.read_sql(text(q_base), conn, params={"fecha": fecha} if fecha else None)
    except Exception as e:
        print(f"Error en extract_reseller: {e}")
        return pd.DataFrame()