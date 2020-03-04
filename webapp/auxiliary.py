import glob
from os import path, remove

from collections.abc import MutableMapping

from webapp import __path__ as web_path, db_io, json_io
from webapp.opt import run_jump

DEFAULT_DIR = path.join(path.dirname(web_path[0]), 'estudos')


def get_studies_names(sdir=DEFAULT_DIR):

    names = []

    for db in glob.iglob(path.join(sdir, '*.db')):
        file_name, _ = path.splitext(path.basename(db))
        names.append(file_name)

    return names


def db_name_from_study_name(study_name, sdir=DEFAULT_DIR):

    return path.join(sdir, ''.join((study_name, '.db')))


def buffer_name_from_study_name(study_name, sdir=DEFAULT_DIR):

    return path.join(sdir, ''.join((study_name, '.json')))


def create_study(study_name, json_file=None, sdir=DEFAULT_DIR):

    db_name = db_name_from_study_name(study_name, sdir)

    if json_file is None:
        data = None
    else:
        data = json_io.json_reader(json_file)
    
    db_name, success = db_io.create_db(db_name, data)

    return db_name, success, data


def update_study(study_name, data, sdir=DEFAULT_DIR):

    db_name = db_name_from_study_name(study_name, sdir)

    if isinstance(data, MutableMapping):
        dict_data = dict(data)
    elif isinstance(data, str) and path.isfile(data):
        dict_data = json_io.json_reader(data)
    else:
        raise UserWarning("data deve ser um arquivo JSON ou um dicionario"
                          " python com os campos de entrada adequados.")
    
    db_io.write_db(db_name, dict_data)

    return dict_data


def run_study(study_name, sdir=DEFAULT_DIR, write_ans_to_db=True,
              delete_buffer_file=True):

    db_name = db_name_from_study_name(study_name, sdir)
    data, _ = db_io.read_db(db_name, tables=["ORIG", "DEST", "COST"])

    buffer_file = buffer_name_from_study_name(study_name, sdir)
    json_io.json_writer(data, buffer_file)

    res = run_jump._call_jump(buffer_file)

    if write_ans_to_db:
        update_study(study_name, {"RES": res[2]}, sdir)
    
    if delete_buffer_file:
        remove(buffer_file)

    return res
