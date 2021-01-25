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
            # TODO 1 write call to all_method functions in methods with setattr
            # TIP: you may need to write an additional wrapper function or use lambda
            # see expected beahvior below in if __name__="__main__"
            pass
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
        # TODO 2 : can we change (re-affect) self.name and self.url after class __init__?
        # => meaning, yes of course we can, but does it change the rpc methods??
        #   => if yes, why?
        #   => if no, how to rewrite class __init__ to make it possible?

    def build_methods(self):
        for method in self.methods:
            # TODO 1 : write call to all_method functions in methods with setattr
            # TIP: you may need to write an additional wrapper function or use lambda
            # see expected beahvior below in if __name__="__main__"
            pass



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
    # good authent:
    response = rpc_client.GetSlices(auth=911, data={})
    print(response)

