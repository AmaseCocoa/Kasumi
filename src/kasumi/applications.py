import inspect
from importlib import import_module
import os
from http.client import responses

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .exceptions import AlreadyRegistedError, GearException
from .gear import Gear

class Kasumi:
    
    def __init__(self) -> None:
        self.__requests = {}
        self.__err = {}
    
    async def __call__(self, scope, receive, send):
        """
        This function handles incoming HTTP requests by routing them to the appropriate handler based on
        the request method and path.
        
        :param scope: The `scope` parameter in the `__call__` method represents the metadata of the
        incoming request. It contains information such as the type of the request (e.g., 'http' for HTTP
        requests), the path of the request, and other details related to the communication channel. In
        the provided
        :param receive: The `receive` parameter in the `__call__` method is a callable that is used to
        receive messages from the client. It is typically an asynchronous function that receives
        messages from the client connection. In the context of an HTTP server, the `receive` function is
        used to receive incoming HTTP requests
        :param send: The `send` parameter in the `__call__` method is a coroutine function that is used
        to send messages to the client. It is typically used to send HTTP response messages back to the
        client. The `send` function takes a single argument, which is a dictionary representing the
        message to be
        """
        
        assert scope['type'] == 'http'
        request = Request(scope, receive)
        if self.__requests.get(scope['path']):
            req: dict = self.__requests[scope['path']]
            if req.get(request.method):
                func = req.get(request.method)
                response = await func(request)
                await response(scope, receive, send)
            else:
                await self.__handle_err(request, scope, receive, send, status_code=405)
        else:
            await self.__handle_err(request, scope, receive, send, status_code=404)
    
    async def __handle_err(self, request, scope, receive, send, status_code: int=404):
        if self.__err.get(status_code):
            func: dict = self.__err[status_code]
            response = await func(request)
            await response(scope, receive, send)
        else:
            resp_msg = responses.get(status_code)
            if resp_msg is None:
                resp_msg = f"Error {status_code}, UNKNOWN STATUSCODE"
            response = PlainTextResponse(resp_msg, status_code=status_code)
            await response(scope, receive, send)

    def route(self, route: str, method: list="GET"):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            for m in method:
                met = m.upper()
                ev = self.__requests.get(route)
                if ev is None:
                    self.__requests[route] = {}
                    ev = self.__requests.get(route)
                else:
                    if ev.get(met) and ev.get(met) != {}:
                        raise AlreadyRegistedError(f'The function is already registered in the method “{met}” of the route “{route}”.')
                ev[met] = func
            return func
        return decorator

    def get(self, route: str):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            ev = self.__requests.get(route)
            if ev is None:
                self.__requests[route] = {}
                ev = self.__requests.get(route)
            else:
                if ev.get("GET") and ev.get("GET") != {}:
                    raise AlreadyRegistedError(f'The function is already registered in the method “GET” of the route “{route}”.')
            ev["GET"] = func
            return func
        return decorator

    def post(self, route: str):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            ev = self.__requests.get(route)
            if ev is None:
                self.__requests[route] = {}
                ev = self.__requests.get(route)
            else:
                if ev.get("POST") and ev.get("POST") != {}:
                    raise AlreadyRegistedError(f'The function is already registered in the method “POST” of the route “{route}”.')
            ev["POST"] = func
            return func
        return decorator

    def err(self, error_code: int):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Handler that listen for error must be coroutines.")
            ev = self.__err.get(error_code)
            if ev is not None:
                if ev and ev != {}:
                    raise AlreadyRegistedError(f'The function is already registered in the ErrorCode “{error_code}”.')
            self.__err[error_code] = func
            return func
        return decorator
    
    def combine_route(self, route: dict, name: str, routeType: str="normal"):
        if routeType == "normal":
            self.__requests[name] = route
        elif routeType == "err":
            self.__err[name] = route
    
    def include_gear(self, module: Gear):
        route = module._requests
        for k in route.keys():
            if self.__requests.get(k):
                for router in route[k].keys():
                    if self.__requests[k].get(router):
                        raise GearException(f"""The Route "{k}" registered in the gear has another function registered""")
            else:
                self.combine_route(
                    route[k], k
                )
        del k
        err = module._err
        for k in err.keys():
            if self.__err.get(k):
                for error in err[k].keys():
                    if self.__requests[k].get(error):
                        raise GearException(f"""The Route "{k}" registered in the gear has another function registered""")
            else:
                self.combine_route(
                    err[k], k
                )