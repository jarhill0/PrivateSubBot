import json
import os
import sys

import config
import helpers
import main as daddy

userlist_path = os.path.join(helpers.folder_path(), 'data', 'user_list.json')


def main(user):
    reddit = helpers.initialize_reddit()

    insert_user_to_userlist(user)

    daddy.add_users([user], reddit)

    with open(userlist_path, 'r') as f:
        users = json.load(f)

    daddy.flair_users([user], reddit, config.flair_normal, number_adjustment=len(users))


def insert_user_to_userlist(user):
    with open(userlist_path, 'r') as f:
        users = json.load(f)
    users.append(user)
    with open(userlist_path, 'w') as f:
        json.dump(users, f)


def process_input():
    if len(sys.argv) == 2:
        user = sys.argv[1]
    else:
        user = input('Enter user to re-add: ')

    main(user)


if __name__ == '__main__':
    process_input()
