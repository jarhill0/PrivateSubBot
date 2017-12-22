import os
import random
import sys
import time
import traceback

import praw
import prawcore

import daily
import helpers
import post_gist
import updates

try:
    import config
except (ImportError, ModuleNotFoundError):
    print('config.py not found. Rename config.example.py to config.py after configuration.')
    sys.exit(1)


def main():
    if config.delay:
        time.sleep(random.randrange(0, config.max_delay * 60))

    daily.main()

    reddit = helpers.initialize_reddit()  # will exit if Reddit isn't properly initialized
    check_permissions(reddit)  # will check if bot has all needed permissions; exit on failure
    participated = set(helpers.load_data('participated'))
    stats = helpers.load_data('stats')
    user_list = helpers.load_data('user_list')
    helpers.write_log_trash('User list {}'.format(helpers.date_string()), user_list)

    if stats['last_full_run'] + 23 * 60 * 60 > time.time():
        if '--override_time' not in sys.argv:
            msg = 'Less than 23 hours since last run. Exiting. Run with "--override_time" as an option to disregard'
            print(msg)
            helpers.write_log_trash('Failed {}'.format(helpers.date_string()), msg)
            sys.exit(1)

    updated_list, not_participated = segregate_users(user_list, participated)
    helpers.write_log_trash('Not participated {}'.format(helpers.date_string()), not_participated)

    flair_and_remove(not_participated, reddit)
    flair_users(updated_list, reddit, config.flair_normal)

    new_users, new_user_urls = get_new_users(reddit, max(min(len(not_participated), 25), 10), updated_list)
    helpers.write_log_trash('New users {}'.format(helpers.date_string()), new_users)

    post_text_lines = [build_removed_text(user_list, not_participated), '\n',
                       build_new_text(new_users, len(updated_list) + 1), '\n']

    if config.entry_comments:
        post_text_lines.append('\n[Comments for entry]({})'.format(build_and_post_gist(new_users, new_user_urls)))
    if config.stats_section:
        post_text_lines.append('\n# Info:\n')
        post_text_lines.append('- {} users kicked'.format(len(not_participated)))
        post_text_lines.append('- {} users added'.format(len(new_users)))
        diff = len(new_users) - len(not_participated)
        change = '+{}'.format(diff) if diff >= 0 else str(diff)
        post_text_lines.append('- Membercap: {} ({})'.format((len(updated_list) + len(new_users)), change))

    post_text = '\n'.join(post_text_lines)

    title = config.main_log_title
    if config.title_date:
        title = helpers.date_string() + ' - ' + title
    if config.title_number:
        stats['log_count'] += 1
        title += ' #{}'.format(stats['log_count'])

    make_post(title, post_text, reddit)

    if config.change_title:
        updates.change_title()

    add_users(new_users, reddit)
    flair_users(new_users, reddit, 'numbernew', number_adjustment=len(updated_list))

    updated_list_copy = updated_list[:]
    updated_list_copy.extend(new_users)
    if config.update_sidebar:
        updates.update_sidebar(updated_list_copy)

    stats['last_full_run'] = time.time()
    helpers.write_data('stats', stats)
    helpers.write_data('user_list', updated_list_copy)
    helpers.write_data('participated', [])


def add_users(users, reddit):
    for user in users:
        if not config.testing:
            try:
                reddit.subreddit(config.target_subreddit).contributor.add(user)
            except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
                error = traceback.format_exc() + '\n'
                helpers.write_log_trash('Exception: add_users() {}'.format(helpers.date_string()), error)
        else:
            print('Testing: added {}.'.format(user))


def build_and_post_gist(users, urls):
    gist_lines = ['# Comments for entry', '\n', 'User|Comment', '---|---']
    for user, url in zip(users, urls):
        gist_lines.append('/u/{} | {}  '.format(user, url))
    gist_body = '\n'.join(gist_lines)
    return post_gist.make_gist(gist_body)


def build_new_text(new_users, starting_index):
    index = starting_index
    lines = ['# New users\n']

    for user in new_users:
        lines.append('- #{} /u/{}'.format(index, user))
        index += 1

    text = '\n'.join(lines)
    return text


def build_removed_text(user_list, removed):
    lines = ['# Users removed\n']
    for user in removed:
        lines.append('- #{} /u/{}'.format(user_list.index(user) + 1, user))

    text = '\n'.join(lines)
    return text


