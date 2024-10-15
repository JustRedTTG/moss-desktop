from typing import TYPE_CHECKING
import jwt
from pycparser.ply.yacc import token

from rm_api.storage.v3 import get_documents_api_root

if TYPE_CHECKING:
    from rm_api import API
    from rm_api.models import *

SYNC_ROOT_URL = "{0}sync/v4/root"


def get_root(api: 'API') -> dict:
    return api.session.get(
        SYNC_ROOT_URL.format(api.document_storage_uri),
    ).json()


def get_documents_new_sync(api: 'API', progress):
    root = get_root(api)['hash']
    return get_documents_api_root(api, progress, root)


def handle_new_api_steps(api: 'API'):
    token_info = jwt.decode(api.token, algorithms=["HS256"], options={"verify_signature": False})
    tectonic = token_info['tectonic']
    api.document_storage_uri = f'https://{tectonic}.tectonic.remarkable.com/'
