import json
import os
import time

import praw

import config


def date_string():
    return time.strftime('%Y-%m-%d', time.localtime())


def initialize_reddit():
    return praw.Reddit(config.bot_username, user_agent='PrivateSubManager')


def load_data(name):
    filepath = os.path.join(folder_path(), 'data', '%s.json' % name)
    with open(filepath, 'r') as f:
        output = json.load(f)
    return output


def write_data(name, data):
    filepath = os.path.join(folder_path(), 'data', '%s.json' % name)
    with open(filepath, 'w') as f:
        json.dump(data, f)


def write_log_trash(name, data):
    filepath = os.path.join(folder_path(), 'log_trash', '%s.json' % name)
    with open(filepath, 'w') as f:
        json.dump(data, f)


def folder_path():
    return os.path.dirname(os.path.abspath(__file__))
