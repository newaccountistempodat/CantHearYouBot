#Copyright © /u/sagiksp 2016, all right reserved.
#Seriously, don't be a dick.

import praw, time

#Variables

user_agent="CantHearYou by /u/sagiksp"
username=""
password=""

users = [] #Array of all people that used the bot, and times of use. Format: [[Username,UTC_Time],[Username,UTC_Time],...]

yelled = []

Triggers = ['What', 'what', 'WHAT', 'What?', 'what?', 'WHAT?',
             'Wut', 'wut', 'WUT', 'Wut?', 'wut?', 'WUT?',
             'Wat', 'wat', 'WAT', 'Wat?', 'wat?', 'WAT?'] #Texts that trigger the bot.

footer = """***

[^^^Beep ^^^boop.](https://np.reddit.com/r/CantHearYouBot/)""" #Text to be in the end of a message

def check_condition(c): #Check the bot condition
    return (c.body in Triggers) and (not RateLimit(c.author.name)) #Is the comment a trigger, and is the author not rate limited.

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
    #For the gods of python above, please make a switch statement.
    if line == "": return "\n" 
    if line[0] ==  "#": return line.upper() + "\n" #If line already bolded, ignore.
    if line == "***": return "***\n" #If line is *** (Horizontal rule), ignore.
    if line == "[^^^Beep ^^^boop.](https://np.reddit.com/r/CantHearYouBot/)": return "#[^^^BEEP ^^^BOOP.](https://np.reddit.com/r/CantHearYouBot/)\n" #TODO: Make links work. Currently it capitalizes the link address. A work around for the subreddit link
    if line == "#[^^^BEEP ^^^BOOP.](https://np.reddit.com/r/CantHearYouBot/)": return line + "\n" #Here too. It's not working. Send help.
    return "#" + line.upper() + "\n" #For normal lines, bold it and go home.

def isNotAValidComment(thing): #Is it not a valid comment
    return hasattr(thing,"domain") #If it has domain, It's a post, so ignore.

r = praw.Reddit(user_agent) #user_agent

r.login(username=username,password=password)

for c in praw.helpers.comment_stream(r, 'all'): #for all comments
    if check_condition(c): #If condition
        bot_action(c,r) #Action
