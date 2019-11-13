import argparse
import random
import sys
from time import mktime, sleep

import peewee
import feedparser

from model import Papers, Authors


def insert_entry(id, version, entry, update=False):
    published = int(mktime(entry['published_parsed']))
    summary = entry['summary']
    title = entry['title']
    updated = int(mktime(entry['updated_parsed']))
    category = entry['arxiv_primary_category']['term']
    authors = [author['name'] for author in entry['authors']]
    authors_str = ', '.join(authors)

    if update:
        Papers.update(
            version=version,
            category=category,
            title=title,
            authors=authors_str,
            published=published,
            updated=updated,
            summary=summary,
        ).where(Papers.id == id).execute()

    else:
        Papers.create(
            id=id,
            version=version,
            category=category,
            title=title,
            authors=authors_str,
            published=published,
            updated=updated,
            summary=summary,
        )


def insert_authors(id, authors, update=False):
    if update:
        Authors.delete().where(Authors.paper == id).execute()

    authors = [(author, id) for author in authors]

    Authors.insert_many(authors, fields=[Authors.author, Authors.paper]).execute()


def parse_arxiv_id(id):
    split = id.rfind('/')
    id_ver = id[split + 1 :]
    id_ver = id_ver.rsplit('v', 1)

    assert len(id_ver) == 2, 'id is malformed: ' + id

    return id_ver[0], int(id_ver[1])


def _print(string):
    sys.stdout.write(string)
    sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_id', type=int, default=0, help='index of start scraping from'
    )
    args = parser.parse_args()

    query = (
        'cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:stat.ML'
    )
    start_id = args.start_id
    max_id = 70000
    max_results = 100

    Papers.update({'new': 0}).execute()

    n_insert_total = 0
    n_update_total = 0
    n_skip_total = 0

    for i in range(start_id, max_id, max_results):
        url = f'http://export.arxiv.org/api/query?search_query={query}&sortBy=lastUpdatedDate&start={i}&max_results={max_results}'
        entries = feedparser.parse(url)

        n_update = 0
        n_skip = 0
        n_insert = 0

        for entry in entries['entries']:
            id, version = parse_arxiv_id(entry['id'])
            authors = [author['name'] for author in entry['authors']]

            try:
                insert_entry(id, version, entry)
                insert_authors(id, authors)

            except peewee.IntegrityError:
                prev_version = Papers.get_by_id(id).version

                if prev_version < version:
                    insert_entry(id, version, entry, True)
                    insert_authors(id, authors, True)

                    n_update += 1
                    n_update_total += 1

                elif prev_version > version:
                    n_skip += 1
                    n_skip_total += 1

            else:
                n_insert += 1
                n_insert_total += 1

        n_fetched = len(entries['entries'])

        print(
            (
                f'{i}/{max_id}; '
                f'Fetched: {n_fetched}; '
                f'Inserted: {n_insert}/{n_insert_total}; '
                f'Updated: {n_update}/{n_update_total}; '
                f'Skipped: {n_skip}/{n_skip_total}'
            )
        )

        if n_fetched == 0:
            print('Fetched zero entries. Maybe rate limiting. Please try later.')
            break

        if n_insert == 0 and n_update == 0:
            print(
                'Inserted or updated zero entries. Maybe there are no new updates. Exiting.'
            )
            break

        for i in range(5 + int(random.uniform(0, 3))):
            _print('.')
            sleep(1)

        print()
