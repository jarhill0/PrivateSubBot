import json
import os
import random

import config
import helpers


def change_title():
    titles_path = os.path.join(helpers.folder_path(), config.titles_path[0], config.titles_path[1])
    with open(titles_path) as f:
        titles = json.load(f)

    if not config.testing:
        reddit = helpers.initialize_reddit()
        reddit.subreddit(config.target_subreddit).mod.update(title=random.choice(titles))
    else:
        print('Testing: updated title ("{}")'.format(random.choice(titles)))


def update_sidebar(user_list):
    path_1 = os.path.join(helpers.folder_path(), config.sidebar_text_paths[0][0], config.sidebar_text_paths[0][1])
    path_2 = os.path.join(helpers.folder_path(), config.sidebar_text_paths[1][0], config.sidebar_text_paths[1][1])
    with open(path_1, 'r') as f:
        sidebar_1 = f.read()
    with open(path_2, 'r') as f:
        sidebar_2 = f.read()

    sidebar = sidebar_1
    sidebar += 'Number | User\n---|---\n'

    for i, user in enumerate(user_list):
        sidebar += '{} | /u/{}\n'.format(i + 1, user)

    sidebar += sidebar_2

    if not config.testing:
        reddit = helpers.initialize_reddit()
        reddit.subreddit(config.target_subreddit).mod.update(description=sidebar)
    else:
        print('Testing: description updated:\n')
        print(sidebar)


if __name__ == '__main__':
    choice = input('Update what? T for title or S for sidebar [T/S]: ')

    if choice.lower() == 't':
        change_title()
    elif choice.lower() == 's':
        update_sidebar(helpers.load_data('user_list'))
    else:
        print('Invalid choice. Exiting.')
