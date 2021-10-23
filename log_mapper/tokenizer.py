import os
import re
from typing import List, Dict

import logger


Token = Dict[str, str]


def init_patterns() -> Dict[str, re.Pattern]:
    return {
        'date': re.compile(r'\d{4}-\d{2}-\d{2}'),
        'time': re.compile(r'\d{2}:\d{2}:\d{2}'),
        'ip': re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
        'query':
            re.compile(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
    }


def tokenize(filename: str) -> List[Token]:
    def tokenize_line(line_num: int, text: str) -> Token:
        tokenized_line = {}
        for pattern_name, pattern in patterns.items():
            try:
                tokenized_line[pattern_name] = pattern.search(text).group(0)
            except AttributeError:
                logger.log_warning(f'Unable to parse pattern {pattern_name} on line {line_num}\nLine contents: {text}')

        return tokenized_line

    patterns: Dict[str, re.Pattern] = init_patterns()
    with open(filename) as f:
        return [tokenize_line(line_num, line) for line_num, line in enumerate(f.readlines())]


if __name__ == '__main__':
    print(*tokenize(os.path.join('../data', 'logs.txt')), sep='\n')
