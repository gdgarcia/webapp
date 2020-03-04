import sqlite3
from os import path
from collections.abc import MutableMapping

import webapp


def create_db(db_name, data=None, overwrite=False):

    success = False

    if path.isfile(db_name) and not overwrite:
        raise RuntimeError("Uma DB com o nome {1} ja existe no diretorio {0}. "
                           " Para sobreescrever, faca overwrite=True "
                           "".format(*path.split(db_name)))

    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        for create_statement in _create_statements().values():
            cur.execute(create_statement)
        conn.commit()
        success = True
    
    if data is not None:
        write_db(db_name, data)

    return db_name, success 


def write_db(db_name, data):

    if not path.isfile(db_name):
        raise RuntimeError("A DB {1} nao existe no diretorio {0}. " 
                           "Para criar uma nova DB, use a funcao "
                           "especifica.".format(*path.split(db_name)))
    
    try:
        with sqlite3.connect(db_name) as conn:
            _write_data_to_db(conn, data)
    except sqlite3.Error:
        pass


def read_db(db_name, tables=None):

    success = False

    if not path.isfile(db_name):
        raise RuntimeError("DB {1} nao existente no diretorio {0}. Para "
                           "criar, use a funcao webapp.create_db. "
                           "".format(*path.split(db_name)))

    try:
        with sqlite3.connect(db_name) as conn:
            db_data = _get_data_from_db(conn, tables)

    except sqlite3.Error:
        raise
    else:
        success = True

    return db_data, success


def _write_data_to_db(conn, data):

    cur = conn.cursor()

    write_statements = _write_statements()
    tables = set(data.keys())

    if tables.issubset(write_statements.keys()):
        tables = tables.intersection(write_statements.keys())
    else:
        raise UserWarning("Os dados para escrita na DB contêm outros campos "
                          "além de 'ORIG', 'DEST', 'COST', 'RES'.")


    for table in tables:
        flat_items = _get_flat_items(data[table])
        for item in flat_items:
            cur.execute(write_statements[table], item)
            conn.commit()

    return tables


def _get_data_from_db(conn, tables=None):

    db_data = {}
    read_statements = _read_statements()
    cur = conn.cursor()

    if tables is None:
        tables = read_statements.keys()
    else:
        if isinstance(tables, str):
            tables = {tables}
        else:
            tables = set(tables)
        
        if not tables.issubset(read_statements.keys()):
            raise UserWarning("As tabelas para leitura da DB contêm outros "
                              "campos além de 'ORIG', 'DEST', 'COST', 'RES'.")
        else:
            tables = tables.intersection(set(read_statements.keys()))

    for table in tables:
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
