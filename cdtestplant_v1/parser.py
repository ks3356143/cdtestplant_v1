import orjson
from django.http import HttpRequest
from ninja.parser import Parser
from ninja.types import DictStrAny

class MyParser(Parser):
    def parse_body(self, request: HttpRequest) -> DictStrAny:
        return orjson.loads(request.body)
