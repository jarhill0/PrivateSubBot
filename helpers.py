import json
import time

import praw

import config


def date_string():
    return time.strftime('%Y-%m-%d', time.localtime())


def initialize_reddit():
    return praw.Reddit(config.bot_username, user_agent='PrivateSubManager')


def load_data(name):
    with open('data/%s.json' % name, 'r') as f:
        output = json.load(f)
    return output


def write_data(name, data):
    with open('data/%s.json' % name, 'w') as f:
        json.dump(data, f)


def write_log_trash(name, data):
    with open('log_trash/%s.json' % name, 'w') as f:
        json.dump(data, f)
