from sqlalchemy.engine import Engine
from sqlalchemy import Engine, text
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd


def check_db_connection(engine: Engine, entity: str = "") -> bool:
    """Check DB connection by executing a simple statement. Returns True if successful."""
    try:
        # use a lightweight query to validate the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"DB connection successful for {entity}")
        return True
    except Exception as e:
        # keep output simple; callers can decide how to handle
        print(f"DB connection failed for {entity}: {e}")
        return False

def parse_demographics(xml_data: str) -> dict:
    """Parses the XML 'demographics' column into a dictionary."""
    ns = {'ns': 'http://schemas.microsoft.com/sqlserver/2004/07/adventure-works/IndividualSurvey'}
    try:
        root = ET.fromstring(xml_data)
        return {
            "birthdate": root.findtext("ns:BirthDate", None, ns),
            "maritalstatus": root.findtext("ns:MaritalStatus", None, ns),
            "yearlyincome": root.findtext("ns:YearlyIncome", None, ns),
            "gender": root.findtext("ns:Gender", None, ns),
            "totalchildren": root.findtext("ns:TotalChildren", None, ns),
            "numberchildrenathome": root.findtext("ns:NumberChildrenAtHome", None, ns),
            "englisheducation": root.findtext("ns:Education", None, ns),
            "englishoccupation": root.findtext("ns:Occupation", None, ns),
            "houseownerflag": root.findtext("ns:HomeOwnerFlag", None, ns),
            "numbercarsowned": root.findtext("ns:NumberCarsOwned", None, ns),
            "commutedistance": root.findtext("ns:CommuteDistance", None, ns),
            "datefirstpurchase": root.findtext("ns:DateFirstPurchase", None, ns),
        }
    except Exception:
        return {
            "birthdate": None,
            "maritalstatus": None,
            "yearlyincome": None,
            "gender": None,
            "totalchildren": None,
            "numberchildrenathome": None,
            "englisheducation": None,
            "englishoccupation": None,
            "houseownerflag": None,
            "numbercarsowned": None,
            "commutedistance": None,
            "datefirstpurchase": None,
        }


def save_dataframe_to_csv(df: pd.DataFrame, filename: str, folder: str = "./output", index: bool = False, sep: str = ",") -> None:
    try:
        # Asegurar extensión y carpeta
        if not filename.endswith(".csv"):
            filename += ".csv"
        Path(folder).mkdir(parents=True, exist_ok=True)

        # Construir ruta completa
        filepath = Path(folder) / filename

        # Guardar CSV
        df.to_csv(filepath, index=index, sep=sep, encoding="utf-8")

        print(f"DataFrame guardado exitosamente en: {filepath.resolve()}")
    except Exception as e:
        print(f"Error al guardar CSV: {e}")

def has_new_fact_data(conne: Engine, fact_table: str, saved_col: str = "saved", date_col: str = "orderdate") -> bool:
    query_saved = text(f"SELECT MAX({saved_col}) FROM {fact_table};")
    query_date = text(f"SELECT MAX({date_col}) FROM {fact_table};")
    with conne.connect() as conn:
        try:
            lastupdate = conn.execute(query_saved).scalar()
            lastdate = conn.execute(query_date).scalar()
            if not lastupdate or not lastdate:
                return True
            return lastdate.date() > lastupdate
        except Exception as e:
            print(f"Error: {e}")
            return False


""" Se altero la tabla factinternetsales y factinternetsalesreason en la base de datos OLAP para incluir las columnas 'saved' y 'orderdate'"""