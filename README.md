# arxiv-sanity
arXiv feed tool that heavily inspired by Arxiv Sanity Preserver

![Index page](screenshot.png)

This project manages dependencies with Poetry (https://github.com/sdispater/poetry), so you can install with Poetry.

> poetry shell
> poetry install

You will need arXiv databases. You can download it at https://github.com/rosinality/arxiv-sanity/releases/tag/v1.0

Now you can run web server with server.py:

> python server.py

Web server will serves at localhost:8000.

You can update arXiv databases with fetcher.py

> python fetcher.py

I recommend you to schedule this scripts daily for make database up-to-date, by using tools like cron.