import pandas as pd
import glob
import duckdb
import os


DB_NAME = 'database/dadosmg.duckdb'
DATASETS_DIR = 'despesa/'
DATASET_DIR = 'datasets/'
DATA_DIR = 'data/'
DATA_PATH = DATASET_DIR + DATASETS_DIR + DATA_DIR

# obtem lista de paths para arquivos CSV localizados no caminho DATA_PATH
file_paths = [i.replace('\\', '/') for i in list(glob.iglob(f'{DATA_PATH}*.csv*'))]

# paths de bases csv que sao separadas por anos
file_paths_desp = [x for x in file_paths if "dm_empenho_desp_" in x]
file_paths_ft = [x for x in file_paths if "ft_despesa_" in x]

# paths de bases csv que não são separadas por anos
file_paths = list(set(file_paths) - set(file_paths_desp) - set(file_paths_ft))

# True Dropa todas as tabelas atuais da database
DROP_TABLES = True

def drop_tables(con=None):

    tables_list = con.execute("""SHOW TABLES""").fetchall()
    if tables_list:
        for table_name in tables_list:
            con.execute(f"""DROP TABLE {table_name[0]} """)
            print(f"Tabela {table_name} apagada.")
    else:
        print(f"Não há tabelas na database {DB_NAME}")


def tables_from_csv(file_paths):

    for file in file_paths:
        head, tail = os.path.split(file)
        name = tail.split('.')[0]
        _, file_extension = os.path.splitext(tail)
        con.execute(f"""CREATE TABLE '{name}' AS SELECT * FROM read_csv_auto('{file}')""")
        print(f"Arquivo {file} carregado para tabela {name}\n")

    print('-------------------------------------------------------\n')

def append_from_csv(file_paths_append, tbl_agg_name):
    #tbl_agg_name = 'ft_despesa'
    df_agg = pd.DataFrame()
    num_linhas = 0
    exec_error = False
    files_error = []

    #Toma o primeiro arquivo da lista de csvs como definidor dos nomes das colunas e tipos
    temp_csv = con.sql(f"""SELECT * FROM '{file_paths_append[0]}' LIMIT 10 """)

    # cria lista contendo nomes e tipos das colunas lidas em temp_csv
    table_columns = [str(temp_csv.columns[i] + ' ' + temp_csv.dtypes[i]) for i in range(len(temp_csv.columns))]

    # Concatena lista de strings em uma string somente para uso na criação da tabela nova.
    table_columns = ', '.join(table_columns)

    # Cria tabela para agregar arquivos CSV de faturamento
    con.execute(f"""CREATE TABLE '{tbl_agg_name}'({table_columns}) """)
    print(f'Tabela {tbl_agg_name} criada\n')

    for file in file_paths_append:
        print(f'Lendo:', file)
        df1 = con.execute(f"""SELECT * FROM '{file}' """).df()
        try:
            con.execute(f"""INSERT INTO '{tbl_agg_name}' SELECT * FROM df1""")
            print(f'Arquivo {file} concatenado na tabela {tbl_agg_name}\n')

        except:
            print(f"ERRO: Arquivo {file} está vazio ou contém schema divergente dos demais.\n")
            exec_error = True
            files_error.append(file)


        num_linhas += len(df1)

    print('-------------------------------------------------------')

    print('Total de linhas tabelas lidas:', num_linhas)
    #print('Num linhas da tabela agregada:')
    #print(con.sql(f"""SELECT COUNT(*) FROM {tbl_agg_name}"""))

    #con.table(tbl_agg_name).show()

    # alerta para falha no carregamento de arquivos. Arquivos somente com cabeçalhos geram esse erro.
    if exec_error:
        print(f"ATENÇÃO! os seguintes arquivos não foram carregados para a base de dados:")
        print(files_error, sep='\n')
        print('\n\n')


def descbribe_db(con=None):
    print(con.sql("DESCRIBE"))


def describe_table(con, table_name):
    print(con.table(table_name).describe())


def group_by_field(con, table_name, field_agg, field_values):

    rel = con.sql(f"""SELECT * FROM {table_name}""")
    agg = rel.aggregate(f"{field_agg} AS 'agregado', sum({field_values}), count({field_agg})")
    print(agg)


if __name__ == '__main__':
    con = duckdb.connect(DB_NAME) #Cria se não existe e se conecta à base de dados

    if DROP_TABLES:
        drop_tables(con)

    tables_from_csv(file_paths)

    append_from_csv(file_paths_desp, 'dm_empenho_desp')
    append_from_csv(file_paths_ft, 'ft_despesa')
    #descbribe_db(con)
    #describe_table(con,'ft_despesa')
    #group_by_field(con, 'ft_despesa', 'ano_particao', 'vr_liquidado')

