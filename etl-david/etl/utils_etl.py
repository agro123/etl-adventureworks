from sqlalchemy import Engine, text


def new_data(conne: Engine) -> bool:
    queryo = text("select saved from dim_date order;")
    with conne.connect() as con:
        try:
            rs1 = con.execute(queryo)

            lastupdate = rs1.fetchone()

            if lastupdate is None:
                return True

            print(
                f"""No hay datos nuevos desde la ultima fecha de carga {lastupdate}"""
            )
            return False
        except Exception as e:
            print("[*]", e)
            return False
