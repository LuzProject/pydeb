# module imports
from pathlib import Path
from os import environ, path, walk
from shutil import which
from typing import Union


def resolve_path(path: str) -> Union[Path, list]:
    """Resolve a Path from a String."""
    # format env vars in path
    if "$" in str(path):
        path = format_path(path)
    # get path
    p = Path(path)
    # handle globbing
    if "*" in str(path):
        p = Path(path)
        parts = p.parts[1:] if p.is_absolute() else p.parts
        return list(Path(p.root).glob(str(Path("").joinpath(*parts))))
    # return path
    return p


def chained_dict_get(dictionary, key: str):
    """Get a value nested in a dictionary by its nested path.

    :param dict dictionary: Dictionary to operate on.
    :param str key: The key to get.
    :return: The value of the key.
    """
    value_path = key.split(".")
    dict_chain = dictionary
    while value_path:
        try:
            dict_chain = dict_chain.get(value_path.pop(0))
        except AttributeError:
            return None
    return dict_chain


def get_filepaths(directory):
    file_paths = []

    for root, directories, files in walk(directory):
        for filename in files:
            filepath = path.join(root.replace(directory, "") + "/" + filename)
            file_paths.append(filepath)

    return file_paths


def format_path(file: str) -> str:
    """Format a path that contains environment variables.

    :param str file: Path to format.
    :return: The formatted path.
    """
    new_file = ""
    for f in file.split("/"):
        if f.startswith("$"):
            new_file += environ.get(f[1:]) + "/"
        else:
            new_file += f + "/"
    return new_file


def cmd_in_path(cmd: str) -> Union[None, str]:
    """Check if command is in PATH"""
    path = which(cmd)

    if path is None:
        return None

    return resolve_path(path)
