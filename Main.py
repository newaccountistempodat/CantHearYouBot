# Copyright © /u/sagiksp 2016, all right reserved.
# Seriously, don't be a dick.
import time
import traceback

import praw

# Variables

# Self-explanatory
username = ""
password = ""
user_agent = ""

# Dict of all people that used the bot, and times of use.
# Format: {username: utc_time, etc.}
users = {}
# List of parent comments that have already been yelled.
yelled = []
# Words that activate the bot
triggers = ('what', 'wut', 'wat')
# Footer placed at the end of a comment with link to bot's subreddit.
footer = """***

[^^^Beep ^^^boop.](https://np.reddit.com/r/CantHearYouBot/)"""


def check_condition(comment):
    # type(praw.objects.Comment) -> bool
    # Check if a comment should trigger the bot.
    trigged = comment.body.lower().rstrip('?') in triggers
    return trigged and not rate_limit(comment.author.name)


def bot_action(comment, r):
    # type(praw.object.Comment, praw.Reddit) -> None
    # The actions of the bot, after doing some checks it will reply.

    # True if the comment is a top level reply.
    if comment.is_root:
        return

    parent = r.get_info(thing_id=comment.parent_id)
    # True if the comment has already been yelled.
    if parent.id in yelled:
        return
    # Prevent people from getting the bot to echo itself.
    if parent.author.name == username:
        return

    users.append([comment.author.name, comment.created_utc])
    yelled.append(parent.id)

    # True if both comments are triggers.
    # comment 1: what
    #   comment 2: what
    if check_condition(parent):
        try:
            comment.reply("In da but")
        except praw.errors.APIException:
            print("Error while replying to comment: ")
            traceback.print_exc()
        return

    lines = parent.body.splitlines()
    reply = ""
    for line in lines:
        reply += parse_line(line)

    try:
        comment.reply(reply + footer)
        print("Replying to user:\n{reply}".format(reply=reply))
        print("Permalink to comment: {url}".format(url=comment.permalink))
    except praw.errors.APIException:
        print("Error while replying to comment: ")
        traceback.print_exc()


def rate_limit(name):
    # type(str) -> bool
    current_time = time.time()
    if name not in users:
        return False
    last_use = users[name]
    return current_time - last_use <= 300


def parse_line(line):
    # type(str) -> str
    if line == "":
        return "\n"
    if line[0] == "#":
        return "{line}\n".format(line=line.upper())
    if line == "***":
        return "***\n"
    return "#{line}\n".format(line=line.upper())


if __name__ == "__main__":
    r = praw.Reddit(user_agent=user_agent)
    r.login(username=username, password=password, disable_warning=True)

    for comment in praw.helpers.comment_stream(r, 'all'):
        if check_condition(comment):
            bot_action(comment, r)
