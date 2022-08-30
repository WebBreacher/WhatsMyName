from enum import Enum


class OutputFormat(str, Enum):
    CSV = 'csv'
    JSON = 'json'
    TABLE = 'table'

