#Copyright: Copyright 2016 /u/sagiksp, all right reserved.
#Seriously, don't be a dick.

import praw, time, re

#Variables

user_agent=""
username=""
password=""

users = [] #Array of all people that used the bot, and times of use. Format: [[Username,UTC_Time],[Username,UTC_Time],...]

yelled = []

Triggers = ('what', 'wut', 'wat')

footer = """***

[^^^Beep ^^^boop.](https://np.reddit.com/r/CantHearYouBot/)""" #Text to be in the end of a message

def check_condition(c): #Check the bot condition
    return (c.body.lower().rstrip('?') in Triggers) and (not RateLimit(c.author.name)) #Is the comment a trigger, and is the author not rate limited.

def bot_action(c,r): #Action the bot preforms
    global users
    parent = r.get_info(thing_id=c.parent_id) #get parent comment

    if isNotAValidComment(parent): return #If it is a response to a thread, stop.

    if parent.author.name == username and parent.body != "In da but": #If parent is bot and comment is not "in da but"
        return

    users.append([c.author.name,c.created_utc]) #Add username and time of use to the users list


    if check_condition(parent): #What What
        try: #Crashed without this
            c.reply("In da but")
        except:
            pass
        return

    lines = parent.body.split("\n") #Split parent into lines
    total = ""
    for line in lines: #for each line
        total += parseLine(line) #Parse line and add to total
    try: #Crashes without this
        c.reply(total + footer) #reply
        print("\n"+total+"\n\n") #Debug
    except:
        return

def findUsersWithName(name): #find all people with username on the users list
    uses = []
    for use in users: #For each use
        if use[0] == name: #If use name is username
            uses.append(use) 
    return uses #Yesus

def getLastTimeOfUse(name): #Get last time a username has used the bot
    return findUsersWithName(name)[-1][1]

def RateLimit(username): #Boolean. if user has used the bot in the last 5 minutes, stop.
    if username == "sagiksp": return False #unlimited testing
    c_time = time.time() #Current time
    if findUsersWithName(username) == []: #first time using the bot
        return False #No Rate limiting
    lastUseTime = getLastTimeOfUse(username) #Latest time of use
    return (c_time - lastUseTime) <= 300 #has the user used the bot in the last 300 seconds (5 minutes)

def parseLine(line):
    # Some basic parsing rules that bypass the rest of our logic.
    if line == '' or line == '***': # Restore split newline // Horizontal rule
        return line + '\n'
    
    # Bold the line
    if line[0] == ">":
       line = ">#" + line[1:]
    elif line[0] != '#':
       line = '#' + line
    
    # Uppercase the line, all except URLs. Could probably be made more effective?
    ldata = re.split(r"(\[.*?\]\(.*?\))", line) # this finds reddit markdown URLs, i.e. [google](http://google.com)
    line = ''
    for content in ldata:
        if not content.startswith('['): # typical string
            content = content.upper()
        else:
            # url; so let's break it up a little further and capitalize the title also
            url_groups = re.search(r"\[(.*)\]\((.*)\)", content)
            content = '[' + url_groups.group(1).upper() + '](' + url_groups.group(2) + ')'
        
        line += content
    
    # Finally, return!
    return line + '\n'

def isNotAValidComment(thing): #Is it not a valid comment
    return hasattr(thing,"domain") #If it has domain, It's a post, so ignore.

r = praw.Reddit(user_agent) #user_agent

r.login(username=username,password=password)

for c in praw.helpers.comment_stream(r, 'all'): #for all comments
    if check_condition(c): #If condition
        bot_action(c,r) #Action
