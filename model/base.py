import attr
from typing import List, Optional
from collections import defaultdict
from enum import Enum
from IPython.display import HTML, display

display(HTML("""
<style>

</style>
"""))


@attr.s
class Book:
    shorthand: str = attr.ib()
    author: str = attr.ib()
    title: str = attr.ib()
    year: int = attr.ib()
    structure: List = attr.ib(default=list)
    nb_images: int = attr.ib(default=0)
    text: str = attr.ib(default='', repr=False)

    def short_descriptor(self) -> str:
        return f"{self.author}, {self.year}"


@attr.s(hash=True)
class EntityMention:
    name: str = attr.ib()
    confident: bool = attr.ib(default=True)


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
    entities: List[EntityMention] = attr.ib(default=list)
    works: List[EntityMention] = attr.ib(default=list)
    form: List[str] = attr.ib(default=None)
    content: List[str] = attr.ib(default=None)
    grouping = attr.ib(default=None)
    service: Optional[EntityMention] = attr.ib(default=None)
    place: Optional[EntityMention] = attr.ib(default=None)

    def __attrs_post_init__(self):
        # parse the list properly
        self.entities = _parse_entity_mentions(self.entities)
        self.works = _parse_entity_mentions(self.works)
        self.form = _parse_list(self.form)
        self.content = _parse_list(self.content)
        self.service = _parse_optional_entity(self.service)
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
    def all_entities(self) -> List[EntityMention]:
        c = defaultdict(lambda: False)
        for e in self.left.entities + self.right.entities:
            c[e.name] |= e.confident
        return [EntityMention(name=k, confident=v) for k, v in c.items()]

    @property
    def all_works(self) -> List[EntityMention]:
        c = defaultdict(lambda: False)
        for e in self.left.works + self.right.works:
            c[e.name] |= e.confident
        return [EntityMention(name=k, confident=v) for k, v in c.items()]

    @property
    def place(self) -> Optional[EntityMention]:
        #TODO correct this
        return self.left.place

    @property
    def service(self) -> Optional[EntityMention]:
        # TODO correct this
        return self.left.service

    @property
    def form(self) -> List[str]:
        return list(set(self.left.form+self.right.form))

    @property
    def content(self) -> List[str]:
        return list(set(self.left.form + self.right.form))

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
            <td style="text-align:right;">id={self.id}</td>
          </tr>
        </table> 
        """
        display(HTML(text))


@attr.s
class BooksComparison:
    book_left: Book = attr.ib()
    book_right: Book = attr.ib()
    matches: List[Match] = attr.ib(default=list)
