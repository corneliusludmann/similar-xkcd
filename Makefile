.PHONY: serv
serv:
	pipenv run python3 main.py serv

.PHONY: crawl
crawl:
	pipenv run python3 main.py crawl

.PHONY: yapf
yapf:
	pipenv run yapf -ri --parallel --exclude '.venv/**/*.py' .

.PHONY: prepare
prepare:
	pipenv install --dev
