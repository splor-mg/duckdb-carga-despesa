.PHONY: activate despesa

download:
	ckanapi dump datasets --remote https://dados.mg.gov.br/ --datapackages=datasets despesa

load: 
	python -m dadosmg.load

transform:
	python -m dadosmg.transform ft_despesa
	python -m dadosmg.transform dm_empenho_desp

all: load transform
	