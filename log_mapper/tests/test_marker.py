from log_mapper.marker import mark_tokens
from log_mapper.QueryType import QueryType


class TestMarker:
    def test_empty_tokens(self):
        result = mark_tokens([])
        assert [] == result

    def test_none_mark_one(self):
        result = mark_tokens([{
            'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
            'query': 'https://all_to_the_bottom.com/'
        }])[0][0]
        assert QueryType.NONE == result

    def test_none_mark_two(self):
        result = mark_tokens([{
            'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
            'query': 'https://all_to_the_bottom.com/success_pay_8642/'
        }])[0][0]
        assert QueryType.NONE == result

    def test_query_with_params_one(self):
        result = mark_tokens([{
            'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
            'query': 'https://all_to_the_bottom.com/pay?user_id=81270149216&cart_id=8642'
        }])[0][0]
        assert QueryType.PAYMENT == result

    def test_query_with_params_two(self):
        result = mark_tokens([{
            'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
            'query': 'https://all_to_the_bottom.com/cart?goods_id=8&amount=1&cart_id=8642'
        }])[0][0]
        assert QueryType.ADDITION == result

    def test_query_with_params_three(self):
        result = mark_tokens([{
            'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
            'query': 'https://all_to_the_bottom.com/some_page?wrong_param=1'
        }])[0][0]
        assert QueryType.NONE == result

    def test_category(self):
        result = mark_tokens([
            {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/fresh_fish/'
            },
            {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/canned_food/pate_of_tuna/'
            },
            {
                'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                'query': 'https://all_to_the_bottom.com/caviar/black_caviar/'
            }
        ])
        result = [x[0] for x in result]
        assert [QueryType.CATEGORY, QueryType.CATEGORY, QueryType.CATEGORY] == result
