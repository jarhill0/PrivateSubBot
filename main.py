import sys
import time

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
    daily.main()

    reddit = helpers.initialize_reddit()
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
            reddit.subreddit(config.target_subreddit).contributor.add(user)
        else:
            print('Testing: added {}.'.format(user))


def build_and_post_gist(users, urls):
    gist_lines = ['# Comments for entry', '\n']
    for user, url in zip(users, urls):
        gist_lines.append('{}: {}  '.format(user, url))
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
    for user in users:
        if not config.testing:
            try:
                reddit.subreddit(config.target_subreddit).flair.set(
                    redditor=user,
                    text=config.text_removed,
                    css_class=config.flair_removed)
                reddit.subreddit(config.target_subreddit).contributor.remove(user)
            except (praw.exceptions.APIException, prawcore.exceptions.BadRequest):
                # Deleted user, most likely
                pass
        else:
            print('Testing: Flaired and removed {}.'.format(user))


def flair_users(users, reddit, default_flair_class, number_adjustment=0):
    for i, name in enumerate(users):
        i += 1 + number_adjustment
        flair_class = config.special_flairs.get(i, default_flair_class)
        if not config.testing:
            try:
                reddit.subreddit(config.target_subreddit).flair.set(
                    redditor=name,
                    text='#{}'.format(i),
                    css_class=flair_class)
            except (praw.exceptions.APIException, prawcore.exceptions.BadRequest):
                # Deleted user, most likely
                pass
        else:
            print('Testing: Flaired {} as #{} (class "{}")'.format(name, i, flair_class))


def get_new_users(reddit, number, current_users):
    raw_new_users = []
    for comment in reddit.subreddit('all').comments(limit=number + 10):
        try:
            raw_new_users.append((comment.author.name, 'https://reddit.com' + comment.permalink))
        except AttributeError:
            # reddit changed the name of permalink in their API, hopefully to permalink_url
            try:
                raw_new_users.append((comment.author.name, 'https://reddit.com' + comment.permalink_url))
            except AttributeError:
                raw_new_users.append((comment.author.name, 'Permalink loading failed.'))

    new_users = []
    new_user_urls = []
    while len(new_users) < number:
        user = raw_new_users.pop()
        if user[0] not in current_users and user[0] not in config.redditor_blacklist:
            new_users.append(user[0])
            new_user_urls.append(user[1])
    return new_users, new_user_urls


def make_post(title, text, reddit, *, distinguish=config.distinguish_log, sticky=config.sticky_log):
    if not config.testing:
        new_post = reddit.subreddit(config.target_subreddit).submit(
            title,
            selftext=text,
            send_replies=False)
        if distinguish:
            reddit.submission(id=new_post.id).mod.distinguish(how='yes')
        if sticky:
            reddit.submission(id=new_post.id).mod.sticky()
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


def valid_user(username, reddit):
    """Return 1 if user is shadowbanned and 2 if they are deleted; else 0"""
    user = reddit.redditor(username)
    try:
        user.unblock()
    except prawcore.exceptions.BadRequest:
        return 2
    else:
        try:
            user.fullname
        except prawcore.exceptions.NotFound:
            return 1
        else:
            return 0


if __name__ == '__main__':
    main()
