.PHONY: activate despesa

download:
	ckanapi dump datasets --remote https://dados.mg.gov.br/ --datapackages=datasets despesa

load: 
	python main.py

transform:
	cat transform.sql | duckdb database/dadosmg.duckdb

all: load transform
	