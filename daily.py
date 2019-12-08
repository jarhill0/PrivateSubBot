import sys
import time

import forward_messages
import helpers

try:
    import config
except (ImportError, ModuleNotFoundError):
    print(
        "config.py not found. Rename config.example.py to config.py after configuration."
    )
    sys.exit(1)


def main():
    if config.forward_user:
        forward_messages.forward(config.forward_user)

    reddit = helpers.initialize_reddit()
    participated = set(helpers.load_data("participated"))
    stats = helpers.load_data("stats")

    participated = participated.union(get_participants(reddit, stats["last_daily_run"]))

    helpers.write_data("participated", list(participated))
    stats["last_daily_run"] = (
        time.time() - 60
    )  # to cover accidental gaps due to execution time
    helpers.write_data("stats", stats)


def get_participants(reddit, last_check):
    participated = set()
    old_comments = False
    old_submissions = False

    for submission in reddit.subreddit(config.target_subreddit).new(limit=None):
        if submission.created_utc < last_check:
            old_submissions = True
            break
        try:
            participated.add(submission.author.name)
        except AttributeError:
            # More than likely a deleted user
            pass

    for comment in reddit.subreddit(config.target_subreddit).comments(limit=None):

        if comment.created_utc < last_check:
            old_comments = True
            break
        try:
            participated.add(comment.author.name)
        except AttributeError:
            # More than likely a deleted user
            pass

    if (
        not old_comments or not old_submissions
    ) and "--ignore-old-comments-warning" not in sys.argv:
        raise Exception(
            "Not all old comments were retrieved. Run again with --ignore-old-comments-warning to "
            "suppress."
        )

    return participated


if __name__ == "__main__":
    main()
