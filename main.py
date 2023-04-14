import duckdb
import logging
from pathlib import Path

def drop_tables(DB_NAME, con=None):

    tables_list = con.execute("""SHOW TABLES""").fetchall()
    if tables_list:
        for table_name in tables_list:
            con.execute(f"""DROP TABLE {table_name[0]} """)
            logging.info(f"Tabela {table_name} apagada.")
    else:
        logging.info(f"Não há tabelas na database {DB_NAME}")


def tables_from_csv(con, file_paths):

    for file in file_paths:
        name = file.stem.rstrip('.csv')
        con.execute(f"""CREATE TABLE '{name}' AS SELECT * FROM read_csv_auto('{file}')""")
        logging.info(f"Arquivo {file} carregado para tabela {name}")

def append_from_csv(con, file_paths_append, tbl_agg_name):
    num_linhas = 0
    exec_error = False
    files_error = []

    #Toma o primeiro arquivo da lista de csvs como definidor dos nomes das colunas e tipos
    temp_csv = con.sql(f"""SELECT * FROM '{list(file_paths_append)[0]}' LIMIT 10 """)

    # cria lista contendo nomes e tipos das colunas lidas em temp_csv
    table_columns = [str(temp_csv.columns[i] + ' ' + temp_csv.dtypes[i]) for i in range(len(temp_csv.columns))]

    # Concatena lista de strings em uma string somente para uso na criação da tabela nova.
    table_columns = ', '.join(table_columns)

    # Cria tabela para agregar arquivos CSV de faturamento
    con.execute(f"""CREATE TABLE '{tbl_agg_name}'({table_columns}) """)
    logging.info(f'Tabela {tbl_agg_name} criada')

    for file in file_paths_append:
        logging.info(f'Lendo:{file}')
        df1 = con.execute(f"""SELECT * FROM '{file}' """).df()
        try:
            con.execute(f"""INSERT INTO '{tbl_agg_name}' SELECT * FROM df1""")
            logging.info(f'Arquivo {file} concatenado na tabela {tbl_agg_name}')

        except:
            logging.error(f"Arquivo {file} está vazio ou contém schema divergente dos demais.")
            exec_error = True
            files_error.append(file)


        num_linhas += len(df1)

    logging.info(f'Total de linhas tabelas lidas: {num_linhas}')

    # alerta para falha no carregamento de arquivos. Arquivos somente com cabeçalhos geram esse erro.
    if exec_error:
        logging.warn(f"Os seguintes arquivos não foram carregados para a base de dados: {files_error}")

def descbribe_db(con=None):
    print(con.sql("DESCRIBE"))


def describe_table(con, table_name):
    print(con.table(table_name).describe())


def group_by_field(con, table_name, field_agg, field_values):

    rel = con.sql(f"""SELECT * FROM {table_name}""")
    agg = rel.aggregate(f"{field_agg} AS 'agregado', sum({field_values}), count({field_agg})")
    print(agg)

def main():
    DB_NAME = 'database/dadosmg.duckdb'
    DATASETS_DIR = 'despesa/'
    DATASET_DIR = 'datasets/'
    DATA_DIR = 'data/'
    data_path = Path(DATASET_DIR, DATASETS_DIR, DATA_DIR)

    # obtem lista de paths para arquivos CSV localizados no caminho DATA_PATH
    file_paths = data_path.glob('*.csv.gz')

    # paths de bases csv que sao separadas por anos
    file_paths_desp = list(data_path.glob('dm_empenho_desp_*'))
    file_paths_ft = list(data_path.glob('ft_despesa_*'))

    # paths de bases csv que não são separadas por anos
    file_paths = list(set(file_paths) - set(file_paths_desp) - set(file_paths_ft))

    # True Dropa todas as tabelas atuais da database
    DROP_TABLES = True

    con = duckdb.connect(DB_NAME) #Cria se não existe e se conecta à base de dados

    if DROP_TABLES:
        drop_tables(DB_NAME, con)

    tables_from_csv(con, file_paths)

    append_from_csv(con, file_paths_desp, 'dm_empenho_desp')
    append_from_csv(con, file_paths_ft, 'ft_despesa')

if __name__ == '__main__':
    
    LOG_FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
