from typing import TypeVar, Generic, List

from pydantic.generics import GenericModel

T = TypeVar('T')


class ListChunk(GenericModel, Generic[T]):
    chunk: List[T]
    length_total: int
