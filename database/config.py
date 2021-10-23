from typing import Dict
from configparser import ConfigParser
from functools import lru_cache


@lru_cache()
def config(filename: str, section: str = 'postgresql') -> Dict[str, str]:
    parser = ConfigParser()
    parser.read(filename)

    result = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            result[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return result
