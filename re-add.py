import sys

import config
import helpers
import main as daddy


def main(user):
    reddit = helpers.initialize_reddit()

    users = helpers.load_data('user_list')

    daddy.add_users([user], reddit)
    daddy.flair_users([user], reddit, config.flair_normal, number_adjustment=len(users))

    insert_user_to_userlist(user)
    users = helpers.load_data('user_list')

    title, body = build_post(user, len(users))
    daddy.make_post(title, body, reddit, distinguish=True, sticky=False)


def build_post(user, number):
    title = 'User re-add'
    if config.title_date:
        title = helpers.date_string() + ' - ' + title
    if config.title_number:
        stats = helpers.load_data('stats')
        stats['re-add count'] += 1
        readd_count = ['re-add count']
        helpers.write_data('stats', stats)
        title += ' #%d' % readd_count
    body = '- #%d /u/%s' % (number, user)

    return title, body


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
