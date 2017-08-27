import sys

import config
import helpers
import main as daddy
import updates


def main(new_users):
    reddit = helpers.initialize_reddit()

    user_list = helpers.load_data('user_list')

    daddy.add_users(new_users, reddit)
    daddy.flair_users(new_users, reddit, config.flair_normal, number_adjustment=len(user_list))

    insert_users_to_userlist(new_users)
    user_list = helpers.load_data('user_list')

    title, body = build_post(new_users, len(user_list) - len(new_users) + 1)
    daddy.make_post(title, body, reddit, distinguish=True, sticky=False)

    if config.update_sidebar:
        updates.update_sidebar(user_list)


def build_post(new_users, number):
    title = 'User re-add'
    if config.title_date:
        title = helpers.date_string() + ' - ' + title
    if config.title_number:
        stats = helpers.load_data('stats')
        stats['re-add count'] += 1
        readd_count = stats['re-add count']
        helpers.write_data('stats', stats)
        title += ' #%d' % readd_count

    lines = []
    for user in new_users:
        lines.append('- #%d /u/%s' % (number, user))
        number += 1

    body = '  /n'.join(lines)

    return title, body


def insert_users_to_userlist(new_users):
    user_list = helpers.load_data('user_list')
    user_list.extend(new_users)
    helpers.write_data('user_list', user_list)


def process_input():
    if len(sys.argv) >= 2:
        users = sys.argv[1:]
    else:
        users = input('Enter users to re-add, separated by spaces: ').split()

    main(users)


if __name__ == '__main__':
    process_input()
