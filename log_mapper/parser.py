import itertools as it
from typing import List, Dict, Callable
from datetime import datetime
from functools import lru_cache

import requests

import data_wrappers as dw
import logger
from data_wrappers import Serializable
from log_mapper.marker import MarkedToken
from log_mapper.tokenizer import Token
from log_mapper.QueryType import QueryType


TokenGroups = Dict[str, List[MarkedToken]]


def __extract_datetime(token: Token) -> datetime:
    return datetime.strptime(token['date'] + ' ' + token['time'], '%Y-%m-%d %H:%M:%S')


@lru_cache(maxsize=256)
def __extract_country(ip_address: str) -> str:
    logger.log_trace(f'Searching for user\'s country by ip {ip_address}...')
    try:
        response = requests.get('http://ipinfo.io/json')
        return response.json()['country']
    except Exception as error:
        logger.log_warning(str(error))

    return ''


def __get_category_name(query: str) -> str:
    assert len(query.replace('https://', '').split('/')) >= 2, f'Got unexpected query: {query}'
    return query.replace('https://', '').split('/')[1]


def __get_goods_name(query: str) -> str:
    assert len(query.replace('https://', '').split('/')) >= 3, f'Got unexpected query: {query}'
    return query.replace('https://', '').split('/')[2]


def group_by_ip(marked_tokens: List[MarkedToken]) -> TokenGroups:
    marked_tokens = sorted(marked_tokens, key=lambda x: x[1]['ip'])
    return {ip: list(tokens) for ip, tokens in it.groupby(marked_tokens, key=lambda x: x[1]['ip'])}


def parse(groups: TokenGroups, logging_callback: Callable[[str], None] = None) -> List[Serializable]:
    total_lines_count = sum(len(group) for group in groups.values())
    current_line: int = 1
    queries_count: int = 0
    categories_visits_count: int = 0
    categories_count: int = 0
    transactions_count: int = 0
    transaction_items_count: int = 0
    active_carts: Dict[int, dw.Cart] = {}
    active_users: Dict[int, dw.User] = {}
    active_goods: Dict[int, dw.Goods] = {}
    categories_names: List[str] = []
    result: List[Serializable] = []
    for ip in groups.keys():
        for token_num, (token_type, token) in enumerate(groups[ip]):
            logger.log_trace(f'Line {current_line}/{total_lines_count}')

            if token_type == QueryType.CATEGORY:
                category_name = __get_category_name(token['query'])
                if category_name not in categories_names:
                    category_id = categories_count

                    category = dw.Category(category_id, category_name)
                    categories_names.append(category_name)
                    result.append(category)
                    categories_count += 1
                else:
                    category_id = categories_names.index(category_name)

                visit = dw.CategoriesVisit(
                    categories_visits_count, category_id, __extract_datetime(token),
                    token['ip'], __extract_country(token['ip'])
                )
                result.append(visit)
                categories_visits_count += 1
            elif token_type == QueryType.ADDITION:
                params = token['query'].split('?')[1].split('&')  # [goods_id=n, amount=m,cart_id=r]
                goods_id = int(params[0].split('=')[1])
                amount = int(params[1].split('=')[1])
                cart_id = int(params[2].split('=')[1])
                if goods_id not in active_goods.keys():
                    previous_query = groups[ip][token_num - 1][1]['query']
                    category_id = categories_names.index(__get_category_name(previous_query))
                    goods = dw.Goods(goods_id, category_id, __get_goods_name(previous_query))

                    active_goods[goods_id] = goods
                    result.append(goods)

                if cart_id not in active_carts.keys():
                    cart = dw.Cart(cart_id, {})
                    cart.goods_amount[goods_id] = amount
                    active_carts[cart_id] = cart
                elif goods_id in active_carts[cart_id].goods_amount.keys():
                    active_carts[cart_id].goods_amount[goods_id] += amount
                else:
                    active_carts[cart_id].goods_amount[goods_id] = amount
            elif token_type == QueryType.PAYMENT:
                params = token['query'].split('?')[1].split('&')  # [user_id=n, cart_id=m]
                user_id = int(params[0].split('=')[1])
                cart_id = int(params[1].split('=')[1])
                if cart_id not in active_carts.keys():
                    logger.log_error(f'Payment on non-existent cart {cart_id} detected. Skipping to the next query...')
                    query = dw.Query(queries_count, token['ip'], token['query'], __extract_datetime(token))
                    result.append(query)
                    queries_count += 1
                    continue

                if user_id not in active_users.keys():
                    user = dw.User(user_id, 'Unknown', token['ip'], __extract_country(token['ip']), 1, 1)
                    active_users[user_id] = user
                    result.append(user)  # this value will be changing via pointer in "active_users"
                else:
                    active_users[user_id].visits_count += 1
                    active_users[user_id].carts_count += 1
                    active_users[user_id].last_ip = token['ip']

                transaction = dw.Transaction(transactions_count, user_id, __extract_datetime(token))
                transaction_items = []
                for goods_id, amount in active_carts[cart_id].goods_amount.items():
                    transaction_item = dw.TransactionGoods(
                        transaction_items_count, transactions_count, goods_id, amount
                    )
                    transaction_items_count += 1
                    transaction_items.append(transaction_item)
                transactions_count += 1
                result.append(transaction)
                '''all transaction items should be added after transaction to satisfy db integrity'''
                result.extend(transaction_items)

                active_users[user_id].payments_count += 1
                del active_carts[cart_id]  # this cart is used

            query = dw.Query(queries_count, token['ip'], token['query'], __extract_datetime(token))
            result.append(query)
            queries_count += 1

            current_line += 1

    result.extend(active_carts.values())
    if logging_callback is not None:
        logging_callback(
            f'Parsing completed, created {len(result)} wrappers.'
        )
    return result
