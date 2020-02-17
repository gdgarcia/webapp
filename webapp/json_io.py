import json


def json_reader(file):

    with open(file, 'r') as fp:
        json_dict = json.load(fp)

    return json_dict


def json_writer(data, file, indent=None):

    with open(file, 'w') as fp:
        json.dump(data, fp, indent=indent)
