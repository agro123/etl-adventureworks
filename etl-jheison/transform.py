import pandas as pd


def _choose_key(df: pd.DataFrame, candidates: list[str]) -> str:
    """
    Busca una columna clave en el DataFrame ignorando mayúsculas/minúsculas.
    Si no encuentra ninguna, devuelve la primera columna del DF.
    """
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        cand_lower = cand.lower()
        if cand_lower in lower_map:
            return lower_map[cand_lower]
    # Fallback: primera columna
    return df.columns[0]


# ==============================
#  DIMENSIONES
# ==============================

def transform_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["ProductKey", "ProductAlternateKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


def transform_dim_reseller(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["ResellerKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


def transform_dim_sales_territory(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["SalesTerritoryKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


def transform_dim_employee(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["EmployeeKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


def transform_dim_currency(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["CurrencyKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


def transform_dim_promotion(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["PromotionKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


def transform_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    df = df.copy()
    key_col = _choose_key(df, ["DateKey"])
    df = df.drop_duplicates(subset=[key_col])
    return df.where(pd.notnull(df), None)


# ==============================
#  HECHOS
# ==============================

def transform_fact_reseller_sales(fact_df: pd.DataFrame) -> pd.DataFrame:
    """
    Maneja nombres de columnas ignorando mayúsculas/minúsculas.
    Calcula:
    - SalesAmount (si no existe)
    - TotalProductCost (si no existe)
    - Profit (si puede)
    """
    if fact_df is None or fact_df.empty:
        return fact_df

    df = fact_df.copy()
    lower_map = {c.lower(): c for c in df.columns}

    def col(name: str) -> str | None:
        """Devuelve el nombre real de la columna si existe (case-insensitive)."""
        return lower_map.get(name.lower())

    order_qty_col = col("OrderQuantity")
    unit_price_col = col("UnitPrice")
    extended_amount_col = col("ExtendedAmount")
    discount_amount_col = col("DiscountAmount")
    product_std_cost_col = col("ProductStandardCost")
    total_product_cost_col = col("TotalProductCost")
    sales_amount_col = col("SalesAmount")

    # SalesAmount
    if sales_amount_col is None:
        if extended_amount_col and discount_amount_col:
            df["SalesAmount"] = df[extended_amount_col] - df[discount_amount_col]
            sales_amount_col = "SalesAmount"

    # TotalProductCost
    if total_product_cost_col is None:
        if order_qty_col and product_std_cost_col:
            df["TotalProductCost"] = df[order_qty_col] * df[product_std_cost_col]
            total_product_cost_col = "TotalProductCost"

    # Profit
    if sales_amount_col and total_product_cost_col:
        df["Profit"] = df[sales_amount_col] - df[total_product_cost_col]

    return df.where(pd.notnull(df), None)
