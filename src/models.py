from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Type, TypeVar
from uuid import uuid4, UUID
from google.cloud import datastore
from pydantic import BaseModel, Field, UUID4

T = TypeVar('T')

client = datastore.Client()


def is_instance_of_datastore_basic_type(o: object) -> bool:
    return isinstance(o, (datetime, bool, float, int, str, None))


def datastore_dict_conversion(d: dict) -> dict:
    converted = {}
    for k, v in d.items():
        if isinstance(v, UUID):
            converted[k] = str(v)
        elif is_instance_of_datastore_basic_type(v):
            converted[k] = v
        elif (isinstance(v, list)):
            converted[k] = datastore_list_conversion(v)
        elif (isinstance(v, dict)):
            converted[k] = datastore_dict_conversion(v)
        else:
            raise ValueError(
                f'{type(v)} could not be serialised to Datastore, must be one '
                f'of {(datetime, bool, float, int, str, None, list, dict)}. (found at {k}: {v})'
            )
    return converted


def datastore_list_conversion(a_list: list) -> list:
    converted = []
    for i in a_list:
        if isinstance(i, UUID):
            converted.append(str(i))
        elif is_instance_of_datastore_basic_type(v):
            converted.append(i)
        elif (isinstance(i, list)):
            converted.append(datastore_list_conversion(i))
        elif (isinstance(i, dict)):
            converted.append(datastore_dict_conversion(i))
        else:
            raise ValueError(
                f'{type(i)} could not be serialised to Datastore, must be one '
                f'of {(datetime, bool, float, int, str, None, list, dict)}. (found at {i})'
            )
    return converted


class DatastoreModel(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)

    @classmethod
    @property
    def datastore_kind(cls: Type[T]) -> str:
        return cls.__name__.lower()

    @property
    def datastore_parent_key(self: Type[T]) -> datastore.Key:
        return None

    @property
    def datastore_key(self: Type[T]) -> datastore.Key:
        return client.key(
            self.datastore_kind, str(self.id),
            parent=self.datastore_parent_key
        )

    def as_datastore_entity(self: Type[T]) -> datastore.Entity:
        entity = datastore.Entity(key=self.datastore_key)
        self_as_dict = datastore_dict_conversion(self.dict())
        entity.update(self_as_dict)
        return entity

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
            filter_for=str(self.id)
        )

    def save(self) -> None:
        client.put(self.as_datastore_entity())


class Author(DatastoreModel):
    name: str

    @property
    def stories(self) -> List[Story]:
        return self.children_of_type(Story)

    @classmethod
    def from_name(cls: Type[T], name: str) -> T:
        query = client.query(kind=cls.datastore_kind)
        query = query.add_filter('name', '=', name)
        return [cls.parse_obj(result) for result in query.fetch()][0]


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

    @property
    def datastore_parent_key(self: Type[T]) -> datastore.Key:
        return self.universe.datastore_key


class Story(DatastoreModel):
    title: str
    author_id: UUID4
    series_id: UUID4

    @property
    def datastore_parent_key(self: Type[T]) -> datastore.Key:
        return self.series.datastore_key

    @property
    def author(self) -> Author:
        return Author.from_datastore(id=self.author_id)

    @property
    def series(self) -> Series:
        return Series.from_datastore(id=self.series_id)


T.__constraints__ = tuple(DatastoreModel.__subclasses__())
categories_literal = Literal[tuple(DatastoreModel.subclasses)]
