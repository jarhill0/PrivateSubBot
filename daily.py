import sys
import time

import helpers

try:
    import config
except (ImportError, ModuleNotFoundError):
    print('config.py not found. Rename config.example.py to config.py after configuration.')
    sys.exit(1)


def main():
    reddit = helpers.initialize_reddit()
    participated = set(helpers.load_data('participated'))
    stats = helpers.load_data('stats')

    participated = participated.union(get_participants(reddit, stats['last_daily_run']))

    helpers.write_data('participated', list(participated))
    stats['last_daily_run'] = time.time() - 60  # to cover accidental gaps due to execution time
    helpers.write_data('stats', stats)


def get_participants(reddit, last_check):
    now = time.time()
    participated = set()
    old_comments = False

    for submission in reddit.subreddit(config.target_subreddit).submissions(start=last_check, end=now):
        try:
            participated.add(submission.author.name)
        except AttributeError:
            # More than likely a deleted user
            pass

    for comment in reddit.subreddit(config.target_subreddit).comments(limit=1000):

        if comment.created_utc > last_check:  # perplexingly, created_utc returns the creation time in local time
            try:
                participated.add(comment.author.name)
            except AttributeError:
                # More than likely a deleted user
                pass
        else:
            old_comments = True
            break

    if not old_comments:
        raise Exception('Not all old comments were retrieved.')

    return participated


if __name__ == '__main__':
    main()
