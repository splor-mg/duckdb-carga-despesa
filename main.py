import duckdb
import logging
import argparse
from pathlib import Path

class database:
    def __init__(self, database_name):
        self.database_name = database_name

    def __enter__(self):
        self.conn = duckdb.connect(self.database_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

def drop_tables(db_name, con=None):
    with database(db_name) as con:
        tables_list = con.execute("""SHOW TABLES""").fetchall()
        if tables_list:
            for table_name in tables_list:
                con.execute(f"""DROP TABLE {table_name[0]} """)
                logging.info(f"Tabela {table_name} apagada.")
        else:
            logging.info(f"Não há tabelas na database {db_name}")


def tables_from_csv(db_name, file_paths):
    with database(db_name) as con:
        for file in file_paths:
            name = file.stem.rstrip('.csv')
            con.execute(f"""CREATE TABLE '{name}' AS SELECT * FROM read_csv_auto('{file}')""")
            logging.info(f"Arquivo {file.name} carregado para tabela {name}")

def create_view_from_partition(db_name, table_prefix):
    with database(db_name) as con:
        _sql = f"""
               SELECT table_name
               FROM duckdb_tables()
               WHERE schema_name = 'main' AND table_name LIKE '{table_prefix}%'"""
        tables = con.execute(_sql).fetchall()
        _sql = ' union all '.join([f'select * from {table[0]}\n' for table in tables])
        _sql = f"""CREATE VIEW {table_prefix} AS {_sql}
                """
        logging.info(f'Criando view {table_prefix}...')
        con.execute(_sql)

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
    
    tables_from_csv(args.db_name, file_paths)

    create_view_from_partition(args.db_name, 'ft_despesa')
    create_view_from_partition(args.db_name, 'dm_empenho_desp')

if __name__ == '__main__':
    
    LOG_FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
