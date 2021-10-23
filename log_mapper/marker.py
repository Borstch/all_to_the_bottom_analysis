from typing import Tuple, List

from log_mapper.tokenizer import Token
from log_mapper.QueryType import QueryType


MarkedToken = Tuple[QueryType, Token]


def mark_line(token: Token) -> MarkedToken:
    query = token['query'].replace('https://', '')
    if len(query.split('?')) == 2:
        if 'pay' in query:
            return QueryType.PAYMENT, token
        if 'cart' in query:
            return QueryType.ADDITION, token
    elif len(query.split('/')) > 2 and 'success_pay' not in query:
        return QueryType.CATEGORY, token
    return QueryType.NONE, token


def mark_tokens(tokens: List[Token]) -> List[MarkedToken]:
    return [mark_line(token) for token in tokens]
