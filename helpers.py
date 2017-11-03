import json
import os
import sys
import time
import traceback

import config
import praw
import prawcore


def date_string():
    return time.strftime('%Y-%m-%d', time.localtime())


def initialize_reddit():
    reddit = praw.Reddit(config.bot_username, user_agent=config.user_agent)
    try:
        reddit.user.me()
    except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
        err = traceback.format_exc() + '\n'
        write_log_trash('Could not initialize Reddit {}'.format(date_string()), err)
        sys.exit(1)
    return reddit


def load_data(name):
    filepath = os.path.join(folder_path(), 'data', '{}.json'.format(name))
    with open(filepath, 'r') as f:
        output = json.load(f)
    return output


def write_data(name, data):
    filepath = os.path.join(folder_path(), 'data', '{}.json'.format(name))
    with open(filepath, 'w') as f:  # will not stack
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f)


def write_log_trash(name, data):
    filepath = os.path.join(folder_path(), 'log_trash', '{}.json'.format(name))
    with open(filepath, 'a') as f:  # will stack if there is more than one message per name
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f)


def folder_path():
    return os.path.dirname(os.path.abspath(__file__))
