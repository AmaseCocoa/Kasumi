from __future__ import annotations

import inspect
from typing import Any, Callable, Coroutine, Dict

from .exceptions import AlreadyRegistedError, GearException

class Gear:
    def __init__(self, prefix: str = "") -> None:
        self._prefix = prefix
        self._requests: Dict[
            str, Dict[str, Callable[..., Coroutine[Any, Any, Any]]]
        ] = {}
        self._err: Dict[int, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._gears: Dict[str, Gear] = {}

    @property
    def prefix(self) -> str:
        return self._prefix

    def __normalize_path(self, path: str) -> str:
        return path.rstrip('/')

    def route(self, route: str, method: list = ["GET", "POST"]):
        def decorator(func):
            route_normalized = self.__normalize_path(self.prefix + route)
            route_prf = self.prefix + route
            if isinstance(func, staticmethod):
                func = func.__func__
            func._router_method = method
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Routes that listen for requests must be coroutines.")
            for m in method:
                met = m.upper()
                if route_prf not in self._requests or route_normalized not in self._requests:
                    self._requests[route_prf] = {}
                    self._requests[route_normalized] = {}
                if met in self._requests[route_prf] or met in self._requests[route_normalized]:
                    raise AlreadyRegistedError(
                        f"The function is already registered in the method “{met}” of the route “{route_normalized} ({route_prf})”."
                    )
                self._requests[route_prf][met] = func
                if route_prf != route_normalized:
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
            ev = self._err.get(error_code)
            if ev is not None:
                if ev and ev != {}:
                    raise AlreadyRegistedError(
                        f"The function is already registered in the ErrorCode “{error_code}”."
                    )
            self._err[error_code] = func
            return func

        return decorator

    def include_gear(self, gear: Gear):
        """
        Include routes and error handlers from another Gear instance.

        Parameters:
        - gear: The Gear instance to include.
        """
        if gear.prefix in self._gears:
            raise GearException(
                f"Gear with prefix '{gear.prefix}' is already included."
            )

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
            
    def _find_route_handler(self, path: str, method: str):
        """
        Find the route handler for a given path and method.

        Parameters:
        - path: The request path.
        - method: The request method (e.g., "GET", "POST").

        Returns:
        - The route handler function if found, otherwise None.
        """
        route_handlers = self._requests.get(path)
        if route_handlers:
            handler = route_handlers.get(method)
            if handler:
                return handler
        return None
