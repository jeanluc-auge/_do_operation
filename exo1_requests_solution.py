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
RPC_ENDPOINTS = {
    'onev': {
        'ListAll': ['object_type', 'filter_attrs', 'return_attrs'],
        'Update': ['object_type', 'object_id', 'data_attrs'],
        'Create': ['object_type', 'data_attrs'],
        'Bind': ['1st_object_type', '1st_object_id', '2nd_object_type', '2nd_object_id'],
        'Delete': ['object_type', 'object_id'],
    },
    'plc': {
        'GetSlices': ['data_attrs', 'return_attrs'],
    },
    'cob': {
        'GetPersons': ['person_filter', 'return_fields'],
        'AddPerson': ['person_fields'],
        'UpdatePerson': ['person_id_or_email', 'person_fields'],
        'DeletePerson': ['person_id_or_email'],
    }
}
methods_to_api = {method:api for api in RPC_ENDPOINTS for method in RPC_ENDPOINTS[api] }

def all_method(method, auth, data, name, url):
    """emulate a rest or rpc request on url"""
    if auth == AUTHORIZATION_CODE:
        return f"authorized {method} request of {data} on {name} {url}"
    else:
        return f"!! UNAUTHORIZED !!, auth = {auth} on {name} {url}"

def rest_wrapper(method):
    # TODO How is wrapped signature modified if we use classmethod instead of staticmethod in the call??
    def wrapped(auth, data, name, url):
        return all_method(method, auth, data, name, url)
    return wrapped

def rest_wrapper(method):
    # 2nd solution using *args & **kwargs
    # TODO: why I don't need to use named parameter on <method> arg?
    def wrapped(*args, **kwargs):
        return all_method(method, *args, **kwargs)
    return wrapped


def rpc_wrapper(method, name, url):
    # TODO: why don't we need to have self in wrapped args?
    # isn't wraped an instance method and tehrefore recieves self??
    def wrapped(auth, data):
        return all_method(method, auth, data, name, url)
    return wrapped


def rpc_wrapper(method, name, url):
    # 2nd solution using *args & **kwargs
    # TODO: why do I need to use named parameter on <name> and <url> args?
    def wrapped(*args, **kwargs):
        return all_method(method=method, name=name, url=url, *args, **kwargs)
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
        # TODO why do we use staticmethod? What do we need to modify if we use classmethod decorator?
        for method in methods:
            setattr(
                cls,
                method,
                staticmethod(rest_wrapper(method))
            )
        return cls
r = RestRequest('get', 'post', 'put', 'delete')


class RpcRequest():
    """
    this is our mock of xmlrpc library
    use:
        onev = RpcRequest(name, url)
        onev.<method>(auth, data)
        <method> in RPC_ENDPOINTS
        unlike RestRequest, RpcRequest works with a class instance and regular methods
    """
    def __init__(self, name, url):
        """"""
        self.name = name
        self.url = url
        self.methods = list(RPC_ENDPOINTS[name])
        self.build_methods()


    def build_methods(self):
        # we cannot reaffect name & url after class __init__ call
        for method in self.methods:
            setattr(
                self,
                method,
                rpc_wrapper(method, self.name, self.url)
            )


if __name__ == '__main__':
    # test rest request:
    # bad authent:
    response = RestRequest.get(auth=0, data={}, name='rest', url='url')
    print(response)
    # good authent
    response = RestRequest.post(auth=911, data={}, name='rest', url='url')
    print(response)

    # test rpc request:
    # init class:
    rpc_client = RpcRequest(name='plc', url='url')
    # bad authent:
    response = rpc_client.GetSlices(auth=0, data={})
    print(response)
    # good authent, and check if we can reaffect url?
    rpc_client.url = 'new_url'
    response = rpc_client.GetSlices(auth=911, data={})
    print(response)


