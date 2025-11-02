import pandas as pd
from sqlalchemy import text, Engine

def load_table(
    df: pd.DataFrame,
    target_engine: Engine,
    table_name: str,
    key_columns: list[str],
    schema: str = "public",
) -> None:
    """
    :param df : pd.DataFrame
        DataFrame transformado que se desea cargar.
    :param target_engine : Engine
        Conexión SQLAlchemy al destino (OLAP).
    :param table_name : str
        Nombre de la tabla destino.
    :param key_columns : list[str]
        Lista de columnas que identifican un registro único.
    :param schema : str
        Esquema del DW. Por defecto 'public'.
    """
    if df.empty:
        print(f"No hay datos para cargar en {schema}.{table_name}")
        return

    try:
        # 1 btener las claves existentes del DW
        cols_str = ", ".join(key_columns)
        query = text(f"SELECT {cols_str} FROM {schema}.{table_name}")
        with target_engine.connect() as conn:
            existing = pd.read_sql(query, conn)
        
        # 2 Identificar duplicados
        merged = df.merge(existing, on=key_columns, how="left", indicator=True)
        new_rows = merged.loc[merged["_merge"] == "left_only", df.columns]

        if new_rows.empty:
            print(f"No hay registros nuevos para insertar en {schema}.{table_name}")
            return
        
        # 3 Insertar solo nuevos registros
        with target_engine.begin() as conn:
            new_rows.to_sql(
                name=table_name,
                con=conn,
                schema=schema,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=5000
            )
        print(f"{len(new_rows)} registros nuevos insertados en {schema}.{table_name}")
    
    except Exception as e:
        print(f"Error al cargar {schema}.{table_name}: {e}")
