import functools
from logging import (
    getLogger,
    INFO,
    StreamHandler,
)
import json
import os

logger = getLogger()
logger.setLevel(INFO)
ch = StreamHandler()
logger.addHandler(ch)

AUTHORIZATION_CODE = 911

def all_method(method, auth, data, name, url):
    """emulate a rest or rpc request on url"""
    if auth == AUTHORIZATION_CODE:
        return f"authorized {method} request of {data} on {name} {url}"
    else:
        return f"!! UNAUTHORIZED !!, auth = {auth} on {name} {url}"

def rest_wrapper(method):
    def wrapped(auth, data, name, url):
        return all_method(method, auth, data, name, url)
    return wrapped


class RestRequest():
    """
    this is our mock of python requests library
    use:
        RestRequest.<method>(auth, data, name, url)
        <method> in ('get', 'post', 'put', 'delete')
    RestRequest work with class methods only
    """
    def __new__(cls, *methods):
        for method in methods:
            setattr(
                cls,
                method,
                staticmethod(rest_wrapper(method))
            )
        return cls
r = RestRequest('get', 'post', 'put', 'delete')


class RestClient():
    def __init__(self, client_name, url, auth=None):
        self.client_name = client_name
        self.url = url
        self.auth = auth

    def _do_operation # TODO complete args in signature?
        data = json.dumps(kwargs.get("data", {}))
        endpoint = os.path.join(self.url, api_path.format(**kwargs))
        # TODO write call to RestRequest
        logger.info(
            f"===============================\n"
            f'RestClient._do_operation\n'
            f'on method:    {method_name}\n'
            f'on path:      {api_path}\n'
            f"with result:  {response}\n"
            f"===============================\n"
        )
        return response


def api_request(method_name, api_path):
    def outer_wrapper(func):
        @functools.wraps(func)
        def method_wrapper # TODO write signature args
            # + amc authent: not implemented here for simplicity)
            logger.info(
                f"api_request decorator on:\n"
                f"************** {func.__name__} **************\n"
                f"with with keyword arguments: {kwargs}\n"
            )
            return self._do_operation # TODO write args to call?

        return method_wrapper

    return outer_wrapper


class Contentd(RestClient):
    def __init__(self, client_name, url, auth):
        super().__init__(client_name, url, auth)

    @api_request('get', 'contentd/cdn_prefix/{cdn_prefix_id}')
    def get_cdn_prefix(self, cdn_prefix_id):
        """"""

    @api_request('put', 'contentd/cdn_prefix/{cdn_prefix_id}')
    def update_cdn_prefix(self, cdn_prefix_id, data):
        """"""


if __name__ == '__main__':
    c = Contentd('contentd', 'url', 911)
    c.get_cdn_prefix(cdn_prefix_id=5)

    c = Contentd('contentd', 'url', 911)
    c.update_cdn_prefix(cdn_prefix_id=5, data={'prefix':'my prefix'})

