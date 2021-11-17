from __future__ import annotations

from typing import List, Literal, Type, TypeVar
from uuid import uuid4
from google.cloud import datastore
from pydantic import BaseModel, Field, UUID4

T = TypeVar('T')

client = datastore.Client()


class DatastoreModel(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)

    @classmethod
    @property
    def datastore_kind(cls: Type[T]) -> str:
        return cls.__name__.lower()

    @classmethod
    @property
    def subclasses(cls) -> List[str]:
        return [s.datastore_kind for s in cls.__subclasses__()]

    @classmethod
    def from_id(cls: Type[T], id: UUID4) -> T:
        key = client.key(cls.datastore_kind, id)
        result = client.get(key)

        if result is None:
            return None

        return cls.parse_obj(result)

    @classmethod
    def from_type_and_id(cls: Type[T], subclass_name: str, id: UUID4) -> T:
        if subclass_name not in cls.subclasses:
            raise ValueError(f'Invalid type {subclass_name}')
        subclass = [
            s for s in cls.__subclasses__()
            if s.__name__.lower() == subclass_name
        ][0]
        return subclass.from_id(id)

    @classmethod
    def from_query(cls: Type[T], filter_by: str, filter_for: str) -> List[T]:
        query = client.query(kind=cls.datastore_kind)
        query = query.add_filter(filter_by, '=', filter_for)
        return [cls.parse_obj(result) for result in query.fetch()]

    def children_of_type(self, child_type: Type[T]) -> List[T]:
        return child_type.from_query(
            filter_by=self.datastore_kind,
            filter_for=self.id
        )


class Author(DatastoreModel):
    name: str

    @property
    def stories(self) -> List[Story]:
        return self.children_of_type(Story)


class Universe(DatastoreModel):
    name: str

    @property
    def series(self) -> List[Series]:
        return self.children_of_type(Series)


class Series(DatastoreModel):
    name: str
    universe_id: UUID4

    @property
    def universe(self) -> Universe:
        return Universe.from_datastore(id=self.universe_id)

    @property
    def stories(self) -> List[Story]:
        return self.children_of_type(Story)


class Story(DatastoreModel):
    title: str
    author_id: Author
    series_id: Series

    @property
    def author(self) -> Author:
        return Author.from_datastore(id=self.author_id)

    @property
    def series(self) -> Series:
        return Series.from_datastore(id=self.series_id)


T.__constraints__ = tuple(DatastoreModel.__subclasses__())
categories_literal = Literal[tuple(DatastoreModel.subclasses)]
