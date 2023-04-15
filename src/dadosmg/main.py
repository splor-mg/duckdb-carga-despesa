import duckdb
import logging
import argparse
from pathlib import Path

class DB:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = duckdb.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

def drop_tables(db_name):
    with DB(db_name) as con:
        tables_list = con.execute('SHOW TABLES').fetchall()
        if tables_list:
            for table_name in tables_list:
                con.execute(f'DROP TABLE {table_name[0]}')
                logging.info(f'Tabela {table_name} apagada.')
        else:
            logging.info(f'Não há tabelas na database {db_name}')


def create_table_from_csv_files(db_name, file_paths):
    with DB(db_name) as con:
        for file in file_paths:
            table_name = file.stem.rstrip('.csv')
            _sql = f"""
                    CREATE TABLE '{table_name}' AS 
                    SELECT * FROM read_csv_auto('{file}')
                    """
            con.execute(_sql)
            logging.info(f'Arquivo {file.name} carregado para tabela {table_name}')

def sql_union_all(tables):
    result =' union all '.join([f'select * from {table[0]}' for table in tables])
    return result

def create_view_from_partitions(db_name, table_prefix):
    with DB(db_name) as con:
        _sql = f"""
               SELECT table_name
               FROM duckdb_tables()
               WHERE schema_name = 'main' AND table_name LIKE '{table_prefix}%'"""
        tables = con.execute(_sql).fetchall()
        _sql = sql_union_all(tables)
        _sql = f'CREATE VIEW {table_prefix} AS {_sql}'
        logging.info(f'Criando view {table_prefix}...')
        con.execute(_sql)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_name', default='database/dadosmg.duckdb')
    parser.add_argument('--data_dir', default='datasets/despesa/data')
    parser.add_argument('--drop_tables', action=argparse.BooleanOptionalAction, help='Dropa todas as tabelas atuais da database', default=True)

    args = parser.parse_args()

    if args.drop_tables:
        drop_tables(args.db_name)

    create_table_from_csv_files(args.db_name, Path(args.data_dir).glob('*.csv.gz'))
    create_view_from_partitions(args.db_name, 'ft_despesa')
    create_view_from_partitions(args.db_name, 'dm_empenho_desp')

if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
