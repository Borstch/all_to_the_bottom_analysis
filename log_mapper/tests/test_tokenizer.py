from log_mapper.tokenizer import tokenize


class TestTokenizer:
    def test_empty_file(self):
        result = tokenize('../../data/empty_logs.txt')
        assert [] == result

    def test_incomplete_line(self):
        result = tokenize('../../data/incomplete_log_line.txt')
        assert [{'date': '2018-08-01', 'query': 'https://all_to_the_bottom.com/'}] == result

    def test_default_behavior(self):
        result = tokenize('../../data/first_5_log_lines.txt')
        assert [
                   {
                       'date': '2018-08-01', 'time': '00:01:35', 'ip': '121.165.118.201',
                       'query': 'https://all_to_the_bottom.com/'
                   },
                   {
                       'date': '2018-08-01', 'time': '00:01:47', 'ip': '121.165.118.201',
                       'query': 'https://all_to_the_bottom.com/fresh_fish/'
                   },
                   {
                       'date': '2018-08-01', 'time': '00:03:02', 'ip': '121.165.118.201',
                       'query': 'https://all_to_the_bottom.com/'
                   },
                   {
                       'date': '2018-08-01', 'time': '00:04:27', 'ip': '121.165.118.201',
                       'query': 'https://all_to_the_bottom.com/canned_food/'
                   },
                   {
                       'date': '2018-08-01', 'time': '00:05:55', 'ip': '121.165.118.201',
                       'query': 'https://all_to_the_bottom.com/'
                   }
        ] == result
