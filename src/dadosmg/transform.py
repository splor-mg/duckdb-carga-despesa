import argparse
import logging
from .utils import DB

logger = logging.getLogger(__name__)

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
        logger.info(f'Criando view {table_prefix}...')
        con.execute(_sql)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('db_name')
    parser.add_argument('prefix')
    
    args = parser.parse_args()
    
    create_view_from_partitions(args.db_name, args.prefix)

if __name__ == '__main__':
    main()
