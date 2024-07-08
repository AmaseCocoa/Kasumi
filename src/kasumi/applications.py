import inspect
from http.client import responses
from typing import Dict, Callable, Coroutine, Any

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .exceptions import AlreadyRegistedError, GearException
from .gear import Gear
from .websocket import WebSocket
class Kasumi:
    
    def __init__(self) -> None:
        self.__err = {}
        self.__lifespan = {
            "startup": [],
            "shutdown": [],
            "lifespan": []
        }
        self._requests: Dict[str, Dict[str, Callable[..., Coroutine[Any, Any, Any]]]] = {}
        self._err: Dict[int, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._gears: Dict[str, Gear] = {}

    def include_gear(self, gear: Gear):
        """
        Include routes and error handlers from a Gear instance into the Kasumi app.

        Parameters:
        - gear: The Gear instance to include.
        """
        if gear.prefix in self._gears:
            raise GearException(f"Gear with prefix '{gear.prefix}' is already included.")
        self._gears[gear.prefix] = gear
        for route, methods in gear._requests.items():
            full_route = gear.prefix + route
            if full_route not in self._requests:
                self._requests[full_route] = methods
            else:
                for method, func in methods.items():
                    if method in self._requests[full_route]:
                        raise AlreadyRegistedError(
                            f"The function is already registered in the method “{method}” of the route “{full_route}”."
                        )
                    self._requests[full_route][method] = func
        for error_code, func in gear._err.items():
            if error_code in self._err:
                raise AlreadyRegistedError(
                    f"The function is already registered in the ErrorCode “{error_code}”."
                )
            self._err[error_code] = func

    def __normalize_path(self, path: str) -> str:
        return path.rstrip('/')

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
        if scope['type'] == 'http':
            handler = None
            request = Request(scope, receive)
            handler = self.__find_route_handler(scope, request.method)
            if handler:
                if isinstance(handler, int):
                    await self.__handle_err(request, scope, receive, send, handler)
                else:
                    response = await handler(request)
                    await response(scope, receive, send)
            else:
                await self.__handle_err(request, scope, receive, send, 404)
        elif scope['type'] == 'lifespan':
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    for lifespan in self.__lifespan["startup"]:
                        await lifespan()
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    for lifespan in self.__lifespan["shutdown"]:
                        await lifespan()
                    await send({'type': 'lifespan.shutdown.complete'})
                    return
        elif scope['type'] == 'websocket':
            print(self._requests[scope['path']])
            handler = None
            handler = self.__find_route_handler(scope, "WS")
            if handler:
                websocket = WebSocket(scope, receive, send)
                await handler(websocket)

    def __find_route_handler(self, scope, method: str) -> Callable[..., Coroutine[Any, Any, Any]]:
        path = scope['path']
        method = method.upper()
        if path in self._requests and method in self._requests[path]:
            return self._requests[path][method]
        for gear in self._gears.values():
            if path.startswith(gear.prefix):
                return gear._find_route_handler(path, method)
        return None

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

    def lifespan(self, event: str):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("lifespan that listen for requests must be coroutines.")
            if event not in ["startup", "shutdown"]:
                raise TypeError("Only startup or shutdown can be set for event.")
            else:
                self.__lifespan[event].append(func)
            return func
        return decorator

    def ws(self, route: str):
        def decorator(func):
            route_normalized = self.__normalize_path(route)
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            if route not in self._requests or route_normalized not in self._requests:
                    self._requests[route] = {}
                    self._requests[route_normalized] = {}
            if "WS" in self._requests[route] or "WS" in self._requests[route_normalized]:
                raise AlreadyRegistedError(
                    f"The function is already registered in the method “WebSocket” of the route “{route_normalized} ({route})”."
                )
            self._requests[route]["WS"] = func
            if route != route_normalized:
                self._requests[route_normalized]["WS"] = func
            return func
        return decorator

    def route(self, route: str, method: list = ["GET", "POST"]):
        def decorator(func):
            route_normalized = self.__normalize_path(route)
            if isinstance(func, staticmethod):
                func = func.__func__
            func._router_method = method
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            for m in method:
                met = m.upper()
                if route not in self._requests or route_normalized not in self._requests:
                    self._requests[route] = {}
                    self._requests[route_normalized] = {}
                if met in self._requests[route] or met in self._requests[route_normalized]:
                    raise AlreadyRegistedError(
                        f"The function is already registered in the method “{met}” of the route “{route_normalized} ({route})”."
                    )
                self._requests[route][met] = func
                if route != route_normalized:
                    self._requests[route_normalized][met] = func
            return func
        return decorator

    def get(self, route: str):
        return self.route(route, method=["GET"])

    def post(self, route: str):
        return self.route(route, method=["POST"])

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