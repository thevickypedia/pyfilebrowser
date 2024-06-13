"""Module for database controls.

>>> Database

"""

import sqlite3
from typing import List, Tuple

from pydantic import FilePath

from pyfilebrowser.proxy import settings


class Database:
    """Creates a connection to the Database using sqlite3.

    >>> Database

    """

    def __init__(self, datastore: FilePath | str, timeout: int = 10):
        """Instantiates the class ``Database`` to create a connection and a cursor.

        Args:
            datastore: Name of the database file.
            timeout: Timeout for the connection to database.
        """
        self.connection = sqlite3.connect(
            database=datastore, check_same_thread=False, timeout=timeout
        )

    def create_table(self, table_name: str, columns: List[str] | Tuple[str]) -> None:
        """Creates the table with the required columns.

        Args:
            table_name: Name of the table that has to be created.
            columns: List of columns that has to be created.
        """
        with self.connection:
            cursor = self.connection.cursor()
            # Use f-string or %s as table names cannot be parametrized
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            )


database = Database(settings.env_config.database)
database.create_table("auth_errors", ["host", "block_until"])


def get_record(host: str) -> int | None:
    """Gets blocked epoch time for a particular host.

    Args:
        host: Host address.

    Returns:
        int:
        Returns the epoch time until when the host address should be blocked.
    """
    with database.connection:
        cursor = database.connection.cursor()
        state = cursor.execute(
            "SELECT block_until FROM auth_errors WHERE host=(?)", (host,)
        ).fetchone()
    if state and state[0]:
        return state[0]


def put_record(host: str, block_until: int) -> None:
    """Inserts blocked epoch time for a particular host.

    Args:
        host: Host address.
        block_until: Epoch time until when the host address should be blocked.
    """
    with database.connection:
        cursor = database.connection.cursor()
        cursor.execute(
            "INSERT INTO auth_errors (host, block_until) VALUES (?,?)",
            (host, block_until),
        )
        database.connection.commit()


def remove_record(host: str) -> None:
    """Deletes all records related to the host address.

    Args:
        host: Host address.
    """
    with database.connection:
        cursor = database.connection.cursor()
        cursor.execute("DELETE FROM auth_errors WHERE host=(?)", (host,))
        database.connection.commit()
