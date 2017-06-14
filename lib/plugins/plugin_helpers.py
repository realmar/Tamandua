"""Helper functions which help the user to write plugins."""

import re
from typing import Union, List, Callable

from ..constants import DPHYS_DOMAINS

dphysDomainRegexps = [re.compile(r'@' + x + r'$', re.X) for x in DPHYS_DOMAINS]


def is_any_dphys_subdomain(d: str) -> bool:
    for regex in dphysDomainRegexps:
        if regex.search(d):
            return True

    return False


def check_value(v: Union[List[str], str], predicate: Callable[[str], bool]):
    if v is None:
        return False

    if isinstance(v, list):
        for i in v:
            if predicate(i):
                return True
        return False
    else:
        return predicate(v)


def add_tag(data: dict, name: str):
    if not isinstance(data.get('tags'), list):
        data['tags'] = [name]
    else:
        if name not in data['tags']:
            data['tags'].append(name)


def get_tag(data: dict, name: str):
    return data.get(name)