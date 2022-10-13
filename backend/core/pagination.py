from typing import Generic, Sequence, TypeVar

from fastapi import Query
from pydantic.generics import GenericModel


T = TypeVar('T')


class Page(GenericModel, Generic[T]):
    limit: int = 10
    offset: int = 0
    total: int = 0
    items: Sequence[T]


class LimitOffsetPagination:
    def __init__(self, limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
        self.limit = limit
        self.offset = offset

    def paginate(self, items: Sequence[T], total: int) -> Page[T]:
        return Page(
            limit=self.limit,
            offset=self.offset,
            total=total,
            items=items
        )
