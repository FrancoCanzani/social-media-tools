import os


def remove_file(path: str):
    """Function to remove a file"""
    if os.path.exists(path):
        os.remove(path)
