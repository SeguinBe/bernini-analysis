import attr
from typing import List


@attr.s
class Book:
    shorthand: str = attr.ib()
    author: str = attr.ib()
    title: str = attr.ib()
    year: int = attr.ib()
    structure: List = attr.ib(default=list)

    def short_descriptor(self) -> str:
        return f"{self.author}, {self.year}"


@attr.s
class Passage:
    book: Book = attr.ib()
    begin_c: int = attr.ib()
    end_c: int = attr.ib()
    image_number: int = attr.ib()
    text: str = attr.ib()

    # annotations
    entities: List = attr.ib(default=list)
    works: List = attr.ib(default=list)
    form = attr.ib(default=None)
    content = attr.ib(default=None)
    grouping = attr.ib(default=None)
    service = attr.ib(default=None)
    place = attr.ib(default=None)


@attr.s
class Match:
    id: int = attr.ib()
    meta: dict = attr.ib()
    left: Passage = attr.ib()
    right: Passage = attr.ib()
    raw_data = attr.ib(repr=False)  # Original dataframe row

    # annotations
    irrelevant: bool = attr.ib()


@attr.s
class BooksComparison:
    book_left: Book = attr.ib()
    book_right: Book = attr.ib()
    matches: List[Match] = attr.ib(default=list)
