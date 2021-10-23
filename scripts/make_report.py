import os
from argparse import ArgumentParser
from datetime import time
from typing import List

from database.api import DataBase, QueryResult
from reports.api import (
    get_visits_count_per_country, get_category_by_country, get_category_visits_by_time_of_day,
    get_hourly_queries_counts, count_purchases_categories_joint_with_category, count_unused_carts,
    count_users_with_more_than_n_purchases
)


def __get_max_value_from_query_results(query_results: List[QueryResult]) -> QueryResult:
    return max(query_results, key=lambda x: x[0])


def __translate_time_of_day(time_of_day_in_russian: str) -> str:
    if time_of_day_in_russian.lower() == 'утро':
        return 'morning'
    if time_of_day_in_russian.lower() == 'день':
        return 'day'
    if time_of_day_in_russian.lower() == 'вечер':
        return 'evening'
    if time_of_day_in_russian.lower() == 'ночь':
        return 'night'
    return '?'


def main():
    parser = ArgumentParser(description='')
    parser.add_argument(
        '--db_config', type=str, help='path to the file with database config',
        default=os.path.join('../', 'database', 'database.ini')
    )
    args = parser.parse_args()

    db = DataBase(args.db_config)
    try:
        country_with_most_visits: str = __get_max_value_from_query_results(get_visits_count_per_country(db))[1]
        country_most_interested_in_fresh_fish: str = __get_max_value_from_query_results(
            get_category_by_country(db, 'fresh_fish')
        )[1]
        time_of_day_with_most_visits_of_frozen_fish: str = __get_max_value_from_query_results(
            get_category_visits_by_time_of_day(db, 'frozen_fish')
        )[1]
        hourly_queries_count: List[int] = get_hourly_queries_counts(db)
        hour_with_most_queries: int = hourly_queries_count.index(max(hourly_queries_count))
        visits_of_category_joint_with_semi_manufactures: str = __get_max_value_from_query_results(
            count_purchases_categories_joint_with_category(db, 'semi_manufactures')
        )[1]
        unused_carts_count: int = count_unused_carts(db)
        users_with_repeated_purchases_count: int = count_users_with_more_than_n_purchases(db, 1)
    finally:
        db.disconnect()

    print('\nREPORT')
    print(f'Users from {country_with_most_visits} visits site more frequently than others')
    print(
        f'Users from {country_most_interested_in_fresh_fish}',
        'visits category \'fresh_fish\' more frequently than others'
    )
    print(
        'Category \'frozen_fish,\' is visited more at',
        f'{__translate_time_of_day(time_of_day_with_most_visits_of_frozen_fish)}'
    )
    print(
        f'The most visitable period is {str(time(hour=hour_with_most_queries))} '
        f'- {str(time(hour=hour_with_most_queries + 1))}'
    )
    print(
        f'Goods from \'{visits_of_category_joint_with_semi_manufactures}\' '
        f'is purchased more frequently with \'semi_manufactures\''
    )
    print(f'There is {unused_carts_count} unused carts')
    print(f'{users_with_repeated_purchases_count} users has bought something more than once')


if __name__ == '__main__':
    main()
