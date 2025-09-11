from contextvars import ContextVar
from fastapi import Request

request_var: ContextVar[Request] = ContextVar("request", default=None)

def set_request(request: Request):
    request_var.set(request)

def get_request() -> Request:
    return request_var.get()
