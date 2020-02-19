import sqlite3
from os import path
from collections.abc import MutableMapping

import webapp


DEFAULT_DIR = path.join(path.dirname(webapp.__path__[0]), 'estudos')


def create_db(name, db_dir=DEFAULT_DIR, data=None, overwrite=False):

    success = False
    db_name = path.join(db_dir, name)

    if path.isfile(db_name) and not overwrite:
        raise RuntimeError("Uma DB com o nome {} ja existe no diretorio {}. "
                           " Para sobreescrever, faca overwrite=True "
                           "".format(name, db_dir))

    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        for create_statement in _create_statements().values():
            cur.execute(create_statement)
        conn.commit()
        success = True

    return name, db_dir, success 


def write_db(name, data, table=None, db_dir=DEFAULT_DIR):

    db_name = path.join(db_dir, name)
    if not path.isfile(db_name):
        raise RuntimeError("A DB {} nao existe no diretorio {}. " 
                           "Para criar uma nova DB, use a funcao "
                           "especifica.".format(name, db_dir))
    
    try:
        with sqlite3.connect(db_name) as conn:
            _write_data_to_db(conn, data, table)
    except sqlite3.Error:
        pass


def read_db(name, db_dir=DEFAULT_DIR, table=None):

    success = False
    db_name = path.join(db_dir, name)

    if not path.isfile(db_name):
        raise RuntimeError("DB {} nao existente no diretorio {}. Para criar, "
                           "use a funcao webapp.create_db. "
                           "".format(db_name, db_dir))

    try:
        with sqlite3.connect(db_name) as conn:
            db_data = _get_data_from_db(conn, table)

    except sqlite3.Error:
        raise
    else:
        success = True

    return db_data, success


def _write_data_to_db(conn, data, table=None):

    write_statements = _write_statements()

    cur = conn.cursor()
    for table in write_statements:
        flat_items = _get_flat_items(data[table])
        for item in flat_items:
            cur.execute(write_statements[table], item)
            conn.commit()


def _get_data_from_db(conn, table=None):

    db_data = {}
    read_statements = _read_statements()
    cur = conn.cursor()

    if table is None:
        for table_name in read_statements:
            cur.execute(read_statements[table_name])
            db_data[table_name] = _dict_from_flat_data(cur.fetchall())
    else:
        cur.execute(read_statements[table])
        db_data[table] = _dict_from_flat_data(cur.fetchall())

    return db_data


def _create_statements():

    create_statements = {
        "ORIG": ("""
            CREATE TABLE IF NOT EXISTS ORIG (
                name TEXT PRIMARY KEY NOT NULL,
                supply REAL NOT NULL
            );
        """),

        "DEST": ("""
            CREATE TABLE IF NOT EXISTS DEST (
                name TEXT PRIMARY KEY NOT NULL,
                demand REAL NOT NULL
            );
        """),

        "COST": ("""
            CREATE TABLE IF NOT EXISTS COST (
                orig TEXT NOT NULL,
                dest TEXT NOT NULL,
                cost REAL NOT NULL,
                FOREIGN KEY (orig) references ORIG(name),
                FOREIGN KEY (dest) references DEST(name),
                PRIMARY KEY (orig, dest)
            );
        """),

        "RES": ("""
            CREATE TABLE IF NOT EXISTS RES (
                orig TEXT NOT NULL,
                dest TEXT NOT NULL,
                trans REAL NOT NULL,
                FOREIGN KEY (orig) references ORIG(name),
                FOREIGN KEY (dest) references DEST(name),
                PRIMARY KEY (orig, dest)
            )
        """)
    }

    return create_statements


def _read_statements():

    read_statements = {
        "ORIG": "SELECT * FROM ORIG",
        "DEST": "SELECT * FROM DEST",
        "COST": "SELECT * FROM COST",
        "RES": "SELECT * FROM RES"
    }

    return read_statements


def _write_statements():

    write_statements = {
        "ORIG": ("""
            INSERT INTO ORIG (name, supply) VALUES (?, ?);
        """),
        "DEST": ("""
            INSERT INTO DEST (name, demand) VALUES (?, ?);
        """),
        "COST": ("""
            INSERT INTO COST (orig, dest, cost) VALUES (?, ?, ?);
        """),
        "RES": ("""
            INSERT INTO RES (orig, dest, trans) VALUES (?, ?, ?);
        """)
    }

    return write_statements


def _get_flat_items(data):
    flatten_data = list()
    for k, v in data.items():
        if not isinstance(v, MutableMapping):
            flatten_data.append((k, v))
        else:
            for v_key, v_val in v.items():
                flatten_data.append((k, v_key, v_val))

    return flatten_data


def _dict_from_flat_data(flat_data):

    dict_data = {}

    for data in flat_data:
        if len(data) == 2:
            dict_data[data[0]] = data[1]
        else:
            if data[0] in dict_data:
                dict_data[data[0]].update({data[1]: data[2]})
            else:
                dict_data[data[0]] = {data[1]: data[2]}

    return dict_data
