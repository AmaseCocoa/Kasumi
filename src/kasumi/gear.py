import inspect

from .exceptions import AlreadyRegistedError

class Gear:
    
    def __init__(self, prefix: str="") -> None:
        self.__prefix = prefix
        self._requests = {}
        self._err = {}
        
    def route(self, route: str, method: list="GET"):
        def decorator(func):
            APIRoute = self.__prefix + route
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            for m in method:
                met = m.upper()
                ev = self._requests.get(APIRoute)
                if ev is None:
                    self._requests[APIRoute] = {}
                    ev = self._requests.get(APIRoute)
                else:
                    if ev.get(met) and ev.get(met) != {}:
                        raise AlreadyRegistedError(f'The function is already registered in the method “{met}” of the route “{APIRoute}”.')
                ev[met] = func
            return func
        return decorator

    def get(self, route: str):
        def decorator(func):
            APIRoute = self.__prefix + route
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            ev = self._requests.get(APIRoute)
            if ev is None:
                self._requests[APIRoute] = {}
                ev = self._requests.get(APIRoute)
            else:
                if ev.get("GET") and ev.get("GET") != {}:
                    raise AlreadyRegistedError(f'The function is already registered in the method “GET” of the route “{APIRoute}”.')
            ev["GET"] = func
            return func
        return decorator

    def post(self, route: str):
        def decorator(func):
            APIRoute = self.__prefix + route
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            ev = self._requests.get(APIRoute)
            if ev is None:
                self._requests[APIRoute] = {}
                ev = self._requests.get(APIRoute)
            else:
                if ev.get("POST") and ev.get("POST") != {}:
                    raise AlreadyRegistedError(f'The function is already registered in the method “POST” of the route “{APIRoute}”.')
            ev["POST"] = func
            return func
        return decorator

    def err(self, error_code: int):
        def decorator(func):
            if isinstance(func, staticmethod):
                func = func.__func__
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Handler that listen for error must be coroutines.")
            ev = self._err.get(error_code)
            if ev is not None:
                if ev and ev != {}:
                    raise AlreadyRegistedError(f'The function is already registered in the ErrorCode “{error_code}”.')
            self._err[error_code] = func
            return func
        return decorator