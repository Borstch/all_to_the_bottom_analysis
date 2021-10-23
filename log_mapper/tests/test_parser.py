from datetime import datetime

import data_wrappers as dw
from log_mapper.QueryType import QueryType
from log_mapper.parser import group_by_ip, parse


class TestGrouping:
    def test_empty(self):
        result = group_by_ip([])
        assert {} == result

    def test_single_group(self):
        result = group_by_ip([
            (QueryType.CATEGORY, {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/caviar/black_caviar/'
            }),
            (QueryType.ADDITION, {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
            }),
            (QueryType.PAYMENT, {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
            })
        ])

        assert ['121.165.118.201'] == list(result.keys())

    def test_multiple_groups(self):
        result = group_by_ip([
            (QueryType.CATEGORY, {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '255.255.255.255',
                'query': 'https://all_to_the_bottom.com/caviar/black_caviar/'
            }),
            (QueryType.ADDITION, {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
            }),
            (QueryType.PAYMENT, {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '1.1.1.201',
                'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
            })
        ])

        assert sorted(['255.255.255.255', '121.165.118.201', '1.1.1.201']) == sorted(list(result.keys()))


class TestParser:
    def test_empty(self):
        result = parse({})
        assert [] == result

    def test_query(self):
        result = parse({
            '121.165.118.201': [
                (QueryType.NONE, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com'
                })
            ],
            '255.255.255.255': [
                (QueryType.NONE, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '255.255.255.255',
                    'query': 'https://all_to_the_bottom.com'
                })
            ]
        })
        assert [
            dw.Query(
                0, '121.165.118.201', 'https://all_to_the_bottom.com',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Query(
                1, '255.255.255.255', 'https://all_to_the_bottom.com',
                self.__extract_datetime('2018-08-01 00:05:55')
            )
        ] == result

    def test_category_one(self):
        result = parse({
            '255.255.255.255': [
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '255.255.255.255',
                    'query': 'https://all_to_the_bottom.com/caviar/black_caviar/'
                })
            ]
        })
        assert [
            dw.Category(0, 'caviar'),
            dw.CategoriesVisit(0, 0, self.__extract_datetime('2018-08-01 00:05:55'), '255.255.255.255', ''),
            dw.Query(
                0, '255.255.255.255', 'https://all_to_the_bottom.com/caviar/black_caviar/',
                self.__extract_datetime('2018-08-01 00:05:55')
            )
        ] == result

    def test_category_two(self):
        result = parse({
            '255.255.255.255': [
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '255.255.255.255',
                    'query': 'https://all_to_the_bottom.com/caviar/black_caviar/'
                }),
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '255.255.255.255',
                    'query': 'https://all_to_the_bottom.com/caviar/black_caviar/'
                })
            ]
        })

        assert [
            dw.Category(0, 'caviar'),
            dw.CategoriesVisit(0, 0, self.__extract_datetime('2018-08-01 00:05:55'), '255.255.255.255', ''),
            dw.Query(
                0, '255.255.255.255', 'https://all_to_the_bottom.com/caviar/black_caviar/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.CategoriesVisit(1, 0, self.__extract_datetime('2018-08-01 00:05:55'), '255.255.255.255', ''),
            dw.Query(
                1, '255.255.255.255', 'https://all_to_the_bottom.com/caviar/black_caviar/',
                self.__extract_datetime('2018-08-01 00:05:55')
            )
        ] == result

    def test_addition_one(self):
        result = parse({
            '121.165.118.201': [
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/frozen_fish/shark/'
                }),
                (QueryType.ADDITION, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
                })
            ]
        })

        assert [
            dw.Category(0, 'frozen_fish'),
            dw.CategoriesVisit(0, 0, self.__extract_datetime('2018-08-01 00:05:55'), '121.165.118.201', ''),
            dw.Query(
                0, '121.165.118.201', 'https://all_to_the_bottom.com/frozen_fish/shark/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Goods(8, 0, 'shark'),
            dw.Query(
                1, '121.165.118.201', 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Cart(8642, {8: 1})
        ] == result

    def test_addition_two(self):
        result = parse({
            '121.165.118.201': [
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/frozen_fish/shark/'
                }),
                (QueryType.ADDITION, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
                }),
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/frozen_fish/shark/'
                }),
                (QueryType.ADDITION, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=3&cart_id=8642'
                })
            ]
        })

        assert [
            dw.Category(0, 'frozen_fish'),
            dw.CategoriesVisit(0, 0, self.__extract_datetime('2018-08-01 00:05:55'), '121.165.118.201', ''),
            dw.Query(
                0, '121.165.118.201', 'https://all_to_the_bottom.com/frozen_fish/shark/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Goods(8, 0, 'shark'),
            dw.Query(
                1, '121.165.118.201', 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.CategoriesVisit(1, 0, self.__extract_datetime('2018-08-01 00:05:55'), '121.165.118.201', ''),
            dw.Query(
                2, '121.165.118.201', 'https://all_to_the_bottom.com/frozen_fish/shark/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Query(
                3, '121.165.118.201', 'https://all_to_the_bottom.com/cart?goods_id=8&amount=3&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Cart(8642, {8: 4})
        ] == result

    def test_wrong_payment(self):
        result = parse({
            '121.165.118.201': [
                (QueryType.PAYMENT, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
                })
            ]
        })
        assert [dw.Query(
            0, '121.165.118.201', 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642',
            self.__extract_datetime('2018-08-01 00:05:55')
        )] == result

    def test_payment_one(self):
        result = parse({
            '121.165.118.201': [
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/frozen_fish/shark/'
                }),
                (QueryType.ADDITION, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
                }),
                (QueryType.PAYMENT, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
                })
            ]
        })

        assert [
            dw.Category(0, 'frozen_fish'),
            dw.CategoriesVisit(0, 0, self.__extract_datetime('2018-08-01 00:05:55'), '121.165.118.201', ''),
            dw.Query(
                0, '121.165.118.201', 'https://all_to_the_bottom.com/frozen_fish/shark/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Goods(8, 0, 'shark'),
            dw.Query(
                1, '121.165.118.201', 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.User(81270149216, 'Unknown', '121.165.118.201', '', 1, 1, 1),
            dw.Transaction(0, 81270149216, self.__extract_datetime('2018-08-01 00:05:55')),
            dw.TransactionGoods(0, 0, 8, 1),
            dw.Query(
                2, '121.165.118.201', 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            )
        ] == result

    def test_payment_two(self):
        result = parse({
            '121.165.118.201': [
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/frozen_fish/shark/'
                }),
                (QueryType.ADDITION, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
                }),
                (QueryType.PAYMENT, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
                }),
                (QueryType.CATEGORY, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/frozen_fish/shark/'
                }),
                (QueryType.ADDITION, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
                }),
                (QueryType.PAYMENT, {
                    'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                    'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
                })
            ]
        })

        assert [
            dw.Category(0, 'frozen_fish'),
            dw.CategoriesVisit(0, 0, self.__extract_datetime('2018-08-01 00:05:55'), '121.165.118.201', ''),
            dw.Query(
                0, '121.165.118.201', 'https://all_to_the_bottom.com/frozen_fish/shark/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Goods(8, 0, 'shark'),
            dw.Query(
                1, '121.165.118.201', 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.User(81270149216, 'Unknown', '121.165.118.201', '', 2, 2, 2),
            dw.Transaction(0, 81270149216, self.__extract_datetime('2018-08-01 00:05:55')),
            dw.TransactionGoods(0, 0, 8, 1),
            dw.Query(
                2, '121.165.118.201', 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.CategoriesVisit(1, 0, self.__extract_datetime('2018-08-01 00:05:55'), '121.165.118.201', ''),
            dw.Query(
                3, '121.165.118.201', 'https://all_to_the_bottom.com/frozen_fish/shark/',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Query(
                4, '121.165.118.201', 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            ),
            dw.Transaction(1, 81270149216, self.__extract_datetime('2018-08-01 00:05:55')),
            dw.TransactionGoods(1, 1, 8, 1),
            dw.Query(
                5, '121.165.118.201', 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642',
                self.__extract_datetime('2018-08-01 00:05:55')
            )
        ] == result

    @staticmethod
    def __extract_datetime(date_time_string: str) -> datetime:
        return datetime.strptime(date_time_string, '%Y-%m-%d %H:%M:%S')
