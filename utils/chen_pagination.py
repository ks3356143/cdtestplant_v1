from django.db.models import QuerySet
from ninja.pagination import PaginationBase
from ninja.types import DictStrAny
from ninja_schema import Schema
from ninja import Field
from typing import List,Any

# 这个结构是前端要求的，看前端代码可知
class Total(Schema):
    total:int

class MyPagination(PaginationBase):
    class Input(Schema):
        pageSize: int = Field(10, gt=0)
        page: int = Field(1, gt=-1)

    class Output(Schema):
        items: List[Any]
        pageInfo: Total

    def paginate_queryset(
            self,
            queryset: QuerySet,
            pagination: Input,
            **params: DictStrAny,
    ) -> Any:
        offset = pagination.pageSize * (pagination.page - 1)
        limit: int = pagination.pageSize
        return {
            "page": offset,
            "limit": limit,
            "items": queryset[offset: offset + limit],
            "pageInfo": {'total':self._items_count(queryset)},
        }  # noqa: E203