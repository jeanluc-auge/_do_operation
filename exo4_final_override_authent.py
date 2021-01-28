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
    def wrapped(auth, data, name, url):
        return all_method(method, auth, data, name, url)
    return wrapped


def rpc_wrapper(method, name, url):
    def wrapped(auth, data):
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

    def __getattribute__(self, item):
        if item in methods_to_api:
            return self._do_rpc_operation(item)
        else:
            return super().__getattribute__(item)

    def _do_rpc_operation(self, item):
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
        # TODO add override for authent in signatures and calls
        def do_rpc_method(*args, **kwargs):
            """
            return a partial method with auth field already filled
            RpcRequest.method(auth=auth)

            """
            logger.info(f'_do_rpc_method args={args}, kwargs={kwargs}')
            result = method(self.auth, **kwargs)
            logger.info(
                f"\n================================================================\n"
                f"RpcClient._do_rpc_operation\n"
                f"calling:      {description}\n"
                f"on:           {kwargs}\n"
                f"with result:  {result}\n"
                f"===================================================================="
            )
            return result
        return do_rpc_method


class Onevsh(RpcClient):
    def __init__(self, onev_url, cob_url, plc_url, auth=0):
        super().__init__(onev_url, cob_url, plc_url, auth)

    def listall_node_names(self, ip_address_id):
        return self.ListAll(
            data={
                'object_type':'IpAddress',
                'filter_attrs':{'ip_address_id': ip_address_id},
                'return_attrs':['type']
            }
        )

class RestClient():
    def __init__(self, client_name, url, auth):
        self.client_name = client_name
        self.url = url
        self.auth = auth

    def _do_operation(self, method_name, api_path, **kwargs):
        data = json.dumps(kwargs.get("data", {}))
        # TODO add authent override
        endpoint = os.path.join(self.url, api_path.format(**kwargs))
        response = getattr(RestRequest, method_name)(self.auth, data, self.client_name, endpoint)
        logger.info(
            f"===============================\n"
            f'RestClient._do_operation\n'
            f'on method:    {method_name}\n'
            f'on path:      {api_path}\n'
            f'with kwargs   {kwargs}\n'
            f"with result:  {response}\n"
            f"===============================\n"
        )
        return response


def api_request(method_name, api_path):
    def outer_wrapper(func):
        @functools.wraps(func)
        def method_wrapper(self, *args, **kwargs):
            # + amc authent: not implemented here for simplicity)
            logger.info(
                f"api_request decorator on:\n"
                f"************** {func.__name__} **************\n"
                f"with with keyword arguments: {kwargs}\n"
            )
            return self._do_operation(method_name, api_path, **kwargs)

        return method_wrapper

    return outer_wrapper


class Contentd(RestClient):
    def __init__(self, client_name, url, auth=0):
        super().__init__(client_name, url, auth)

    @api_request('get', 'contentd/cdn_prefix/{cdn_prefix_id}')
    def get_cdn_prefix(self, cdn_prefix_id):
        """"""

    @api_request('put', 'contentd/cdn_prefix/{cdn_prefix_id}')
    def update_cdn_prefix(self, cdn_prefix_id, data):
        """"""



class Libcdn(Contentd, Onevsh):
    def __init__(self, rest_client_name, rest_url, onev_url, cob_url, plc_url, auth=0):
        Contentd.__init__(self, rest_client_name, rest_url, auth)
        Onevsh.__init__(self, onev_url, cob_url, plc_url, auth)

    #TODO redefine _do_rpc_operation & _do_operation to override default authent (=0)
    # so that l.macro1() call does not return '!! unauthorized !!'

    def macro1(self):
        return (
            f"***********************************************************\n"
            f"macro1 with results:\n"
            f"contentd: {self.get_cdn_prefix(cdn_prefix_id=5)}\n"
            f"onevsh:   {self.listall_node_names(2)}"
        )

if __name__ == '__main__':
    # c = Contentd('contentd', 'url', 911)
    # c.get_cdn_prefix(cdn_prefix_id=5)
    #
    # o = Onevsh('onev_url', 'cob_url', 'plc_url', 911)
    # o.listall_node_names(2)

    l = Libcdn('contentd', 'amc_url', 'onev_url', 'cob_url', 'plc_url')
    print(l.macro1())
