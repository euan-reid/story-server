"""Define types of data we store and their heirarchy."""
from __future__ import annotations

from typing import List, Literal

from pydantic import UUID4, validator

from datastore_model import DatastoreModel


class Author(DatastoreModel):
    """Represent an individual author."""

    @property
    def stories(self) -> List[Story]:
        """Fetch stories written by this author."""
        return self.children_of_type(Story)


class Universe(DatastoreModel):
    """Represent a universe one or more series is set in."""

    @property
    def series(self) -> List[Series]:
        """Fetch series set in this universe."""
        return self.children_of_type(Series)


class Series(DatastoreModel):
    """Represent an individual series of stories."""

    universe_id: UUID4

    @property
    def universe(self) -> Universe:
        """Fetch the universe this series is set in."""
        return Universe.from_id_or_exception(datastore_id=self.universe_id)

    @property
    def stories(self) -> List[Story]:
        """Fetch the story or stories in this series."""
        return self.children_of_type(Story)

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Universe:
        """Determine the parent universe to use for the datastore key."""
        # TODO: Consider JIT creation instead
        parent = Universe.from_id_or_exception(values['universe_id'])
        return parent


class Story(DatastoreModel):
    """Represent an individual story."""

    author_id: UUID4
    series_id: UUID4

    @validator('parent', always=True)
    def set_parent(cls, _, values) -> Series:
        """Determine the parent series to use for the datastore key."""
        # TODO: Consider JIT creation instead
        parent = Series.from_id_or_exception(values['series_id'])
        return parent

    @property
    def title(self) -> str:
        """Sugar: Return the story's name/title."""
        return self.name

    @property
    def author(self) -> Author:
        """Return the story's author."""
        return Author.from_id_or_exception(datastore_id=self.author_id)


# Literal can take a tuple but it's a little too dynamic for mypy
# Has to be ignored when used elsewhere for the same reason
CategoriesLiteral = Literal[tuple(DatastoreModel.subclasses())]  # type: ignore
