import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text


def check_db_connection(engine: Engine, name: str) -> bool:
    """Prueba la conexión a una base de datos."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Conexión OK a {name}")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a {name}: {e}")
        return False


def print_df_info(df: pd.DataFrame, name: str) -> None:
    """Imprime info básica de un DataFrame para debug."""
    print(f"\n====== {name} ======")
    if df is None:
        print("DataFrame es None")
        return
    print(f"Filas: {len(df)}")
    print(f"Columnas ({len(df.columns)}): {list(df.columns)}")
