from datetime import date
from sys import argv, exit, stderr

import helpers

try:
    import config
except (ImportError, ModuleNotFoundError):
    print(
        "config.py not found. Rename config.example.py to config.py after configuration.",
        file=stderr,
    )
    exit(1)


def main():
    if len(argv) != 3:
        print(f"Usage: python3 {argv[0]} <day of week (num)> <on|off>", file=stderr)
        return 1
    try:
        dow = int(argv[1])
    except ValueError:
        print(f"{argv[1]!r} is not a number", file=stderr)
        return 1

    # Monday is 1. Compatibility with crontab.
    if dow % 7 != date.today().isoweekday() % 7:
        return 0  # we just do nothing.

    if argv[2] == "on":
        link_type = "any"
    elif argv[2] == "off":
        link_type = "self"
    else:
        print(f"Unknown option {argv[1]!r}")
        return 1

    reddit = helpers.initialize_reddit()
    subreddit = reddit.subreddit(config.target_subreddit)
    subreddit.mod.update(link_type=link_type)


if __name__ == "__main__":
    exit(main())
