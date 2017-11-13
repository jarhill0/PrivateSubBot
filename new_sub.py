import config
import helpers
import main
import updates


def new_sub():
    reddit = helpers.initialize_reddit()
    main.check_permissions(reddit)
    user_list = helpers.load_data('user_list')
    main.flair_users(user_list, reddit, config.flair_normal)
    if config.change_title:
        updates.change_title()
    if config.update_sidebar:
        updates.update_sidebar(user_list)
    main.add_users(user_list, reddit)
    helpers.write_data('participated', [])


if __name__ == '__main__':
    new_sub()
