import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


if __name__ == '__main__':
    conn = create_connection(r"test.db")
    if conn is not None:
        sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS alarms (
                                        id integer PRIMARY KEY,
                                        type text NOT NULL,
                                        optionalMessage text,
                                        creationDate text NOT NULL,
                                        alarmDate text NOT NULL
                                    );"""

        create_table(conn, sql_create_tasks_table)
    else:
        print("Error connecting to db")
