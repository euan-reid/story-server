from __future__ import annotations

from typing import List, Literal

from pydantic import UUID4, validator

from datastore_model import DatastoreModel


class Author(DatastoreModel):
    @property
    def stories(self: Author) -> List[Story]:
        return self.children_of_type(Story)


class Universe(DatastoreModel):
    @property
    def series(self: Universe) -> List[Series]:
        return self.children_of_type(Series)


class Series(DatastoreModel):
    universe_id: UUID4

    @property
    def universe(self: Series) -> Universe:
        return Universe.from_id_or_exception(id=self.universe_id)

    @property
    def stories(self: Series) -> List[Story]:
        return self.children_of_type(Story)

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Universe:
        parent = Universe.from_id(values['universe_id'])
        if parent is None:
            # TODO: Throw an error or trigger a JIT creation flow
            pass
        return parent


class Story(DatastoreModel):
    author_id: UUID4
    series_id: UUID4

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Series:
        parent = Series.from_id(values['series_id'])
        if parent is None:
            # TODO: Throw an error or trigger a JIT creation flow
            pass
        return parent

    @property
    def title(self: Story) -> str:
        return self.name

    @property
    def author(self: Story) -> Author:
        return Author.from_id_or_exception(id=self.author_id)


# Literal can take a tuple but mypy doesn't like it - tell mypy to be quiet
categories_literal = Literal[tuple(DatastoreModel.subclasses)]  # type: ignore
