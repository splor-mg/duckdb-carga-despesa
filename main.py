import duckdb
import logging
import argparse
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

def descbribe_db(con=None):
    print(con.sql("DESCRIBE"))


def describe_table(con, table_name):
    print(con.table(table_name).describe())


def group_by_field(con, table_name, field_agg, field_values):

    rel = con.sql(f"""SELECT * FROM {table_name}""")
    agg = rel.aggregate(f"{field_agg} AS 'agregado', sum({field_values}), count({field_agg})")
    print(agg)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_name', default='database/dadosmg.duckdb')
    parser.add_argument('--data_dir', default='datasets/despesa/data')
    parser.add_argument('--drop_tables', action=argparse.BooleanOptionalAction, help='Dropa todas as tabelas atuais da database', default=True)

    args = parser.parse_args()
    
    file_paths = Path(args.data_dir).glob('*.csv.gz')
    con = duckdb.connect(args.db_name) #Cria se não existe e se conecta à base de dados

    if args.drop_tables:
        drop_tables(args.db_name, con)

    tables_from_csv(con, file_paths)

if __name__ == '__main__':
    
    LOG_FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
