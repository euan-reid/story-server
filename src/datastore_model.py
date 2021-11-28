from __future__ import annotations

from datetime import datetime
from typing import ClassVar, List, Optional, Type, TypeVar
from uuid import uuid4, UUID
from google.cloud import datastore
from pydantic import BaseModel, Field, UUID4

T = TypeVar('T', bound='DatastoreModel')
C = TypeVar('C', bound='DatastoreModel')

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
                f'of {(datetime, bool, float, int, str, None, list, dict)}. '
                f'(found at {k}: {v})'
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
                f'of {(datetime, bool, float, int, str, None, list, dict)}. '
                f'(found at {i})'
            )
    return converted


class DatastoreModel(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    name: str
    default_lookup_field: ClassVar[str] = 'id'
    parent: Optional[T] = None

    @classmethod
    @property
    def subclasses(cls: Type[T]) -> List[str]:
        return [s.datastore_kind for s in cls.__subclasses__()]

    @classmethod
    def subclass_from_name(cls: Type[T], subclass_name: str) -> Type[T]:
        if subclass_name not in cls.subclasses:
            raise ValueError(f'Invalid type {subclass_name}')
        subclass = next((
            s for s in cls.__subclasses__()
            if s.__name__.lower() == subclass_name
        ), None)
        if subclass is None:
            # This path should never be exercised but guard for it just in case
            raise ValueError(f'Could not retrieve {subclass_name}')
        return subclass

    @classmethod
    @property
    def datastore_kind(cls: Type[T]) -> str:
        return cls.__name__.lower()

    @property
    def datastore_parent_key(self: Type[T]) -> datastore.Key:
        if self.parent:
            return self.parent.datastore_key
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
    def from_query(cls: Type[T], filter_by: str, filter_for: str) -> List[T]:
        query = client.query(kind=cls.datastore_kind)
        query = query.add_filter(filter_by, '=', filter_for)
        return [cls.parse_obj(result) for result in query.fetch()]

    @classmethod
    def from_id(cls: Type[T], id: UUID4) -> Optional[T]:
        key = client.key(cls.datastore_kind, id)
        result = client.get(key)

        if result is None:
            return None

        return cls.parse_obj(result)

    @classmethod
    def from_type_and_id(cls: Type[T], subclass_name: str, id: UUID4) -> Optional[T]:
        subclass = cls.subclass_from_name(subclass_name)
        return subclass.from_id(id)

    @classmethod
    def from_unique_lookup(cls: Type[T], by: str, look_for: str) -> Optional[T]:
        query_result = cls.from_query(filter_by=by, filter_for=look_for)
        return next(iter(query_result), None)

    @classmethod
    def from_name(cls: Type[T], name: str) -> Optional[T]:
        return cls.from_unique_lookup(by='name', look_for=name)

    @classmethod
    def from_type_and_name(
        cls: Type[T],
        subclass_name: str,
        name: str
    ) -> Optional[T]:
        subclass = cls.subclass_from_name(subclass_name)
        return subclass.from_name(name)

    @classmethod
    def from_lookup(cls: Type[T], look_for: str) -> Optional[T]:
        if 'id' == cls.default_lookup_field:
            return cls.from_id(look_for)
        return cls.from_unique_lookup(cls.default_lookup_field, look_for)

    @classmethod
    def from_type_and_lookup(
        cls: Type[T],
        subclass_name: str,
        look_for: str
    ) -> Optional[T]:
        subclass = cls.subclass_from_name(subclass_name)
        return subclass.from_lookup(look_for)

    def children_of_type(self: Type[T], child_type: Type[C]) -> List[C]:
        return child_type.from_query(
            filter_by=self.datastore_kind,
            filter_for=str(self.id)
        )

    def save(self: Type[T]) -> None:
        client.put(self.as_datastore_entity())
