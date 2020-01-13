[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/corneliusludmann/similar-xkcd) 

# Similar xkcd comic
This project calculates [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) similarities between [xkcd comics ](https://xkcd.com/) based on the descriptions of [explain xkcd](https://www.explainxkcd.com/).

## Prerequisites

- Python 3
- [pipenv](https://github.com/pypa/pipenv)

Initialize pipenv virtual environment:
```shell
$ pipenv --three
```

Install [YAPF](https://github.com/google/yapf):
```shell
$ pipenv install --dev yapf
```

Reformat code, eg.:
```shell
$ pipenv run yapf -ri --parallel --exclude '.venv/**/*.py' .
```

## Run
```shell
$ pipenv run python3 main.py
```

## Create a Crawler for Explain xkcd

Install [scrapy](https://scrapy.org/):
```shell
$ pipenv install scrapy
```

Run scrapy:
```shell
$ mkdir data
$ rm -f data/xkcd.json && pipenv run scrapy runspider explainxkcd-crawler/explainxkcd-spider.py -o data/xkcd.json -t jsonlines -L 'WARNING'
```

## Generate HTML
```shell
$ pipenv install nltk
$ pipenv install scikit-learn
$ pipenv install scipy
```

```shell
$ pipenv shell
$ ./venv/bin/python3
>>> import nltk
>>> nltk.download('punkt')
```

```shell
$ cd infinite_xkcd && ../.venv/bin/python3 generate_html_ajax.py ../data/xkcd.json gen
$ curl https://getcaddy.com | bash -s personal  # do this once, ignore errors
$ cd gen && /tmp/caddy
```