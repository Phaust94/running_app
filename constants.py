import os

__all__ = [
    "DB_PATH",
    "RAW_DATA_TNAME",
]

DB_PATH = os.path.abspath(os.path.join(
    __file__,
    '..',
    'data',
    'db.sqlite'
))

RAW_DATA_TNAME = "raw_data"
