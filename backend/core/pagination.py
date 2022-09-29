from typing import Generic, Sequence, TypeVar

from pydantic.generics import GenericModel


T = TypeVar('T')


class Page(GenericModel, Generic[T]):
    limit: int = 10
    offset: int = 0
    total: int = 0
    items: Sequence[T]


def paginate(items: Sequence[T], limit: int, offset: int, total: int) -> Page[T]:
    return Page(
        limit=limit,
        offset=offset,
        total=total,
        items=items
    )
