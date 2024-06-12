# Copyright 2024 AmaseCocoa
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
from http.client import responses

from starlette.requests import Request
from starlette.responses import PlainTextResponse

from .exceptions import AlreadyRegistedError


class Kasumi:
    def __init__(self) -> None:
        self.__requests = {}
        self.__err = {}
    
    async def __call__(self, scope, receive, send):
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