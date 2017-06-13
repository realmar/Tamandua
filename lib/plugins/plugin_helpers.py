"""Helper functions which help the user to write plugins."""


def add_tag(data: dict, name: str):
    if not isinstance(data.get('tags'), list):
        data['tags'] = [name]
    else:
        if name not in data['tags']:
            data['tags'].append(name)


def get_tag(data: dict, name: str):
    return data.get(name)