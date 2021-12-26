# RSS News Parser
RSS News Parser is implemented for fetching news from various RSS Feeds.

It works with RSS2.0 standard (https://www.rssboard.org/rss-specification).

It works either as CLI, or as Flask server.
Cached news from CLI and Flask are not related.

This package allows to:

1) Parse rss feed _(Internet connection required)_.
2) Search local storage for specified rss feed source and/or specific date.
3) Display news in as JSON-object or in human-readable style.
4) Limit number of displayed news.
5) Convert news to HTML and/or PDF and save files at specified directory.
6) Colorize displayed news both for JSON and human-readable style.

# Requirements
Common - Python's version 3.9 or higher (visit https://www.python.org/downloads/)

Additional for Flask server - Docker (https://docs.docker.com/engine/) or Docker Compose (https://docs.docker.com/compose/install/)  
# Installation
1) Download files from GitHub.
2) Unpack files to preferred directory.
3) Open this directory in terminal.
4) For Linux:
```bash
  $ pip install . #default Python 3
  $ python3.9 setup.py install  # specifically Python 3.9
```
4) For Windows:
```cmd
  > py -m setup.py install
```
# Usage
## CLI
```bash
$ cd rss_reader
$ python3 rss_reader.py source [-h] [--version] [--json] [--verbose] [--limit LIMIT]

or 

From any location
$ rss_reader source [-h] [--version] [--json] [--verbose] [--limit LIMIT] [--date DATE]

usage: RSS Parser source [-h] [--version] [--json] [--verbose] [--limit LIMIT]
                  [--date DATE] [--to-html TO_HTML] [--to-pdf TO_PDF]
                  [--colorize]
                  

Pure Python command-line RSS reader.

positional arguments:
  source             RSS URL

optional arguments:
  -h, --help         show this help message and exit
  --version          Print version info
  --json             Print result as JSON in stdout
  --verbose          Outputs verbose status messages
  --limit LIMIT      Limit news topics if this parameter provided
  --date DATE        Searches local storage for cached news for particular
                     date. DATE format is YYMMDD
  --to-html TO_HTML  Converts fetched news to html file at specified directory
  --to-pdf TO_PDF    Converts fetched news to pdf file at specified directory
  --colorize         Outputs news in colored mode



```
## --json
With this option specified, news are displayed as JSON-object (list of dictionaries), for example:
```bash
[
    {
        "Rss Feed": "Lenta.ru : Новости",
        "Title": "Олимпийский чемпион придумал наказания для футболистов российских клубов",
        "Description": "Футболистов российских клубов, выступающих в еврокубках, нужно заставить нормально 
        тренироваться. Об этом рассказал четырехкратный олимпийский чемпион по биатлону Александр Тихонов. 
        Спортсмен также придумал наказания для игроков. Среди них биатлонист упомянул лишение зарплаты на 
        несколько месяцев.",
        "Date": "Fri, 22 Oct 2021 19:38:18 +0300",
        "Link": "https://lenta.ru/news/2021/10/22/nakazany/",
        "Image": "https://icdn.lenta.ru/images/2021/10/22/19/20211022191141126/pic_8e08dd360daac88ed9700b070eddd475.jpg"
    },
    {
        "Rss Feed": "Lenta.ru : Новости",
        "Title": "Британцы скрывались пять часов от полиции ради эффектного фото на фоне вулкана",
        "Description": "Четыре туриста из Великобритании придумали хитроумный план обхода полиции, чтобы 
        сфотографироваться на фоне извергающегося вулкана Кумбре-Вьеха на острове Пальма (Канарские острова). 
        Один из членов группы опубликовал фото с товарищами на фоне расплавленной лавы в своих соцсетях.",
        "Date": "Fri, 22 Oct 2021 19:37:00 +0300",
        "Link": "https://lenta.ru/news/2021/10/22/likesharerepost/",
        "Image": "https://icdn.lenta.ru/images/2021/10/22/18/20211022180628763/pic_a7dcdc388e7dcd30e3a2902b7f57c8ff.jpeg"
    }
]
```
## --verbose
This option allows tracking logging information, for example:
```bash
22/10/2021 - 19:38:41 INFO    :.main: RSS News Parser started
```
## News caching
Each time you run rss_reader, it caches news from source according to their publication date and RSS feed.
Local news files are stored at package installation folder:
```bash
./cached/YYYYMMDD/https:__source_rss.json
```
as JSON-objects
## --date
This option allows searching local storage (no Internet connection required) either from specified rss feed soure,
or without it. 
On the first case, rss_parser will display all news (or with limit option) from particular rss feed source
on particular date (will read one file rss_feed.json from YYYYMMDD folder). 
On the second case, rss_parser will fetch all news on particular date (will read all files from YYYYMMDD folder).
Both implementation support other rss_parser options, e.g. --limit, --verbose etc.

