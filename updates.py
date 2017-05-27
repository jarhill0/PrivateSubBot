import json
import random

import config
import helpers


def change_title():
    with open(config.titles_path) as f:
        titles = json.load(f)

    if not config.testing:
        reddit = helpers.initialize_reddit()
        reddit.subreddit(config.target_subreddit).mod.update(title=random.choice(titles))
    else:
        print('Testing: updated title ("%s")' % random.choice(titles))


def update_sidebar(user_list):
    with open(config.sidebar_text_paths[0], 'r') as f:
        sidebar_1 = f.read()
    with open(config.sidebar_text_paths[1], 'r') as f:
        sidebar_2 = f.read()

    sidebar = sidebar_1
    sidebar += 'Number | User\n---|---\n'

    for i, user in enumerate(user_list):
        sidebar += '%s | /u/%s\n' % (i + 1, user)

    sidebar += sidebar_2

    if not config.testing:
        reddit = helpers.initialize_reddit()
        reddit.subreddit(config.target_subreddit).mod.update(description=sidebar)
    else:
        print('Testing: description updated:\n\n%s' % sidebar)


if __name__ == '__main__':
    choice = input('Update what? T for title or S for sidebar [T/S]: ')

    if choice.lower == 't':
        change_title()
    elif choice.lower == 's':
        update_sidebar(helpers.load_data('user_list'))
    else:
        print('Invalid choice. Exiting.')
