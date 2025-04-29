from typing import Any
import orjson
from django.http import HttpRequest
from ninja.renderers import BaseRenderer

class MyRenderer(BaseRenderer):
    media_type = 'application/json'
    charset = 'utf-8'

    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        return orjson.dumps(data)
