import os
import sqlite3
import sys

import pandas as pd

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

from config import DATABASE_NAME  # noqa: E402


DATABASE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "database"
)

REPORTS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "exports",
    "reports"
)



def get_connection():

    path = os.path.join(
        DATABASE_DIR,
        DATABASE_NAME
    )

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No database found at {path}. Run export.py first."
        )

    return sqlite3.connect(path)



def load_table(table_name):

    conn = get_connection()

    df = pd.read_sql(
        f"SELECT * FROM {table_name}",
        conn
    )

    conn.close()

    return df



def save_table(df, table_name):

    conn = get_connection()

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(
        f"  -> Database table updated: {table_name} ({len(df)} rows)"
    )



def save_report(df, filename):

    os.makedirs(
        REPORTS_DIR,
        exist_ok=True
    )

    path = os.path.join(
        REPORTS_DIR,
        filename
    )

    df.to_csv(
        path,
        index=False
    )

    print(
        f"  -> {path}  ({len(df)} rows)"
    )

    return path