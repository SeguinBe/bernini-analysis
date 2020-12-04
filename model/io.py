import pandas as pd
import json
from .base import *


def _get_book_data(filename: str) -> (int, str):
    with open(filename, 'r') as f:
        d = json.load(f)
    return len(d['pages']), d['text']


def _add_structure_data(filename: str, b: Book):
    with open(filename, 'r') as f:
        d = json.load(f)
    b.pageimage_offset = d['pageimage_offset']
    b.nb_pages = d['page_number_max']
    b.sections_sequences['chapters'] = [BookSection(**s) for s in d['chapters']]
    b.sections_sequences['patrons'] = [BookSection(**s) for s in d['patrons']]


def parse_df(df: pd.DataFrame) -> BooksComparison:
    nb_images, text = _get_book_data('data/domenico.json')
    domenico_book = Book(shorthand='domenico', author='Domenico Bernini', title='TEST', year=1713,
                         text=text, nb_images=nb_images)
    nb_images, text = _get_book_data('data/baldinucci.json')
    baldinucci_book = Book(shorthand='baldinucci', author='Baldinucci', title='TEST', year=1682,
                           text=text, nb_images=nb_images)

    _add_structure_data('data/domenico_structure.json', domenico_book)
    _add_structure_data('data/baldinucci_structure.json', domenico_book)

    books_by_sh = {b.shorthand: b for b in [domenico_book, baldinucci_book]}
    left_sh = 'domenico'
    right_sh = 'baldinucci'

    def _parse_passage(r, key):
        return Passage(book=books_by_sh[key],
                       begin_c=r[key + '.begin'],
                       end_c=r[key + '.end'],
                       image_number=r[key + '.image_number'],
                       text=r[key + '.text'],
                       persons=r['person_' + key],
                       works=r['work_' + key],
                       form=r['form_' + key],
                       content=r['content_' + key],
                       patron=r['patron_' + key]
                       )

    matches = []
    for _id, r in df.iterrows():
        assert isinstance(_id, int)
        p1 = _parse_passage(r, left_sh)
        p2 = _parse_passage(r, right_sh)
        m = Match(id=_id, left=p1, right=p2, raw_data=r,
                  meta={k[len('meta.'):]: v for k, v in r.items() if k.startswith('meta.')},
                  irrelevant_type=r.irrelevant
                  )
        matches.append(m)

    return BooksComparison(book_left=books_by_sh[left_sh], book_right=books_by_sh[right_sh], matches=matches)


def parse_csv(filename: str) -> BooksComparison:
    df = pd.read_csv(filename, skiprows=1, index_col=1)
    return parse_df(df)
