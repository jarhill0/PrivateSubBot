import time

import praw
import prawcore

import config
import daily
import helpers
import post_gist
import updates


def main():
    daily.main()

    reddit = helpers.initialize_reddit()
    participated = set(helpers.load_data('participated'))
    stats = helpers.load_data('stats')
    user_list = helpers.load_data('user_list')
    helpers.write_log_trash('User list %s' % helpers.date_string(), user_list)

    updated_list, not_participated = segregate_users(user_list, participated)
    helpers.write_log_trash('Not participated %s' % helpers.date_string(), not_participated)

    flair_and_remove(not_participated, reddit)
    flair_users(updated_list, reddit, config.flair_normal)

    new_users, new_user_urls = get_new_users(reddit, max(min(len(not_participated), 25), 10), updated_list)
    helpers.write_log_trash('New users %s' % helpers.date_string(), new_users)

    post_text = build_removed_text(user_list, not_participated) + \
                '\n\n' + build_new_text(new_users, len(updated_list) + 1)

    if config.entry_comments:
        post_text += '\n\n[Comments for entry](%s)' % build_and_post_gist(new_users, new_user_urls)
    if config.stats_section:
        post_text += '\n\n# Info:\n\n'
        post_text += '- %d users kicked\n' % len(not_participated)
        post_text += '- %d users added\n' % len(new_users)
        diff = len(new_users) - len(not_participated)
        change = '+%d' % diff if diff >= 0 else str(diff)
        post_text += '- Membercap: %d (%s)' % ((len(updated_list) + len(new_users)), change)

    title = config.main_log_title
    if config.title_date:
        title = helpers.date_string() + ' - ' + title
    if config.title_number:
        stats['log_count'] += 1
        title += ' #%d' % stats['log_count']

    make_post(title, post_text, reddit)

    add_users(new_users, reddit)
    flair_users(new_users, reddit, 'numbernew', number_adjustment=len(updated_list))

    updated_list_copy = updated_list[:]
    updated_list_copy.extend(new_users)
    if config.update_sidebar:
        updates.update_sidebar(updated_list_copy)
    if config.change_title:
        updates.change_title()

    stats['last_full_run'] = time.time()
    helpers.write_data('stats', stats)
    helpers.write_data('user_list', updated_list_copy)
    helpers.write_data('participated', [])


def add_users(users, reddit):
    for user in users:
        if not config.testing:
            reddit.subreddit(config.target_subreddit).contributor.add(user)
        else:
            print('Testing: added %s.' % user)


def build_and_post_gist(users, urls):
    gist_body = '# Comments for entry\n\n'
    for user, url in zip(users, urls):
        gist_body += '%s: %s  \n' % (user, url)
    return post_gist.make_gist(gist_body)


def build_new_text(new_users, starting_index):
    index = starting_index
    text = '# New users\n\n'

    for user in new_users:
        text += '- #%d /u/%s\n' % (index, user)
        index += 1

    return text


def build_removed_text(user_list, removed):
    text = '# Users removed\n\n'
    for user in removed:
        text += '- #%d /u/%s\n' % (user_list.index(user) + 1, user)
    return text


def flair_and_remove(users, reddit):
    for user in users:
        if not config.testing:
            try:
                reddit.subreddit(config.target_subreddit).flair.set(
                    redditor=user,
                    text='Removed',
                    css_class='kicked')
                reddit.subreddit(config.target_subreddit).contributor.remove(user)
            except praw.exceptions.APIException:
                # Deleted user, most likely
                pass
        else:
            print('Testing: Flaired and removed %s.' % user)


def flair_users(users, reddit, default_flair_class, number_adjustment=0):
    for i, name in enumerate(users):
        i += 1 + number_adjustment
        flair_class = config.special_flairs.get(i, default_flair_class)
        if not config.testing:
            try:
                reddit.subreddit(config.target_subreddit).flair.set(
                    redditor=name,
                    text='#%d' % i,
                    css_class=flair_class)
            except praw.exceptions.APIException:
                # Deleted user, most likely
                pass
        else:
            print('Testing: Flaired %s as #%d (class "%s")' % (name, i, flair_class))


def get_new_users(reddit, number, current_users):
    raw_new_users = []
    for comment in reddit.subreddit('all').comments(limit=number + 10):
        raw_new_users.append((comment.author.name, 'https://reddit.com' + comment.permalink(fast=True)))
    new_users = []
    new_user_urls = []
    for user in raw_new_users:
        if len(new_users) < number and user[0] not in current_users:
            new_users.append(user[0])
            new_user_urls.append(user[1])
    return new_users, new_user_urls


def make_post(title, text, reddit):
    if not config.testing:
        new_post = reddit.subreddit(config.target_subreddit).submit(
            title,
            selftext=text,
            resubmit=False)
        if config.distinguish_log:
            reddit.submission(id=new_post.id).mod.distinguish(how='yes', sticky=True)
        if config.sticky_log:
            reddit.submission(id=new_post.id).mod.sticky()
    else:
        print('Testing: submitted %s:\n\n%s' % (title, text))


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
