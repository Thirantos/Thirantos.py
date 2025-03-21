import sqlalchemy

type Row = dict[str, any]
type QueryResult = list[Row]
type Clause = tuple[sqlalchemy.Executable, dict[str, any]]
type Clauses = list[Clause]
type ClauseType = Clauses | Clause | sqlalchemy.Executable

def as_array(result: sqlalchemy.CursorResult) -> QueryResult:
    """
    Converts a SQLAlchemy CursorResult into a list of dictionaries.

    Args:
        result (sqlalchemy.CursorResult): The result of a SQLAlchemy query.

    Returns:
        QueryResult: A list of dictionaries representing the query result.
    """
    array: QueryResult = []
    for row in result.mappings().all():
        row_dict: Row = {}
        for key in result.mappings().keys():

            # handling for special types
            match type(row[key]).__name__:
                case "memoryview":
                    row_dict[key] = row.get(key).tobytes().decode()
                case _:

                    row_dict[key] = row.get(key)
        array.append(row_dict)
    return array


def get_array(con: sqlalchemy.Connection, c: any) -> QueryResult:
    """
    Executes a query and returns the result as an array.

    Args:
        con (sqlalchemy.Connection): The database connection.
        c (any): The query to execute.

    Returns:
        QueryResult: The result of the query as a list of dictionaries.
    """
    return as_array(con.execute(c))


def _ensure_clauses(clause: ClauseType) -> Clauses:
    """
    Ensures the clause is in the form of a list of clauses.

    Args:
        clause (ClauseType): The clause to ensure.

    Returns:
        Clauses: A list of clauses.
    """
    if isinstance(clause, sqlalchemy.Executable):
        return [(clause, {})]
    if isinstance(clause, tuple) and len(clause) == 2 and isinstance(clause[0], sqlalchemy.Executable):
        return [clause]
    return list(clause) if isinstance(clause, list) else [clause]

class Database:
    """
    A class to manage database connections and execute queries.

    Attributes:
        sqlEngine (sqlalchemy.Engine): The SQLAlchemy engine for the database.
    """
    def __init__(self, sqluri: str = 'sqlite:///database.db'):
        """
        Initializes the Database class with a given SQL URI.

        Args:
            sqluri (str): The URI of the database.
        """
        self.sqlEngine = sqlalchemy.create_engine(sqluri, echo=True)

    def _exec(self, clauses: ClauseType, commit: bool = False) -> list[QueryResult]:
        """
        Executes a list of clauses and optionally commits the transaction.

        Args:
            clauses (ClauseType): The clauses to execute.
            commit (bool): Whether to commit the transaction.

        Returns:
            list[QueryResult]: The results of the executed clauses.
        """
        results: list[QueryResult] = []
        clauses = _ensure_clauses(clauses)

        with self.sqlEngine.connect() as connection:
            for clause in clauses:
                results.append(as_array(connection.execute(clause[0], clause[1])))
            if commit:
                connection.commit()

        return results
