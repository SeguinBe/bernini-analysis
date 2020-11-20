import pandas as pd
from .model import *


def parse_df(df: pd.DataFrame) -> BooksComparison:
    domenico_book = Book(shorthand='domenico', author='Domenico Bernini', title='TEST', year=1713)
    baldinucci_book = Book(shorthand='baldinucci', author='Baldinucci', title='TEST', year=1682)
    # TODO add book structure

    books_by_sh = {b.shorthand: b for b in [domenico_book, baldinucci_book]}
    left_sh = 'domenico'
    right_sh = 'baldinucci'

    def _parse_passage(r, key):
        return Passage(book=books_by_sh[key],
                       begin_c=r[key + '.begin'],
                       end_c=r[key + '.end'],
                       image_number=r[key + '.image_number'],
                       text=r[key + '.text'],
                       entities=r['entity_' + key],
                       works=r['work_' + key],
                       form=r['form_' + key],
                       content=r['content_' + key],
                       )

    matches = []
    for _id, r in df.iterrows():
        assert isinstance(_id, int)
        p1 = _parse_passage(r, left_sh)
        p2 = _parse_passage(r, right_sh)
        m = Match(id=_id, left=p1, right=p2, raw_data=r,
                  meta={k[len('meta.'):]: v for k, v in r.items() if k.startswith('meta.')},
                  irrelevant=r.irrelevant
                  )
        matches.append(m)

    return BooksComparison(book_left=books_by_sh[left_sh], book_right=books_by_sh[right_sh], matches=matches)


def parse_csv(filename: str) -> BooksComparison:
    df = pd.read_csv(filename, skiprows=1, index_col=1)
    return parse_df(df)
