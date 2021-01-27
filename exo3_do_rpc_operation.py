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


def rpc_wrapper(method, name, url):
    def wrapped(auth, data):
        return all_method(method, auth, data, name, url)
    return wrapped


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
        for method in self.methods:
            setattr(
                self,
                method,
                rpc_wrapper(method, self.name, self.url)
            )


class RpcClient():
    def __init__(self, onev_url, cob_url, plc_url, auth=None):
        self.onev = RpcRequest('onev', onev_url)
        self.cob = RpcRequest('cob', cob_url)
        self.plc = RpcRequest('plc', plc_url)
        self.auth = auth

    def __getattribute__ # TODO complete signature
        if item in methods_to_api:
            return self._do_rpc_operation # TODO complete call
        else:
            return super().__getattribute__(item)

    def _do_rpc_operation # TODO complete signature
        """
        xmlrpc call with decoration and authentification
        :param item: str xmlrpc method name
        :param kwargs: pass specific auth headers with 'auth' key
        :return: xmlrpc method with auth headers already filled in (<=> partial call)
        """
        api_name = methods_to_api[item]
        api = getattr(self, api_name) # onev, cob or plc
        method = getattr(api, item) # onev.ListAll, onev.Update, plc.GetSlices...
        description = f"{api_name}.{item}" # logging & debug interest only
        logger.info(
            f"\n================================================================\n"
            f"RpcClient._do_rpc_operation\n"
            f"calling:      {description}\n"
            f"on:           {item}\n"
            f"===================================================================="
        )
        # TODO 1 : write RpcRequest (for example onev.ListAll)
        # => you will need to modify Onevsh.listall_node_names to pass auth arg
        # TODO 2: same but partially fill auth field with self.auth so that it doesn't need to be passed as arg


class Onevsh(RpcClient):
    """
    our final rpc client called by cdn macros
    expose 'advanced' rpc functions
    built from onev, cob & plc based rpc
    """
    def __init__(self, onev_url, cob_url, plc_url, auth):
        # init our parent RpcClient:
        super().__init__(onev_url, cob_url, plc_url, auth)

    def listall_node_names(self, ip_address_id):
        """
        example of advanced rpc function
        !! we don't need to pass auth !!
        :param ip_address_id:
        :return:
        """
        return self.ListAll(
            data={
                'object_type':'IpAddress',
                'filter_attrs':{'ip_address_id': ip_address_id},
                'return_attrs':['type']
            }
        )


if __name__ == '__main__':
    # direct basic rpc request (exo1):
    rpc_client = RpcRequest(name='plc', url='url')
    response = rpc_client.GetSlices(auth=911, data={})
    print(response)

    # advanced rpc function call:
    o = Onevsh('onev_url', 'cob_url', 'plc_url', 911)
    print(o.listall_node_names(2))

