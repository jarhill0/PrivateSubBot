import json
import os
import random

import prawcore

import config
import helpers


def change_title():
    titles_path = os.path.join(
        helpers.folder_path(), config.titles_path[0], config.titles_path[1]
    )
    with open(titles_path) as f:
        titles = json.load(f)

    if not config.testing:
        reddit = helpers.initialize_reddit()
        reddit.subreddit(config.target_subreddit).mod.update(
            title=random.choice(titles)
        )
    else:
        print('Testing: updated title ("{}")'.format(random.choice(titles)))


def update_sidebar(user_list):
    path_1 = os.path.join(
        helpers.folder_path(),
        config.sidebar_text_paths[0][0],
        config.sidebar_text_paths[0][1],
    )
    path_2 = os.path.join(
        helpers.folder_path(),
        config.sidebar_text_paths[1][0],
        config.sidebar_text_paths[1][1],
    )
    with open(path_1, "r") as f:
        sidebar_1 = f.read()
    with open(path_2, "r") as f:
        sidebar_2 = f.read()

    sidebar = sidebar_1 + "\n\n" + _user_table(user_list) + "\n\n" + sidebar_2

    if not config.testing:
        reddit = helpers.initialize_reddit()
        reddit.subreddit(config.target_subreddit).wiki["config/sidebar"].edit(
            content=sidebar
        )
        widget = _get_widget(sidebar_1)
        widget.mod.update(text=sidebar)
    else:
        print("Testing: description updated:\n")
        print(sidebar)


def _user_table(user_list):
    rows = ["Number | User\n---|---"]
    for i, user in enumerate(user_list):
        rows.append("{} | /u/{}".format(i + 1, user))
    return "\n".join(rows)


def update_top_sticky(user_list):
    reddit = helpers.initialize_reddit()
    subreddit = reddit.subreddit(config.target_subreddit)
    try:
        top_sticky = subreddit.sticky()
    except prawcore.NotFound:
        print("No sticky exists.")
        return

    if top_sticky.author != reddit.user.me():
        print("I did not create the sticky.")
        return

    if top_sticky.title != config.top_sticky_title:
        print(
            f"Titles do not match; got {top_sticky.title!r} and expected {config.top_sticky_title!r}."
        )
        return

    new_contents = _user_table(user_list)

    if config.testing:
        print(f"Testing: updating {top_sticky} to the following.")
        print(new_contents)
    else:
        top_sticky.edit(new_contents)


def _get_widget(sidebar_contents):
    reddit = helpers.initialize_reddit()
    for widget in reddit.subreddit(config.target_subreddit).widgets.sidebar:
        if widget.kind == "textarea" and sidebar_contents in widget.text:
            return widget

    raise ValueError("No widget with specified contents found.")


if __name__ == "__main__":
    choice = input("Update what? T for title, S for sidebar, or P for sticky [T/S/P]: ")

    if choice.lower() == "t":
        change_title()
    elif choice.lower() == "s":
        update_sidebar(helpers.load_data("user_list"))
    elif choice.lower() == "p":
        update_top_sticky(helpers.load_data("user_list"))
    else:
        print("Invalid choice. Exiting.")
