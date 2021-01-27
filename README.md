# architecture sandbox

- proposes 4 evolutive exercises with solution
- explores class inheritance & delegation, function wrappers and decorators 

### EXO 1:

mock of python requests and xmlrpc librairies <br>
- RestRequest class to mock requests library<br>
usage:<br>
```
    implements class methods get, post, put, delete
    response = RestRequest.<method>(auth, data, name, url)
```
- RpcRequest class to mock xmlrpc library<br>
usage:<br>
```
    implements specific rpc methods ListAll, Create, ... depending on instance
    rpc_client = RpcRequest(name, url)
    response = rpc_client.<method>(auth, data)
```
- Both RestRequest and RpcRequest methods return a generic mock function "all_method" that represents the http request:
```
def all_method(method, auth, data, name, url):
    """emulate a rest or rpc request on url"""
    if auth == AUTHORIZATION_CODE:
        return f"authorized {method} request of {data} on {name} {url}"
    else:
        return f"!! UNAUTHORIZED !!, auth = {auth} on {name} {url}"
```
- exo1 automates the creation of RestRequest and RpcRequest methods based on specific wrappers of all_methods

### EXO 2:

Implements a generic RestClient for HTTP REST requests using the mock RestRequest created in exo1 <br>
The generic rest client architecture is as follow:
- *api specific daughter classes* 
    - one implemented as Contentd 
    - exposes api rest functions for each api endpoint
    - the @api_request decorator automates the exposition so that the endpoint function does not need any specific code. Only a docstring:
```
    @api_request(rest_method, this_endpoint_path/{args})
    def this_endpoint_path_function(self, args=args, data=data):
        """doc string"""
        !! no code !! 
```
     
- *generic parent class RestClient*
    - implementing a _do_operation method to make the rest request on the api url
    - _do_operation is called by the @api_rest decorator of each endpoint_function
    
- exo2 explores the construction of the @api_rest decorator and the _do_operation generic function

### EXO 3

Implements a generic RpcClient for XML RPC requests with the mock RpcRequest created in exo1.<br>
The rpc client architecture is as follow:
- *api specific daughter class*
    - one implemented as Onevsh
    - exposes custom functions for specific rpc endpoints
- *generic parent class RpcClient*
    - creates the needed client xmlrpc instances, for example: 
    ```
    self.onev = RpcRequest('onev', onev_url)
    ```
    - class delegation of the daughter classes methods call to these instances
    - the delegation is implemented in a _do_rpc_operation method 
- exo3 explores the construction of the _do_rpc_operation method and how to fill in the auth parameter

### EXO 4

Full sandbox with both rest and rpc clients. The auth parameter is passed as default at init of the rest Contentd(RestClient) and rpc Onevsh(RpcClient) classes. <br>
Here we look at how the default auth can be bypassed by redefining the _do_rpc_operation and _do_operation of the parent class in Onevsh and Contentd daughter classes.<br>
A new class Libcdn inherits from both rest and rpc clients to propose advanced functions (so called macros). The macros may be exposed by a Flask app with specific user authentication. hence the need to redefine the auth credentials in the Flask context, depending on the user credentials accessing the maco endpoint.
 



 

