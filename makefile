.PHONY: activate despesa

download:
	ckanapi dump datasets --remote https://dados.mg.gov.br/ --datapackages=datasets despesa

load: 
	python -m dadosmg.load data-raw/despesa/data/ db.duckdb

transform:
	python -m dadosmg.transform db.duckdb ft_despesa
	python -m dadosmg.transform db.duckdb dm_empenho_desp

all: load transform
	