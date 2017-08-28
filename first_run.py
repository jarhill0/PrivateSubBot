import sys
import time

import helpers
import main as daddy
import updates

try:
    import config
except (ImportError, ModuleNotFoundError):
    print('config.py not found. Rename config.example.py to config.py after configuration.')
    sys.exit(1)


class ActiveCommunity(Exception):
    pass


def main():
    user_list = helpers.load_data('user_list')
    reddit = helpers.initialize_reddit()
    stats = helpers.load_data('stats')

    if user_list and ('--ignore-active-community' not in sys.argv):  # checks if the user-list is non-empty
        msg = 'Userlist is non-empty. Exiting. Call with --ignore-active-community to run anyway'
        helpers.write_log_trash('Failed {}'.format(helpers.date_string()), msg)
        raise ActiveCommunity(msg)

    new_users, new_user_urls = daddy.get_new_users(reddit, 50, [])
    helpers.write_log_trash('New users {}'.format(helpers.date_string()), new_users)

    post_text = daddy.build_new_text(new_users, 1)

    if config.entry_comments:
        post_text += '\n\n[Comments for entry]({})'.format(daddy.build_and_post_gist(new_users, new_user_urls))
    if config.stats_section:
        post_text += '\n\n# Info:\n\n'
        post_text += '- {} users added\n'.format(len(new_users))
        diff = len(new_users)
        change = '+{}'.format(diff) if diff >= 0 else str(diff)
        post_text += '- Membercap: {} ({})'.format(len(new_users), change)

    title = config.main_log_title
    if config.title_date:
        title = helpers.date_string() + ' - ' + title
    if config.title_number:
        stats['log_count'] += 1
        title += ' #{}'.format(stats['log_count'])

    daddy.make_post(title, post_text, reddit)

    if config.change_title:
        updates.change_title()

    daddy.add_users(new_users, reddit)
    daddy.flair_users(new_users, reddit, 'numbernew')

    if config.update_sidebar:
        updates.update_sidebar(new_users)

    stats['last_full_run'] = time.time()
    helpers.write_data('stats', stats)
    helpers.write_data('user_list', new_users)
    helpers.write_data('participated', [])


if __name__ == '__main__':
    main()
