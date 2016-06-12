#Made by /u/sagiksp

username="" #BOTS NAME
password="" #BOTS PASSWORD
creator_name="" #YOUR NAME (WITHOUT THE /U/)
bot_subreddit="" #BOTS SUBREDDIT

import praw, time, re

#Variables

user_agent="Cant Hear You by /u/"+creator_name #The name the bot will use to communicate with reddit.
users = [] #People that have been yelled at. Format: [[Username,UTC_Time],[Username,UTC_Time],...]
banned_users = ["TheWutBot", "TheWallGrows","AutoModerator"] #Other bots
Triggers = ('what', 'wut', 'wat', 'wot')
no_link_subs = ("ImGoingToHellForThis") #Subs that have asked me not to link to the subreddit

footer = { #text at the end of the post. !normal is the default, !no_link is without links and the rest are for custom subs
"!normal":"***\n\n##[^^^(I&#32;am&#32;a&#32;bot,&#32;and&#32;I&#32;don't&#32;respond&#32;to&#32;myself.)](https://np.reddit.com/r/"+bot_subreddit+"/)",

"!no_link":"***\n\n^^^(I&#32;am&#32;a&#32;bot,&#32;and&#32;I&#32;don't&#32;respond&#32;to&#32;myself.)",

"totallynotrobots":"***\n\n##[^^^HELLO ^^^FELLOW ^^^HUMANS! ^^^I ^^^AM ^^^A ^^^~~bot~~HUMAN ^^^TOO, ^^^AND ^^^I ^^^DON'T ^^^RESPOND ^^^TO ^^^MYSELF.](https://np.reddit.com/r/"+bot_subreddit+"/)"
}

def check_condition(c): #The condition for the bot. If this is true, the bot will comment.
    return (c.body.lower().rstrip('?') in Triggers) and (not RateLimit(str(c.author))) #Is the comment a trigger, and is the author not rate limited.

def bot_action(c,r): #Action the bot preforms
    global users
    parent = r.get_info(thing_id=c.parent_id) #get parent comment
    
    if str(parent.author) in banned_users or str(c.author) in banned_users: return #If users banned: return
    
    if isNotAValidComment(parent): return #If it is a response to a thread, stop.
    subreddit = str(c.subreddit)

    if str(parent.author) == username and parent.body != "In da but": #If parent is bot and comment is not "in da but"
        return

    users.append([str(c.author),c.created_utc]) #Add username and time of use to the users list


    if check_condition(parent): #If both comments are triggers, ie. What What
        try:
            c.reply("In da but")
        except:
            pass
        return

    lines = parent.body.split("\n") #Split parent into lines
    total = ""
    for line in lines: #for each line
        pLine = parseLine(line) #Parse line
        total += pLine
    try:
        c.reply(total + get_footer(subreddit))
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
    if username == creator_name: return False #unlimited testing
    c_time = time.time() #Current time
    if findUsersWithName(username) == []: #first time using the bot
        return False #No Rate limiting
    lastUseTime = getLastTimeOfUse(username) #Latest time of use
    return (c_time - lastUseTime) <= 300 #has the user used the bot in the last 300 seconds (5 minutes)

def get_footer(subreddit): #gets footer via subreddit name
    ft = ""
    if subreddit in no_link_subs:
        ft = footer["!no_link"]
    elif subreddit in footer:
        ft = footer[subreddit]
    else:
        ft = footer["!normal"]
    return ft

def parseLine(line): #Written by the awesome sctigercat1
    # Some basic parsing rules that bypass the rest of our logic.
    if line == '' or line == '***': # Restore split newline // Horizontal rule
        return line + '\n'
     
     #Bold the line
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

#Bot code

r = praw.Reddit(user_agent) #user_agent

r.login(username=username,password=password,disable_warning=True)

for c in praw.helpers.comment_stream(r, 'all'): #for all comments
    if check_condition(c): #If condition
        bot_action(c,r) #Action
