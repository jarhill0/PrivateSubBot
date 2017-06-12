import sys

import config
import helpers
import main as daddy


def main(user):
    reddit = helpers.initialize_reddit()

    insert_user_to_userlist(user)

    daddy.add_users([user], reddit)

    users = helpers.load_data('user_list')

    daddy.flair_users([user], reddit, config.flair_normal, number_adjustment=len(users))


def insert_user_to_userlist(user):
    users = helpers.load_data('user_list')
    users.append(user)
    helpers.write_data('user_list', users)


def process_input():
    if len(sys.argv) == 2:
        user = sys.argv[1]
    else:
        user = input('Enter user to re-add: ')

    main(user)


if __name__ == '__main__':
    process_input()
