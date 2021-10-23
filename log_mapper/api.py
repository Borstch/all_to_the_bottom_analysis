from typing import List, Callable

import logger
from data_wrappers import Serializable
from log_mapper.tokenizer import tokenize
from log_mapper.marker import mark_tokens
from log_mapper.parser import parse, group_by_ip


def wrap_logs(logs_filename: str, logging_callback: Callable[[str], None] = None) -> List[Serializable]:
    try:
        if logging_callback is not None:
            logging_callback(f'Beginning to parse logs in file {logs_filename}')
            logging_callback('Preparing logs. Stage 1 - Tokenizing')
        tokens = tokenize(logs_filename)

        if logging_callback is not None:
            logging_callback('Preparing logs. Stage 2 - Marking')
        marked_tokens = mark_tokens(tokens)

        if logging_callback is not None:
            logging_callback('Preparing logs. Stage 3 - Grouping tokens by IP')
        grouped_tokens = group_by_ip(marked_tokens)

        if logging_callback is not None:
            logging_callback('Preparation completed. Parsing...')
        wrapped_logs = parse(grouped_tokens, logging_callback)

        return wrapped_logs
    except Exception as error:
        logger.log_fatal(str(error))
        raise
