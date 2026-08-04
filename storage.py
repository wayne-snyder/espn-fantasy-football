import json
import os
import sqlite3

import pandas as pd

from config import OUTPUT_DIRECTORY, DATABASE_NAME

DATABASE_DIRECTORY = "database"
EXPORTS_DIRECTORY = "exports"


def dump_json(data, season, view_name, output_dir=OUTPUT_DIRECTORY):
    """Writes a raw API response to output/{season}_{view_name}.json"""

    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, f"{season}_{view_name}.json")

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path


def write_csv(df, filename, exports_dir=EXPORTS_DIRECTORY):
    """Writes a polished DataFrame to exports/{filename}"""

    os.makedirs(exports_dir, exist_ok=True)

    path = os.path.join(exports_dir, filename)

    df.to_csv(path, index=False)

    return path


def write_excel(dataframes, filename, exports_dir=EXPORTS_DIRECTORY):
    """
    Writes multiple DataFrames to one workbook, one sheet each.
    dataframes: dict of {sheet_name: DataFrame}
    """

    os.makedirs(exports_dir, exist_ok=True)

    path = os.path.join(exports_dir, filename)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return path


def get_db_connection(database_dir=DATABASE_DIRECTORY, db_name=DATABASE_NAME):

    os.makedirs(database_dir, exist_ok=True)

    path = os.path.join(database_dir, db_name)

    return sqlite3.connect(path)


def write_to_db(conn, df, table_name):
    """Replaces table_name with the contents of df on every run."""

    df.to_sql(table_name, conn, if_exists="replace", index=False)
