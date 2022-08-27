# Configuration page for Private Sub Bot
# note: boolean (True/False) values must have a capital first letter (True, False)
# by default, the only settings you should have to edit are bot_username and target_subreddit
# the bot relies on css flair classes in your target subreddit matching flair_normal and flair_new and matching
# css classes for any classes in special_flairs.

# RENAME THIS FILE TO config.py OR ELSE THE BOT WILL NOT RUN

# Username of your bot. Configuration should be in praw.ini under the same name.
bot_username = "My_bot"
# Name of the private subreddit the bot should operate on
target_subreddit = "My_subreddit"
# Reddit user-agent
user_agent = "script:jarhill0.privatesubmanager:v1.0"

#

# Set to True to prevent making any changes to Reddit, instead printing them to the terminal. For normal
# operation, this should be False.
testing = False

#

# Set to a username to forward all messages to that user at startup. Leave empty to not.
forward_user = ""

#

# List users in the format ['username', 'otherUsername'] to blacklist them from being selected and added. Set to []
# to blacklist nobody
redditor_blacklist = ["AutoModerator", "ImagesOfNetwork"]

#

# Unchanging portion of the log title
main_log_title = "Bot Recap"
# Set to True to number threads sequentially. Relies on "log_count" in data/stats.json
title_number = False
# Set to True to include a date in thread titles
title_date = True
# Set to True to post a list of URLs of comments that users were selected for in the post body
entry_comments = False
# Github Personal Access Token. Required if entry_comments is True.
github_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# Set to True to post a section of numbers about user cap size in the post body
stats_section = True
# Set to True to sticky the post
sticky_log = False
# Set to True to distinguish the post
distinguish_log = True

#

# Flair ID that normal (not new) users should have
flair_normal = "0d60bf96-9c86-11e5-a780-0e2ecdd90c97"
# Flair ID that new users should have
flair_new = "106ca47a-9c86-11e5-8c5d-0e5a3bfc8c5f"
# Flair ID that removed users should have
flair_removed = "6a077900-a1c8-11e5-b1a4-0e19731430eb"
# Flair text for removed users
text_removed = "Removed"
# Special flair IDs for users with specific numbers. The number is the number that gets a special flair
# type, and the string is the name of that flair's ID. The examples (0 and -1) will not have any effect.
special_flairs = {
    0: "f5c8cfb3a5e0-d5c8-5e11-68c9-a74ac601",
    -1: "be03413791e0-4a1b-5e11-8c1a-009770a6",
}

#

# Set to True to change the sidebar with a list of users. Everything that precedes the list should go in the first
# sidebar text path (by default, text_values/sidebar part 1.txt), and everything that goes after the user list should go
# in the second text file (by default, text_values/sidebar part 2.txt).
update_sidebar = False
# Tuple with two filepaths for the purposes described above. Only necessary if update_sidebar is True.
sidebar_text_paths = (
    ("text_values", "sidebar part 1.txt"),
    ("text_values", "sidebar part 2.txt"),
)

#

# Set to True to update the top sticky with a list of current users.
update_top_sticky = False
# Set the title of the top sticky. Top sticky will only be updated if it matches.
top_sticky_title = ""

#

# Set to True to update the subreddit with a random title once a week.
change_title = False
# Path to a json list of titles. Only necessary if change_title is True.
titles_path = ("text_values", "titles.json")

#

# Set to True to enable a random delay at the beginning of main runs.
delay = False
# Maximum delay in minutes
max_delay = 15
