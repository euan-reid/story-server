"""Define core datastore model used by content models."""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar, cast
from uuid import UUID, uuid4

# google.cloud does dynamic build things, so can't be static type checked
from google.cloud import datastore  # mypy: ignore
from pydantic import UUID4, BaseModel, Field
from typing_extensions import Self

# mypy can't handle tuples in isinstance calls even though they're valid
# a bug has been open since 2018 to fix it - just ignore the errors
DATASTORE_BASIC_TYPES = (datetime, bool, float, int, str, None)

T = TypeVar('T', bound='DatastoreModel')

client = datastore.Client()


def datastore_dict_conversion(dict_to_parse: Dict[str, Any]) -> Dict[str, Any]:
    converted: Dict[str, Any] = {}
    for key, val in dict_to_parse.items():
        if isinstance(val, UUID):
            converted[key] = str(val)
        elif isinstance(val, DATASTORE_BASIC_TYPES):  # type: ignore
            converted[key] = val
        elif isinstance(val, list):
            converted[key] = datastore_list_conversion(val)
        elif isinstance(val, dict):
            converted[key] = datastore_dict_conversion(val)
        else:
            raise ValueError(
                f'{type(val)} could not be serialised to Datastore, must be '
                f'one of {DATASTORE_BASIC_TYPES + (list, dict)}. (found at '
                f'{key}: {val})'
            )
    return converted


def datastore_list_conversion(a_list: List[Any]) -> List[Any]:
    converted: List[Any] = []
    for item in a_list:
        if isinstance(item, UUID):
            converted.append(str(item))
        elif isinstance(item, DATASTORE_BASIC_TYPES):  # type: ignore
            converted.append(item)
        elif isinstance(item, list):
            converted.append(datastore_list_conversion(item))
        elif isinstance(item, dict):
            converted.append(datastore_dict_conversion(item))
        else:
            raise ValueError(
                f'{type(item)} could not be serialised to Datastore, must be '
                f'one of {DATASTORE_BASIC_TYPES + (list, dict)}. (found at '
                f'{item})'
            )
    return converted


class DatastoreModel(BaseModel):
    id: UUID4 = Field(default_factory=uuid4)
    name: str
    default_lookup_field: ClassVar[str] = 'id'
    parent: Optional[DatastoreModel] = None

    @classmethod
    @property
    def subclasses(cls) -> List[str]:
        # We should be able to just return [s.data...] but mypy doesn't agree
        # Worth rechecking every so often for a bugfix in mypy
        classes = [s.datastore_kind for s in cls.__subclasses__()]
        return cast(List[str], classes)

    @classmethod
    def subclass_from_name(cls, subclass_name: str) -> Type[DatastoreModel]:
        # cast() is unnecessary here too, but ditto above mypy struggles with
        # it and keeping mypy happy on defaults has value
        if subclass_name not in cls.subclasses():
            raise ValueError(f'Invalid type {subclass_name}')
        subclass = next(
            (
                s
                for s in cls.__subclasses__()
                if s.__name__.lower() == subclass_name
            ),
            None,
        )
        if subclass is None:
            # This path should never be exercised but guard for it just in case
            raise ValueError(f'Could not retrieve {subclass_name}')
        return subclass

    @classmethod
    @property
    def datastore_kind(cls) -> str:
        return cls.__name__.lower()

    @property
    def datastore_parent_key(self) -> Optional[datastore.Key]:
        if self.parent:
            return self.parent.datastore_key
        return None

    @property
    def datastore_key(self) -> datastore.Key:
        return client.key(
            self.datastore_kind,
            str(self.id),
            parent=self.datastore_parent_key,
        )

    def as_datastore_entity(self) -> datastore.Entity:
        entity = datastore.Entity(key=self.datastore_key)
        self_as_dict = datastore_dict_conversion(self.dict())
        entity.update(self_as_dict)
        return entity

    @classmethod
    def from_query(cls, filter_by: str, filter_for: str) -> List[Self]:
        query = client.query(kind=cls.datastore_kind)
        query = query.add_filter(filter_by, '=', filter_for)
        return [cls.parse_obj(result) for result in query.fetch()]

    @classmethod
    def from_id(cls, datastore_id: UUID4) -> Optional[Self]:
        key = client.key(cls.datastore_kind, datastore_id)
        result = client.get(key)

        if result is None:
            return None

        return cls.parse_obj(result)

    @classmethod
    def from_id_or_exception(cls, datastore_id: UUID4) -> Self:
        result = cls.from_id(datastore_id)
        if result is None:
            raise Exception(f'{cls.name} with id {datastore_id} not found')
        return result

    @classmethod
    def from_type_and_id(cls, name: str, id: UUID4) -> Optional[Self]:
        subclass = cls.subclass_from_name(name)
        return subclass.from_id(id)

    @classmethod
    def from_unique_lookup(cls, by: str, lookup: str) -> Optional[Self]:
        query_result = cls.from_query(filter_by=by, filter_for=lookup)
        return next(iter(query_result), None)

    @classmethod
    def from_name(cls, name: str) -> Optional[Self]:
        return cls.from_unique_lookup(by='name', lookup=name)

    @classmethod
    def from_type_and_name(
        cls,
        subclass_name: str,
        name: str,
    ) -> Optional[Self]:
        subclass = cls.subclass_from_name(subclass_name)
        return subclass.from_name(name)

    @classmethod
    def from_lookup(cls, look_for: str) -> Optional[Self]:
        if 'id' == cls.default_lookup_field:
            return cls.from_id(UUID(look_for))
        return cls.from_unique_lookup(cls.default_lookup_field, look_for)

    @classmethod
    def from_type_and_lookup(
        cls,
        subclass_name: str,
        look_for: str,
    ) -> Optional[Self]:
        subclass = cls.subclass_from_name(subclass_name)
        return subclass.from_lookup(look_for)

    def children_of_type(self, child_type: Type[T]) -> List[T]:
        return child_type.from_query(
            filter_by=self.datastore_kind,
            filter_for=str(self.id),
        )

    def save(self) -> None:
        client.put(self.as_datastore_entity())
