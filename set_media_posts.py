from sys import argv, exit, stderr
import helpers

try:
    import config
except (ImportError, ModuleNotFoundError):
    print(
        "config.py not found. Rename config.example.py to config.py after configuration."
    )
    exit(1)


def main():
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} [on|off]", file=stderr)
        return 1
    if argv[1] == "on":
        link_type = "any"
    elif argv[1] == "off":
        link_type = "self"
    else:
        print(f"Unknown option {argv[1]!r}")
        return 1

    reddit = helpers.initialize_reddit()
    subreddit = reddit.subreddit(config.target_subreddit)
    subreddit.mod.update(link_type=link_type)


if __name__ == "__main__":
    exit(main())
