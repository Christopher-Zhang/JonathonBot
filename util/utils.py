import os
import json

def write_to_file(data: dict, file_name: str):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

def read_from_file(file_name: str):
    if os.path.exists(file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)
    else:
        data = None
    return data

def rotate_list(list: list, n: int):
    list = list[n:] + list[:n]
    return list