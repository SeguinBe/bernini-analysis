import attr
from typing import List, Optional, Dict
from collections import defaultdict
from enum import Enum
from IPython.display import HTML, display


@attr.s
class BookSection:
    # TODO somehow these can be float??
    page_number_begin: int = attr.ib()
    page_number_end: int = attr.ib()
    image_number_begin: int = attr.ib()
    image_number_end: int = attr.ib()
    name: str = attr.ib()
    name_id: str = attr.ib(default="")
    id: Optional[int] = attr.ib(default=None)


@attr.s
class Book:
    shorthand: str = attr.ib()
    author: str = attr.ib()
    title: str = attr.ib()
    year: int = attr.ib()
    nb_images: int = attr.ib(default=0)
    nb_pages: int = attr.ib(default=0)
    pageimage_offset: int = attr.ib(default=0)

    text: str = attr.ib(default='', repr=False)

    sections_sequences: Dict[str, List[BookSection]] = attr.ib(default=defaultdict(list))

    def short_descriptor(self) -> str:
        return f"{self.author}, {self.year}"

    @property
    def chapter_sections(self) -> List[BookSection]:
        return self.sections_sequences['chapters']

    @property
    def patron_sections(self) -> List[BookSection]:
        return self.sections_sequences['patrons']


@attr.s(hash=True)
class EntityMention:
    name: str = attr.ib()
    confident: bool = attr.ib(default=True)

    @classmethod
    def merge_list(cls, l: List['EntityMention']) -> List['EntityMention']:
        c = defaultdict(lambda: False)
        for e in l:
            c[e.name] |= e.confident
        return [EntityMention(name=k, confident=v) for k, v in c.items()]


def _parse_entity_mentions(s: str) -> List[EntityMention]:
    if s in ('[]', '', '[]?', '?', None):
        return []

    l = [ss.strip() for ss in s.split(',')]
    result_entities = []
    for e in l:
        if e.endswith('?'):
            result_entities.append(EntityMention(name=e[:-1], confident=False))
        else:
            result_entities.append(EntityMention(name=e, confident=True))
    return result_entities


def _parse_list(s: str) -> List[str]:
    if s in ('[]', '', '[]?', '?', None):
        return []

    l = [ss.strip() for ss in s.split(',')]
    result = []
    for e in l:
        if e == '':
            continue
        if e.endswith('?'):
            result.append(e[:-1])
        else:
            result.append(e)
    return result


def _parse_optional_entity(s: str) -> Optional[EntityMention]:
    tmp = _parse_entity_mentions(s)
    if len(tmp) == 0:
        return None
    else:
        return tmp[0]


class NarratorType(Enum):
    AUTHOR = 1
    BERNINI = 2
    THIRD_PARTY = 3


@attr.s
class Passage:
    book: Book = attr.ib(repr=lambda b: b.shorthand)
    begin_c: int = attr.ib()
    end_c: int = attr.ib()
    image_number: int = attr.ib()
    text: str = attr.ib()

    # annotations
    persons: List[EntityMention] = attr.ib(default=list)
    works: List[EntityMention] = attr.ib(default=list)
    form: List[str] = attr.ib(default=None)
    content: List[str] = attr.ib(default=None)
    grouping = attr.ib(default=None)
    patron: Optional[EntityMention] = attr.ib(default=None)
    place: Optional[EntityMention] = attr.ib(default=None)

    def __attrs_post_init__(self):
        # parse the list properly
        self.persons = _parse_entity_mentions(self.persons)
        self.works = _parse_entity_mentions(self.works)
        self.form = _parse_list(self.form)
        self.content = _parse_list(self.content)
        self.patron = _parse_optional_entity(self.patron)
        self.place = _parse_optional_entity(self.place)

    #TODO Name it better
    @property
    def narrator(self) -> Optional[NarratorType]:
        for c in self.content:
            if c.startswith('a_'):
                return NarratorType.AUTHOR
            elif c.startswith('b_'):
                return NarratorType.BERNINI
            elif c.startswith('c_'):
                return NarratorType.THIRD_PARTY
        return None


@attr.s
class Match:
    id: int = attr.ib()
    meta: dict = attr.ib()
    left: Passage = attr.ib()
    right: Passage = attr.ib()
    raw_data = attr.ib(repr=False)  # Original dataframe row

    # annotations
    irrelevant_type: str = attr.ib()

    @property
    def irrelevant(self) -> bool:
        return not(self.irrelevant_type.startswith('FALSE') or self.irrelevant_type.startswith('FALSO'))

    @property
    def all_persons(self) -> List[EntityMention]:
        return EntityMention.merge_list(self.left.persons + self.right.persons)

    @property
    def all_works(self) -> List[EntityMention]:
        return EntityMention.merge_list(self.left.works + self.right.works)

    @property
    def place(self) -> Optional[EntityMention]:
        if self.left.place:
            return self.left.place
        else:
            return self.right.place

    @property
    def patron(self) -> List[EntityMention]:
        list_mentions = []
        if self.left.patron is not None:
            list_mentions.append(self.left.patron)
        if self.right.patron is not None:
            list_mentions.append(self.left.patron)
        return EntityMention.merge_list(list_mentions)

    @property
    def form(self) -> List[str]:
        return list(set(self.left.form + self.right.form))

    @property
    def content(self) -> List[str]:
        return list(set(self.left.content + self.right.content))

    @property
    def common_entities(self) -> List[EntityMention]:
        raise NotImplementedError

    def display(self, context=300):
        def _make_str(p: Passage):
            s = f"""
            <em>{p.book.text[max(0, p.begin_c-context):p.begin_c]}</em>
            <strong>{p.book.text[p.begin_c:p.end_c]}</strong>
            <em>{p.book.text[p.end_c:min(len(p.book.text)-1, p.end_c + context)]}</em>
            """
            return s

        text = f"""
         <table style="width:100%; text-align:left;">
          <tr>
            <th>{self.left.book.short_descriptor()} | (#{self.left.image_number})</th>
            <th>{self.right.book.short_descriptor()} | (#{self.right.image_number})</th>
          </tr>
          <tr>
            <td style="text-align:justify;">
                {_make_str(self.left)}
            </td>
            <td style="text-align:justify;">
                {_make_str(self.right)}
            </td>
          </tr>
          <tr>
            <td style="text-align:justify;">
            </td>
            <td style="text-align:right;"><a href="{self.raw_data['link']}" target="_blank">Link</a>   id={self.id}</td>
          </tr>
        </table> 
        """
        display(HTML(text))


@attr.s
class BooksComparison:
    book_left: Book = attr.ib()
    book_right: Book = attr.ib()
    matches: List[Match] = attr.ib(default=list)
