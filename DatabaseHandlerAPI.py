import sqlite3
import os
import shutil

def create_database():

    if os.path.exists("_temp_.db"):
        os.remove("_temp_.db")

    conn = sqlite3.connect("_temp_.db")

def create_table(name: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"""CREATE TABLE \"{name}\" (
                        script_name text,
                        script_path text,
                        venv text,
                        venv_path text,
                        thumbnail_path text)""")

    conn.commit()
    conn.close()

def add_script(table: str, script_name: str, script_path: str, thumbnail_path="icons/default_thumbnail.jpg", venv=str, venv_path=""):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"""INSERT INTO \"{table}\" (script_name, script_path, venv, venv_path, thumbnail_path)
            VALUES (?, ?, ?, ?, ?)""", (script_name, script_path, venv, venv_path, thumbnail_path))

    conn.commit()
    conn.close()

def delete_script(table: str, script_name: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"DELETE FROM \"{table}\" WHERE script_name=\"{script_name}\"")

    conn.commit()
    conn.close()

def delete_table(table: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"""DROP TABLE \"{table}\"""")

    conn.commit()
    conn.close()

def read_to_run_script(table: str, script_name: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"SELECT script_path, venv, venv_path FROM \"{table}\" WHERE script_name=\"{script_name}\"")
    script_info = c.fetchone()

    conn.commit()
    conn.close()

    return script_info

def read_to_run_all_scripts(table: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"SELECT script_path, venv, venv_path FROM \"{table}\"")
    script_info = c.fetchall()

    conn.commit()
    conn.close()

    return script_info

def read_all_scripts(table: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"SELECT script_name, thumbnail_path FROM \"{table}\"")
    script_info = c.fetchall()
    conn.commit()
    conn.close()

    return script_info

def read_all_tables():
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"SELECT name from sqlite_master where type=\"table\"")
    tables = c.fetchall()

    scripts = []

    for table in tables:
        c.execute(f"SELECT script_name FROM \"{table[0]}\"")
        scripts.append(c.fetchall())

    conn.commit()
    conn.close()

    return tables, scripts

def get_script_info(table: str, script: str):
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"SELECT * FROM \"{table}\" WHERE script_name=\"{script}\"")
    script_info = c.fetchone()

    conn.commit()
    conn.close()

    return script_info

def save_all(file_path: str):
    original = os.path.abspath("_temp_.db")
    target = file_path
    shutil.copyfile(original, target)

def read_all():
    conn = sqlite3.connect("_temp_.db")
    c = conn.cursor()

    c.execute(f"SELECT name from sqlite_master where type=\"table\"")
    tables = c.fetchall()

    scripts = []

    for table in tables:
        c.execute(f"SELECT * FROM \"{table[0]}\"")
        scripts.append(c.fetchall())

    conn.commit()
    conn.close()

    return tables, scripts