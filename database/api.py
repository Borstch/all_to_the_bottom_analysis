from typing import Tuple, List
from functools import lru_cache

import psycopg2

import data_wrappers
import logger
from database.config import config
from data_wrappers import Serializable


QueryResult = Tuple[str, ...]


class DataBase:
    def __init__(self, config_filename: str):
        self.conn = None
        self.cursor = None
        try:
            params = config(config_filename)
            logger.log_info('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)

            self.tables = self.__get_tables_list(config_filename)

            self.cursor = self.conn.cursor()
            self.cursor.execute('SELECT version()')
            db_version = self.cursor.fetchone()
            logger.log_info(f'PostgreSQL database version: {db_version}')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.log_fatal(error)

    def disconnect(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            logger.log_info('Database connection closed.')

    def execute_query(self, query: str) -> None:
        logger.log_trace(f'Executing query: {query}')
        self.cursor.execute(query)

    def get_query_result(self) -> QueryResult:
        return self.cursor.fetchone()

    def get_query_results(self) -> List[QueryResult]:
        return self.cursor.fetchall()

    def get_table_contents(self, table_name: str) -> List[QueryResult]:
        assert table_name in self.tables, f'Got non-existent table {table_name}'

        self.execute_query(f'SELECT * FROM {table_name};')
        return self.cursor.fetchall()

    def insert_single_item(self, item: Serializable) -> None:
        serialized_item = item.serialize()
        template_query = f'INSERT INTO table_name ({", ".join(serialized_item.keys())})' \
                         f' VALUES ({", ".join(str(value) for value in serialized_item.values())});'
        if isinstance(item, data_wrappers.Category):
            query = template_query.replace('table_name', 'Categories')
        elif isinstance(item, data_wrappers.Goods):
            query = template_query.replace('table_name', 'Goods')
        elif isinstance(item, data_wrappers.User):
            query = template_query.replace('table_name', 'Users')
        elif isinstance(item, data_wrappers.Transaction):
            query = template_query.replace('table_name', 'Transactions')
        elif isinstance(item, data_wrappers.TransactionGoods):
            query = template_query.replace('table_name', 'TransactionsGoods')
        elif isinstance(item, data_wrappers.CategoriesVisit):
            query = template_query.replace('table_name', 'CategoriesVisits')
        elif isinstance(item, data_wrappers.Query):
            query = template_query.replace('table_name', 'Queries')
        elif isinstance(item, data_wrappers.Cart):
            query = template_query.replace('table_name', 'UnusedCarts')
        else:
            raise Exception(f'Unsupported wrapper type {type(item)}')

        self.execute_query(query)

    def insert_items(self, items: List[Serializable]) -> None:
        for item in items:
            self.insert_single_item(item)

    def clear(self) -> None:
        for table in self.tables:
            self.execute_query(f'DELETE FROM {table};')

    @staticmethod
    @lru_cache()
    def __get_tables_list(config_filename: str) -> List[str]:
        try:
            return config(config_filename, 'tables')['tables'].split(',')
        except Exception as error:
            logger.log_fatal(str(error))
            raise


if __name__ == '__main__':
    db = DataBase('database.ini')
    db.disconnect()
