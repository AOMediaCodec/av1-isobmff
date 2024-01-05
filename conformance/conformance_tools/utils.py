import hashlib
import json
import os
import subprocess


def execute_cmd(cmd_string):
    """Execute command"""
    res = subprocess.run(cmd_string.split(), capture_output=True)
    return res


def make_dirs_from_path(dir_or_file_path):
    """
    Make all directories from a path.
    If a path includes a filename with extension, ignore the filename.
    """
    _base, ext = os.path.splitext(dir_or_file_path)
    if ext == '' and not os.path.exists(dir_or_file_path):
        os.makedirs(dir_or_file_path)
    else:
        dir_path, _filename = os.path.split(dir_or_file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def compute_file_md5(file_path):
    """Compute md5 hash of a file"""
    with open(file_path, 'rb') as file:
        file_hash = hashlib.md5()
        while chunk := file.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def dump_to_json(out_file, obj):
    """dump json"""
    with open(out_file, 'w', encoding='utf-8') as file:
        json.dump(obj, file, indent=2)


def read_json(in_file):
    """read json"""
    with open(in_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data
