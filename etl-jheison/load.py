import pandas as pd
from sqlalchemy.engine import Engine


def load_table(
    df: pd.DataFrame,
    engine: Engine,
    table_name: str
) -> None:
    """
    Carga un DataFrame en una tabla del datamart de Jheison.
    Usa if_exists='replace' para simplificar el proyecto.
    """
    if df is None or df.empty:
        print(f"⚠️  Tabla {table_name}: DataFrame vacío, no se carga.")
        return

    print(f"➡️  Cargando {len(df)} filas en {table_name}...")
    df.to_sql(
        table_name,
        engine,
        schema="public",
        if_exists="replace",
        index=False
    )
    print(f"✅ Tabla {table_name} cargada.")
