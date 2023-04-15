import argparse
import logging
from pathlib import Path
from .utils import DB, drop_tables

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_name', default='database/dadosmg.duckdb')
    parser.add_argument('--data_dir', default='datasets/despesa/data')
    parser.add_argument('--drop_tables', action=argparse.BooleanOptionalAction, help='Dropa todas as tabelas atuais da database', default=True)

    args = parser.parse_args()

    if args.drop_tables:
        drop_tables(args.db_name)

    create_table_from_csv_files(args.db_name, Path(args.data_dir).glob('*.csv.gz'))

if __name__ == '__main__':
    main()