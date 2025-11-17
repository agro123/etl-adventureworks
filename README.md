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
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

Si falta algún driver:
```bash
pip install psycopg2
pip install psycopg2-binary
```

---

## Restauración de AdventureWorks 2022 en SQL Server

1. Descargar **AdventureWorks2022.bak** desde Microsoft.  
2. Copiar el archivo a la carpeta de backups (ruta típica):  
   ```
   C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\Backup
   ```
3. Abrir **SSMS** y ejecutar:  
   - Clic derecho en *Bases de datos* → **Restaurar base de datos…**  
   - Seleccionar el archivo `.bak`  
   - Confirmar y restaurar  

---

## Configuración del Proyecto

### Archivo `config.yml`
Configura las conexiones de **origen (SQL Server)** y **destino (PostgreSQL)**:

```yaml
origen_sqlserver:
  drivername: mssql+pyodbc
  user: sa
  password: privado
  host: localhost
  port: 1433
  dbname: AdventureWorks2022
  odbc_driver: "ODBC Driver 17 for SQL Server"

destino_postgres:
  drivername: postgresql
  user: postgres
  password: privado
  host: localhost
  port: 5432
  dbname: adventureworks_migrado
```

---

## Ejecución del Pipeline ETL

Para ejecutar el pipeline:

```bash
python main.py
```

Este proceso realiza:

- Conexión al origen SQL Server  
- Extracción de datos  
- Transformaciones según los módulos del proyecto  
- Inserción en PostgreSQL  

---

## Estructura del Proyecto

```
CS_etl_py/
│── etl/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│── config.yml
│── requirements.txt
│── main.py
│── README.md
```
## Licencia
Puedes agregar una licencia estándar como MIT o Apache 2.0 según tus necesidades.
Puedes agregar una licencia estándar como MIT o Apache 2.0 según tus necesidades.
```
