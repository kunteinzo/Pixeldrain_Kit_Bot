import json

import requests
from requests.auth import HTTPBasicAuth

domain = 'https://pixeldrain.com/api/'


def parse_token(token):
    return HTTPBasicAuth('', token)


def post_file(name: str, file, token: str):
    return requests.post(
        f'{domain}file',
        auth=parse_token(token),
        files={'file': file, 'name': 'test.jpg'}
    )


def post_list(title: str, token: str, anonymous: bool = False, files: list[dict[str, str]] = None):
    return requests.post(
        f'{domain}list',
        data=json.dumps({
            "title": title,
            "anonymous": anonymous,
            "files": files
        }),
        auth=parse_token(token)
    )


def get_list(file_id, token):
    return requests.get(
        f'{domain}list/{file_id}',
        auth=parse_token(token)
    )


def put_file(name: str, file, token: str):
    return requests.put(
        f'{domain}file/{name}',
        auth=parse_token(token),
        files={'file': file}
    )


def get_file(file_id):
    return requests.get(f'{domain}file/{file_id}')


def get_file_info(file_id):
    return requests.get(f'{domain}file/{file_id}/info')


def get_user_files(token: str):
    return requests.get(
        f'{domain}user/files',
        auth=parse_token(token)
    )


def get_user_lists(token: str):
    return requests.get(
        f'{domain}user/lists',
        auth=parse_token(token)
    )


def delete_file(file_id: str, token: str):
    return requests.delete(
        f'{domain}/file/{file_id}',
        auth=parse_token(token)
    )
