import os
from argparse import ArgumentParser

import logger
from database.api import DataBase
from log_mapper.api import wrap_logs


def main():
    parser = ArgumentParser(description='Maps logs into database')
    parser.add_argument(
        '--file_path', type=str, help='path to the file with logs',
        default=os.path.join('../data', 'logs.txt')
    )
    parser.add_argument(
        '--db_config', type=str, help='path to the file with database config',
        default=os.path.join('../', 'database', 'database.ini')
    )
    args = parser.parse_args()

    wrapped_logs = wrap_logs(args.file_path, logger.log_info)
    logger.log_info('Writing data to the data base...')
    db = DataBase(args.db_config)
    try:
        db.clear()
        db.insert_items(wrapped_logs)
    finally:
        db.disconnect()

    logger.log_info('Log mapping completed')


if __name__ == '__main__':
    main()
