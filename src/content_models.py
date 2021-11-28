from __future__ import annotations

from typing import ClassVar, List, Literal

from pydantic import UUID4, validator

from datastore_model import DatastoreModel


class Author(DatastoreModel):
    name: str
    default_lookup_field: ClassVar[str] = 'name'

    @property
    def stories(self: Author) -> List[Story]:
        return self.children_of_type(Story)


class Universe(DatastoreModel):
    name: str

    @property
    def series(self: Universe) -> List[Series]:
        return self.children_of_type(Series)


class Series(DatastoreModel):
    name: str
    universe_id: UUID4

    @property
    def universe(self: Series) -> Universe:
        return Universe.from_id(id=self.universe_id)

    @property
    def stories(self: Series) -> List[Story]:
        return self.children_of_type(Story)

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Universe:
        return Universe.from_id(values['universe_id'])


class Story(DatastoreModel):
    title: str
    author_id: UUID4
    series_id: UUID4

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Series:
        return Series.from_id(values['series_id'])

    @property
    def author(self: Story) -> Author:
        return Author.from_id(id=self.author_id)


categories_literal = Literal[tuple(DatastoreModel.subclasses)]
