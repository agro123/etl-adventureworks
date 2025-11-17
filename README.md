# CS_etl_py
ETL en Python para la migración, transformación y carga de datos desde **AdventureWorks 2022 (SQL Server)** hacia **PostgreSQL**.

## Descripción
Este proyecto implementa un proceso ETL que:

1. **Extrae** datos desde la base de datos de ejemplo **AdventureWorks2022** restaurada en SQL Server.  
2. **Transforma** los datos utilizando Python (limpieza, normalización, conversiones de tipos, etc.).  
3. **Carga** los datos procesados en una base de datos **PostgreSQL** para su análisis o uso posterior.

El objetivo es facilitar la migración y estandarización de datos entre ambas plataformas.

---

## Requisitos Previos
- Python 3.8+  
- SQL Server 2022 (solo para extracción)  
- PostgreSQL 12+  
- SQL Server Management Studio (SSMS)  
- ODBC Driver: **ODBC Driver 17 for SQL Server**

---

## Instalación del Entorno

### 1. Crear entorno virtual
```bash
python3 -m venv my_env


source my_env/bin/activate     # Linux/Mac
.\my_env\Scripts\activate      # Windows
