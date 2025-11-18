import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from utils import check_db_connection, print_df_info
from extract import (
    extract_dim_product,
    extract_dim_reseller,
    extract_dim_sales_territory,
    extract_dim_employee,
    extract_dim_currency,
    extract_dim_promotion,
    extract_dim_date,
    extract_fact_reseller_sales,
)
from transform import (
    transform_dim_product,
    transform_dim_reseller,
    transform_dim_sales_territory,
    transform_dim_employee,
    transform_dim_currency,
    transform_dim_promotion,
    transform_dim_date,
    transform_fact_reseller_sales,
)
from load import load_table


def make_engine(cfg: dict) -> Engine:
    url = (
        f"{cfg['drivername']}://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    )
    return create_engine(url)


def main() -> None:
    # 1. Leer configuración
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)

    src_cfg = config["ORIGEN_DW"]   # origen: DW que tienes en adventureWorksOLTP-full
    tgt_cfg = config["DM_JHEISON"]  # destino: tu datamart

    src_engine = make_engine(src_cfg)
    tgt_engine = make_engine(tgt_cfg)

    if not check_db_connection(src_engine, "ORIGEN_DW") or not check_db_connection(tgt_engine, "DM_JHEISON"):
        print("❌ No se pudo conectar a alguna base. Saliendo.")
        return

    # ===========================
    #  EXTRACCIÓN
    # ===========================
    print("\n===== EXTRACCIÓN RESELLER SALES =====")
    dim_product_raw = extract_dim_product(src_engine)
    dim_reseller_raw = extract_dim_reseller(src_engine)
    dim_st_raw = extract_dim_sales_territory(src_engine)
    dim_emp_raw = extract_dim_employee(src_engine)
    dim_curr_raw = extract_dim_currency(src_engine)
    dim_promo_raw = extract_dim_promotion(src_engine)
    dim_date_raw = extract_dim_date(src_engine)
    fact_reseller_raw = extract_fact_reseller_sales(src_engine)

    # ===========================
    #  TRANSFORMACIÓN
    # ===========================
    print("\n===== TRANSFORMACIÓN RESELLER SALES =====")
    dim_product = transform_dim_product(dim_product_raw)
    dim_reseller = transform_dim_reseller(dim_reseller_raw)
    dim_st = transform_dim_sales_territory(dim_st_raw)
    dim_emp = transform_dim_employee(dim_emp_raw)
    dim_curr = transform_dim_currency(dim_curr_raw)
    dim_promo = transform_dim_promotion(dim_promo_raw)
    dim_date = transform_dim_date(dim_date_raw)
    fact_reseller = transform_fact_reseller_sales(fact_reseller_raw)

    print_df_info(dim_product, "DimProduct")
    print_df_info(dim_reseller, "DimReseller")
    print_df_info(fact_reseller, "FactResellerSales")

    # ===========================
    #  CARGA
    # ===========================
    print("\n===== CARGA RESELLER SALES =====")
    load_table(dim_product, tgt_engine, "dm_dimproduct")
    load_table(dim_reseller, tgt_engine, "dm_dimreseller")
    load_table(dim_st, tgt_engine, "dm_dimsalesterritory")
    load_table(dim_emp, tgt_engine, "dm_dimemployee")
    load_table(dim_curr, tgt_engine, "dm_dimcurrency")
    load_table(dim_promo, tgt_engine, "dm_dimpromotion")
    load_table(dim_date, tgt_engine, "dm_dimdate")
    load_table(fact_reseller, tgt_engine, "dm_factresellersales")

    print("\n✅ ETL de Reseller Sales (Jheison) finalizado.")


if __name__ == "__main__":
    main()
