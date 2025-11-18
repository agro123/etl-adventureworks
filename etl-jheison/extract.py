import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


# ==============================
#  DIMENSIONES RESELLER SALES
# ==============================

def extract_dim_product(engine: Engine) -> pd.DataFrame:
    """Extrae DimProduct desde el DW."""
    query = text("SELECT * FROM public.dimproduct;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def extract_dim_reseller(engine: Engine) -> pd.DataFrame:
    """Extrae DimReseller."""
    query = text("SELECT * FROM public.dimreseller;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def extract_dim_sales_territory(engine: Engine) -> pd.DataFrame:
    """Extrae DimSalesTerritory."""
    query = text("SELECT * FROM public.dimsalesterritory;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def extract_dim_employee(engine: Engine) -> pd.DataFrame:
    """Extrae DimEmployee."""
    query = text("SELECT * FROM public.dimemployee;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def extract_dim_currency(engine: Engine) -> pd.DataFrame:
    """Extrae DimCurrency."""
    query = text("SELECT * FROM public.dimcurrency;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def extract_dim_promotion(engine: Engine) -> pd.DataFrame:
    """Extrae DimPromotion si existe."""
    query = text("SELECT * FROM public.dimpromotion;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def extract_dim_date(engine: Engine) -> pd.DataFrame:
    """Extrae DimDate (por si lo quieres usar luego)."""
    query = text("SELECT * FROM public.dimdate;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ==============================
#  HECHOS RESELLER SALES
# ==============================

def extract_fact_reseller_sales(engine: Engine) -> pd.DataFrame:
    """Extrae FactResellerSales completa desde el DW."""
    query = text("SELECT * FROM public.factresellersales;")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)
