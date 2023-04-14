# DuckDB

## Capacidades

"_DuckDB is the SQLite for Analytics._"


- Consegue rodar comandos SQL em dataframes pandas diretamente.
- Pode carregar dados de arquivos CSV compactados como gzip diretamente, que é o caso do portal dados mg.
- É altamente otimizado para consultas analítica (OLAP), pois é um banco de dados orientado a colunas.
- Ao invés de usar pandas e numpy para carregar e tratar dados o DuckDB pode ser utilizado para isso, mas com todas as vantagens de se usar um RDBMS.
- Não necessita de interfaces client/server e não possui dependências externas.
- Para este projeto em questão, o DuckDB parece se adequar mais que o SQLite, por ser [otimizado para uso em aplicação analíticas (OLAP)](https://simonwillison.net/2022/Sep/1/sqlite-duckdb-paper/#:~:text=While%20the%20performance%20gap%20has,ground%20up%20for%20efficient%20OLAP.).


## Limitações
- Foi desenvolvido para rodar em uma máquina somente.
- Não se trata de uma multi-tenant database. Cada usuário tem de ter sua cópia da base de dados (o uso de  Airflow, S3, Parquet and DBT pode mitigar essas limitações).
- Não deve ser usada como base de dados transacional. No caso deste projeto, a construção de um data warehouse não enseja nessa necessidade.



## Instalação no Windows

Após clonar o projeto, seguir as etapas a seguir.


### Criar ambiente virtual do projeto
```python
cd diretorio/do/projeto
python -m venv venv
```

### Ativar ambiente virtual do projeto

Linha de comando no Windows:
```cmd
cd diretorio/do/projeto
venv\Scripts\activate
```

Git bash:
```gitbash
cd diretorio/do/projeto
source venv\Scripts\activate
```

### Instalar requerimentos
```python
pip install -r requirements.txt
```

### Instalar Jupyter Notebook (opcional)
```python
pip install notebook
```

## Execução no Python

### Ativar o ambiente virtual. 

Linha de comando no Windows:
```cmd
cd diretorio/do/projeto
venv\Scripts\activate
```

Git bash:
```gitbash
cd diretorio/do/projeto
source venv\Scripts\activate
```

### Executar makefile

Baixar arquivos tar.gz do portal dadosmg:  
```python
make download
```

Executar script de carga de dados.  
```python
make run
```

Fazer download dos arquivos e executar o script de carga de dados.
```python
make all
```

## Execução no Jupyter Notebook

Ativar o ambiente virtual:
```gitbash
cd diretorio/do/projeto
source venv\Scripts\activate
```

Baixar os arquivos csv.gz do portal [dadosmg](https://dados.mg.gov.br/dataset/despesa), salvá-los na pasta \datasets e extrair todos os arquivos csv. Após isso abrir o notebook 'dadosmg_basics.ipynb' no jupyter e executar.  

**NOTA**: Durante os testes realizados o kernel do Jupyter se mostrou instável, não conseguindo importar os dados corretamente e reiniciando durante o processo. Logo é recomendado utilizá-lo para consultas e análises, mas no momento não mais para realizar as cargas de dados. O arquivo 'dadosmg_basics.ipynb' contém snippets de manipulações básicas utilizando o DuckDB em python.


## Visualização de Dados

A ferramenta open source [TAD Viewer](https://www.tadviewer.com/) pode ser utilizada para visualizar a base de dados do DuckDB ou arquivos csv, parquet, json antes ou durante o processo de importação.

![imagem](images/tad-home.png)
