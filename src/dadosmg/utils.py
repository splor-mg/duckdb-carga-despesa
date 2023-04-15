import duckdb
import logging

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
