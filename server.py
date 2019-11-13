import re
import logging
from math import ceil
from datetime import datetime

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import uvicorn
from gensim.summarization.summarizer import summarize

from model import Papers, database

templates = Jinja2Templates(directory='templates')

app = Starlette(debug=False)
app.mount('/static', StaticFiles(directory='static'), name='static')


def unix_to_date(unixtime):
    return datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d')


@app.route('/mark/{id}/{state}')
async def mark(request):
    state_map = {'none': 0, 'read': 1, 'later': 2}

    state = request.path_params['state']
    id = request.path_params['id']

    query = Papers.update(state=state_map[state]).where(Papers.id == id)
    query.execute()

    return PlainTextResponse(state)


def make_page_list(page, min_page, max_page, expected_length):
    pages = []

    left_margin = max(min_page, page - (expected_length - 1) // 2)
    right_margin = min(max_page, page + (expected_length - 1) // 2) + 1
    for index, i in enumerate(range(left_margin, right_margin)):
        pages.append(i)

    len_page = len(pages)
    if len_page < expected_length:
        for i in range(
            right_margin, min(max_page, right_margin + expected_length - len(pages))
        ):
            pages.append(i)

        right_page = []

        if len(pages) > 0:
            for i in range(
                max(min_page, left_margin - expected_length + len(pages)), pages[0]
            ):
                right_page.append(i)
            pages = right_page + pages

    if len(pages) > 0 and pages[0] > 1:
        if pages[0] > 2:
            pages = ['...'] + pages

        pages = [1] + pages

    if len(pages) < 1:
        pages = [1] + pages

    if len(pages) > 0:
        if pages[-1] < max_page:
            if pages[-1] < max_page - 1:
                pages = pages + ['...']

            pages = pages + [max_page]

    return pages


def get_page(request, mark='all', page=1):
    paper_per_page = 10

    state_map_rev = {'none': 0, 'read': 1, 'later': 2}
    state_map = {0: 'none', 1: 'read', 2: 'later'}

    keyword = request.query_params.get('search')

    try:
        keyword = request.query_params['search']
        keywords = keyword.split()

    except KeyError:
        keywords = None

    # papers = Papers.select(Papers, fn.COUNT(SQL('*')).over().alias('n_paper'))
    papers = Papers.select()

    if mark != 'all':
        papers = papers.where(Papers.state == state_map_rev[mark])

    if keywords is not None:
        for keyword in keywords:
            papers = papers.where(Papers.title ** f'%{keyword}%')

    '''if len(papers) > 0:
        n_paper = papers[0].n_paper

    else:
        n_paper = 0'''
    n_paper = papers.count()

    max_page = ceil(n_paper / paper_per_page)

    papers = papers.order_by(Papers.updated.desc()).paginate(page, paper_per_page)

    records = []

    for paper in papers.iterator():
        summary = paper.summary.replace('\n', ' ')

        try:
            summary_short = summarize(summary)

        except (ValueError, TypeError) as _:
            summary_short = summary

        title = paper.title

        if keywords is not None:
            for keyword in keywords:
                title = re.sub(
                    f'({keyword})',
                    r'<span class="found">\1</span>',
                    title,
                    flags=re.IGNORECASE,
                )

        records.append(
            {
                'id': paper.id,
                'title': title,
                'category': paper.category,
                'summary': paper.summary,
                'summary_short': summary_short,
                'authors': paper.authors,
                'version': paper.version,
                'published': unix_to_date(paper.published),
                'updated': unix_to_date(paper.updated),
                'state': state_map[paper.state],
                'new': paper.new,
            }
        )

    pages = make_page_list(page, 1, max_page, expected_length=5)

    del papers

    search_query = ''
    if keywords is not None:
        search_query = '?search=' + request.query_params['search']

    # database.close_all()

    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'n_paper': n_paper,
            'searched': True if keyword is not None else False,
            'search_query': search_query,
            'papers': records,
            'total_page': max_page,
            'current_page': page,
            'mark': mark,
            'pagination': pages,
            'prev_page': max(1, page - 1),
            'next_page': max(1, min(max_page, page + 1)),
        },
    )


@app.route('/')
@app.route('/{mark}')
@app.route('/{page:int}')
@app.route('/{mark}/{page:int}')
async def index(request):
    mark = request.path_params.get('mark', 'all')
    page = request.path_params.get('page', 1)

    response = get_page(request, mark, page)

    return response


@app.on_event('shutdown')
def shutdown():
    database.close()


if __name__ == '__main__':
    logger = logging.getLogger('gensim')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.ERROR)

    uvicorn.run(app, host='0.0.0.0', port=8000)
