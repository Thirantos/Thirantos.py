from sqlalchemy import *

ldict = list[dict[str, any]]


def as_array(result: CursorResult) -> ldict:
    l: list[dict[str, any]] = []
    for row in result.mappings().all():
        d: dict[str, any] = {}
        for key in result.mappings().keys():
            d[key] = row.get(key)
        l.append(d)
    return l


def get_array(con: Connection, c: any) -> ldict:
    return as_array(con.execute(c))

class Database:
    def __init__(self, sqluri: str = 'sqlite:///database.db'):
        self.sqlEngine = create_engine(sqluri, echo=True)

    def _exec(self, clauses: list[tuple[Executable, dict[str, any]]], commit: bool = false) -> list[
        list[dict[str, any]]]:
        result = []
        with self.sqlEngine.connect() as con:
            for clause in clauses:
                result.append(as_array(con.execute(clause[0], clause[1])))
            if commit:
                con.commit()

        return result
