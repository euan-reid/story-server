from __future__ import annotations

from typing import List, Literal

from pydantic import UUID4, validator

from datastore_model import DatastoreModel


class Author(DatastoreModel):
    @property
    def stories(self) -> List[Story]:
        return self.children_of_type(Story)


class Universe(DatastoreModel):
    @property
    def series(self) -> List[Series]:
        return self.children_of_type(Series)


class Series(DatastoreModel):
    universe_id: UUID4

    @property
    def universe(self) -> Universe:
        return Universe.from_id_or_exception(datastore_id=self.universe_id)

    @property
    def stories(self) -> List[Story]:
        return self.children_of_type(Story)

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Universe:
        # TODO: Consider JIT creation instead
        parent = Universe.from_id_or_exception(values['universe_id'])
        return parent


class Story(DatastoreModel):
    author_id: UUID4
    series_id: UUID4

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Series:
        # TODO: Consider JIT creation instead
        parent = Series.from_id_or_exception(values['series_id'])
        return parent

    @property
    def title(self) -> str:
        return self.name

    @property
    def author(self) -> Author:
        return Author.from_id_or_exception(datastore_id=self.author_id)


# Literal can take a tuple but it's a little too dynamic for mypy
# Has to be ignored when used elsewhere for the same reason
CategoriesLiteral = Literal[tuple(DatastoreModel.subclasses())]  # type: ignore