def flair_and_remove(users, reddit):
    if not config.testing:
        try:
            reddit.subreddit(config.target_subreddit).flair.update(users, config.text_removed, config.flair_removed)
        except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
            # Deleted user, most likely
            pass
    else:
        print('Testing: Flaired as removed {}.'.format(users))

    for user in users:
        if not config.testing:
            try:
                reddit.subreddit(config.target_subreddit).contributor.remove(user)
            except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
                # Deleted user, most likely
                pass
        else:
            print('Testing: Removed {}.'.format(user))


def flair_users(users, reddit, default_flair_class, number_adjustment=0):
    flair_list = []
    for i, name in enumerate(users):
        i += 1 + number_adjustment
        text = '#{}'.format(i)
        flair_class = config.special_flairs.get(i, default_flair_class)

        flair_list.append({'user': name, 'flair_text': text, 'flair_css_class': flair_class})

    if not config.testing:
        try:
            # will return errors if needed but does not raise exceptions for unrecognized users
            reddit.subreddit(config.target_subreddit).flair.update(flair_list)
        except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
            # Likely a recoverable error
            pass
    else:
        print('Testing: Flaired {}.'.format(flair_list))


def get_new_users(reddit, number, current_users):
    raw_new_users = []
    for comment in reddit.subreddit('all').comments(limit=number + 10):
        raw_new_users.append((comment.author.name, 'https://reddit.com' + comment.permalink))
    new_users = []
    new_user_urls = []
    while len(new_users) < number:
        user = raw_new_users.pop()
        if user[0] not in current_users and user[0] not in config.redditor_blacklist and valid_user(user[0], reddit):
            new_users.append(user[0])
            new_user_urls.append(user[1])
    return new_users, new_user_urls


def make_post(title, text, reddit, *, distinguish=config.distinguish_log, sticky=config.sticky_log):
    if not config.testing:
        try:
            new_post = reddit.subreddit(config.target_subreddit).submit(
                title,
                selftext=text,
                send_replies=False)
        except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
            error = traceback.format_exc() + '\n'
            helpers.write_log_trash('Exception: make_post(), submit {}'.format(helpers.date_string()), error)
            return
        if distinguish:
            try:
                reddit.submission(id=new_post.id).mod.distinguish(how='yes')
            except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
                error = traceback.format_exc() + '\n'
                helpers.write_log_trash('Exception: make_post(), distinguish {}'.format(helpers.date_string()), error)
        if sticky:
            try:
                reddit.submission(id=new_post.id).mod.sticky()
            except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
                error = traceback.format_exc() + '\n'
                helpers.write_log_trash('Exception: make_post(), sticky {}'.format(helpers.date_string()), error)
    else:
        print('Testing: submitted {}:\n\n{}'.format(title, text))


def segregate_users(user_list, participated):
    not_participated = []
    new_list = []
    for user in user_list:
        if user in participated:
            new_list.append(user)
        else:
            not_participated.append(user)

    return new_list, not_participated


def valid_user(user, reddit):
    """Return False if user is banned or deleted; else 0"""
    if isinstance(user, str):
        user = reddit.redditor(user)
    if not isinstance(user, praw.models.reddit.redditor.Redditor):
        raise TypeError("User should be a str or Redditor.")
    try:
        user.unblock()
    except prawcore.exceptions.BadRequest:
        return False
    else:
        try:
            user.fullname
        except prawcore.exceptions.NotFound:
            return False
        else:
            return True


def check_permissions(reddit):
    try:
        for m in reddit.subreddit(config.target_subreddit).moderator(reddit.user.me()):
            my_permissions = m.mod_permissions

    except (praw.exceptions.PRAWException, prawcore.PrawcoreException):
        err = traceback.format_exc() + '\n'
        helpers.write_log_trash('check_permissions() {}'.format(helpers.date_string()), err)
        sys.exit(1)

    # noinspection PyUnboundLocalVariable
    perms = ['access' in my_permissions, 'flair' in my_permissions]
    if config.distinguish_log or config.sticky_log:
        perms.append('posts' in my_permissions)
    if config.update_sidebar or config.change_title:
        perms.append('config' in my_permissions)

    if not (all(perms) or 'all' in my_permissions):
        msg = 'Have: {}\n'.format(my_permissions)
        helpers.write_log_trash('Insufficient Permissions {}'.format(helpers.date_string()), msg)
        sys.exit(1)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        main()
    except:
        with open(os.path.join(helpers.folder_path(), 'log_trash', 'ERROR {}'.format(helpers.date_string())), 'w') as f:
            traceback.print_exc(file=f)
