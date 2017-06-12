import sys

import praw

import config
import helpers
import main


def replace(old_un, new_un):
    users = helpers.load_data('user_list')
    users[users.index(old_un)] = new_un
    helpers.write_data('user_list', users)

    reddit = helpers.initialize_reddit()
    if not config.testing:
        try:
            reddit.subreddit(config.target_subreddit).flair.set(
                redditor=old_un,
                text='Moved to /u/%s' % new_un, )
            reddit.subreddit(config.target_subreddit).contributor.remove(old_un)
        except praw.exceptions.APIException:
            # Deleted user, most likely
            pass
        main.flair_users([new_un], reddit, config.flair_normal, number_adjustment=users.index(new_un))
        main.add_users([new_un], reddit)
    else:
        print('Flaired and removed /u/%s; Flaired and added /u/%s') % (old_un, new_un)


def process_input():
    if len(sys.argv) == 3:
        old_un, new_un = sys.argv[1], sys.argv[2]
    else:
        old_un = input('Enter the exact username of the user to be removed: ')
        new_un = input('Enter the exact username of the user to replace them: ')

    replace(old_un, new_un)


if __name__ == '__main__':
    process_input()
