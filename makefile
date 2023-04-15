.PHONY: activate despesa

download:
	ckanapi dump datasets --remote https://dados.mg.gov.br/ --datapackages=datasets despesa

load: 
	python main.py

all: load
	