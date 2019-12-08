from helpers import initialize_reddit, load_data, write_data
from main import get_new_users


def acquire():
    reddit = initialize_reddit()
    user_list = load_data("user_list")
    new_users, new_user_urls = get_new_users(reddit, 1, user_list)

    potential_adds = load_data("potential_adds", {"users": [], "urls": []})
    while new_users[0] in potential_adds["users"]:  # just in case!!
        new_users, new_user_urls = get_new_users(reddit, 1, user_list)
    potential_adds["users"].append(new_users[0])
    potential_adds["urls"].append(new_user_urls[0])
    write_data("potential_adds", potential_adds)


if __name__ == "__main__":
    acquire()
