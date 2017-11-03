import sys

import config
import helpers
import main


def re_flair(count):
    users = helpers.load_data('user_list')
    reddit = helpers.initialize_reddit()
    main.flair_users(users[:count], reddit, config.flair_normal)


def process_input():
    if len(sys.argv) == 2:
        count = int(sys.argv[1])
    else:
        count = int(input(
            'All users will be flaired as if they are not new. How many users should be re-flaired? '))
    re_flair(count)


if __name__ == '__main__':
    process_input()
