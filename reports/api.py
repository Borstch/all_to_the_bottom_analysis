from typing import List
from datetime import time

from database.api import DataBase, QueryResult


def get_visits_count_per_country(db: DataBase) -> List[QueryResult]:
    query = 'SELECT COUNT(*), visitor_country FROM CategoriesVisits GROUP BY CategoriesVisits.visitor_country;'
    db.execute_query(query)
    return db.get_query_results()


def get_category_by_country(db: DataBase, category_name: str) -> List[QueryResult]:
    query = 'SELECT COUNT(*), CategoriesVisits.visitor_country FROM CategoriesVisits INNER JOIN Categories ' \
            'ON (CategoriesVisits.category_id = Categories.category_id) WHERE Categories.category_name = ' \
            f'\'{category_name}\' GROUP BY CategoriesVisits.visitor_country;'
    db.execute_query(query)
    return db.get_query_results()


def get_category_visits_by_time_of_day(db: DataBase, category_name: str) -> List[QueryResult]:
    query = 'SELECT COUNT(*), TimeOfDaySplittedVisits.time_of_day FROM TimeOfDaySplittedVisits INNER JOIN Categories ' \
            'ON (TimeOfDaySplittedVisits.category_id = Categories.category_id) WHERE Categories.category_name = ' \
            f'\'{category_name}\' GROUP BY TimeOfDaySplittedVisits.time_of_day;'
    db.execute_query(query)
    return db.get_query_results()


def get_hourly_queries_counts(db: DataBase) -> List[int]:
    query_template = 'SELECT COUNT(*) FROM Queries WHERE time_in_interval(time \'{0}\', ' \
                     '(time \'{0}\'+ interval \'1 hours\'), queried_at_t);'

    result = []
    for hour in range(24):
        db.execute_query(query_template.format(time(hour=hour)))
        result.append(int(db.get_query_result()[0]))

    return result


def count_purchases_categories_joint_with_category(db: DataBase, category_name: str) -> List[QueryResult]:
    query = 'SELECT SUM(TransactionsGoods.goods_count) AS amount, Categories.category_name ' \
            'FROM TransactionsGoods INNER JOIN Goods ON TransactionsGoods.goods_id = Goods.goods_id ' \
            'INNER JOIN Categories ON Goods.category_id = Categories.category_id ' \
            'WHERE TransactionsGoods.transaction_id IN ' \
            '(SELECT TransactionsGoods.transaction_id ' \
            'FROM TransactionsGoods INNER JOIN Goods ON TransactionsGoods.goods_id = Goods.goods_id ' \
            'INNER JOIN Categories ON Goods.category_id = Categories.category_id ' \
            f'WHERE Categories.category_name = \'{category_name}\') ' \
            f'AND Categories.category_name != \'{category_name}\' GROUP BY Categories.category_name;'
    db.execute_query(query)
    return db.get_query_results()


def count_unused_carts(db: DataBase) -> int:
    query = 'SELECT COUNT(*) FROM UnusedCarts;'
    db.execute_query(query)
    return int(db.get_query_result()[0])


def count_users_with_more_than_n_purchases(db: DataBase, n: int) -> int:
    query = f'SELECT COUNT(*) FROM Users WHERE Users.visits_count > {n};'
    db.execute_query(query)
    return int(db.get_query_result()[0])


if __name__ == '__main__':
    database = DataBase('../database\\database.ini')
    try:
        print(max(get_visits_count_per_country(database), key=lambda x: x[0]))
        print(max(get_category_by_country(database, 'fresh_fish'), key=lambda x: x[0]))
        print(max(get_category_visits_by_time_of_day(database, 'frozen_fish'), key=lambda x: x[0]))
        hourly_visits_counts = get_hourly_queries_counts(database)
        print(hourly_visits_counts.index(max(hourly_visits_counts)))
        print(max(count_purchases_categories_joint_with_category(database, 'semi_manufactures'), key=lambda x: x[0]))
        print(count_unused_carts(database))
        print(count_users_with_more_than_n_purchases(database, 1))
    finally:
        database.disconnect()