## --to-html and --to-pdf
rss_parser supports news conversion to html and pdf files. As default, these files are called news and will be
stored at specified directory that was given (will be created if not exists). Both files support image download 
(Internet connection required) if they exist in news. By default, pdf file consist news, each one on their own page.

NOTE: due to requirements of pdf-convert engine, converting to pdf should be implemented in folder, which has 
Font file (DejaVuSans.ttf by default). 

The easiest way is to work from project folder
```bash
~/Python/final_task$ 

```
Or you should manually place Font file to the current working directory. Font file can be found either in project
folder, or in installed package folder.
You can easily find it with:
```bash
$ pip show rss_reader

Name: rss-reader
Version: 1.5
Summary: Pure Python command-line RSS reader.
Author: Daniil Tsybulnikau
Author-email: byhrodna@gmail.com
Location: /home/byhrodna/.local/lib/python3.8/site-packages

```

## --colorize
option to print news (both JSON and human-readable) in colored mode. This option doesn't affect news conversion to
html and pdf, and caching to local.

# Flask server
Flask server can be run as 3 separate Docker containers (final_task_nginx, final_task_flask, final_task_news_db).
- final_task_nginx image is used as a proxy server. It will receive HTTP requests and forward them onto 
Python application.
- final_task_flask image contains Python application running either on a uWSGI server or
on in-built Flask server (uWSGI by default). 

NOTE: 
If your want to run in-built Flask server go to ./Dockerfile, comment line 19 with leading # and 
uncomment lines 22 and 24, then go to ./nginx/Dockerfile, comment line 5 and uncomment line 7.

- final_task_news_db image is the latest Postgres image from Docker hub, used to serve our database.

## Usage
- With Docker compose:
1) In terminal head to /final_task.
2) Type:
```bash
$ docker-compose up --build -d
$ docker-compose up --build
```
3) Done

- With separate Docker Images:
1) In terminal head to /final_task.
2) Build images for flask app and nginx:
```bash
$ docker build -f docker/nginx/Dockerfile -t final_task_nginx .
$ docker build -f Dockerfile -t final_task_flask .
```
3) Run containers:
```bash
$ docker run -d --name final_task_nginx -p 80:80 final_task_nginx
$ docker run -d --name final_task_flask -p 8080  --env-file .env final_task_flask
$ docker volume create --name db_volume
$ docker run -d --name final_task_news_db -p 5432:5432 --env-file .env -v db_volume:/var/lib/postgresql postgres:latest
```
4) Done

Go to http://localhost:8080 in browser to see greeting message.

Server API supports basic CRUD operations either from other applications, or by cURL.
Possible usage and examples can be seen at https://documenter.getpostman.com/view/16802653/UV5dcZEA


#### Unit testing
1) Go to final_task folder.
2) Run:
```bash
$ coverage run -m unittest discover
$ coverage report -m
```
Report:
```bash
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
rss_reader/app.py                  0      0   100%
rss_reader/src/app.py             11      6    45%   8-13
rss_reader/src/config.py          16      0   100%
rss_reader/src/models.py          14      1    93%   18
rss_reader/classmodule.py        246     95    61%   94, 103, 252-283, 293-330, 339-348, 364-390
rss_reader/rss_reader.py          41     33    20%   12-55, 59
rss_reader/tests/app.py            0      0   100%
rss_reader/tests/test_unit.py    150      1    99%   247
-------------------------------------------------------------
TOTAL                            478    136    72%

```