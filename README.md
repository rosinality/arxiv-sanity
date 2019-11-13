# arxiv-sanity
arXiv feed tool that heavily inspired by Arxiv Sanity Preserver

![Index page](screenshot.png)

This project manages dependencies with Poetry (https://github.com/sdispater/poetry), so you can run web server using Poetry:

> poetry shell
> python server.py

Web server will serves at localhost:8000.

You can update arXiv databases with fetcher.py

> python fetcher.py

I recommend you to schedule this scripts daily for make database up-to-date, by using tools like cron.