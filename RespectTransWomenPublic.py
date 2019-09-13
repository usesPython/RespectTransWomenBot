import praw #Used to interact with the reddit API
import signal #Used to know when we need to exit
from sys import exit #Preferred over default exit() (See: https://stackoverflow.com/questions/6501121/difference-between-exit-and-sys-exit-in-python/6501134#6501134

class GracefulExiter():
    #Handles SIGINT (Signal interrupt) signals (Raised by pressing Ctrl-C)
    #Instantiate it using with since that allows us to set the SIGINT handler back to SIG_DFL when we're out of a critical section
    #Example usage:
    #with GracefulExiter() as exiter:
    #   while True:
    #       #do stuff
    #       if exiter.get_exit_flag()
    #           #handle exiting gracefully
    #Prefered over:
    #from threading import Thread
    #try:
    #   thread = Thread(target=func, args=(foo,bar))
    #   thread.start()
    #   thread.join()
    #catch KeyboardInterrupt:
    #   #do stuff
    #In cases where code in the catch block being run while thread is being run causes errors (can happen if KeyboardInterrupt is raised between thread.start() and thread.join())
        
    def __init__(self):
        self.state = False #Has SIGINT been raised?
        signal.signal(signal.SIGINT, self.change_state) #If SIGINT is raised then run self.change_state()
        
    def __enter__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state) #If SIGINT is raised then run self.change_state()
    
    def __exit__(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL) #If SIGINT is raised after this point then run the default SIGINT handler (Generally kills the program, but technically is implementation defined)
    
    def change_state(self, signum, frame):
        print("Exiting, repeat to shutdown immediately.")
        self.state = True #SIGINT has been raised
        signal.signal(signal.SIGINT, signal.SIG_DFL) #If SIGINT is raised after this point then run the default SIGINT handler (Generally kills the program, but technically is implementation defined)
    
    def get_exit_flag(self): #Returns True if SIGINT has been raised after object has been created, False otherwise
        return self.state

def main():
    #Initialize the bot
    print("Initializing bot")
    reddit = praw.Reddit(user_agent='Transphobia Notifier by /u/YourActualUsername', client_id='YOURIDHERE', client_secret="YOURSECRETHERE", username='RespectTransWomenBot', password="YOURPASSWORDHERE")
    reddit.read_only = False #False by default, but set to True if you need to do debugging and don't want the bot to post anything
    subreddit = reddit.subreddit("all") #Subreddit we are working in. Should be "all" but set to a subreddit you own for bot testing if you need to do debugging
    
    print("Getting blacklisted subreddits...", end=' ')
    blocked_subreddits = []
    try:
        #blockedsubreddits.txt formatting:
        #subreddit\n
        #empty lines (lines that only contain '\n') are ignored
        #e.g.:
        #sub1
        #sub2
        #
        #sub3
        #
        #returns ["sub1", "sub2", "sub3"]
        with open("D:/Reddit Bots/Respect Trans Women/blockedsubreddits.txt", "r") as fs: #Path to blockedsubreddits.txt
            blocked_subreddits = list(filter(None, fs.read().lower().split('\n'))) #Read all the subreddits in the file, then create a list where a new element is marked by a newline, then remove any empty strings
        print("done!")
    except Exception:
        print("Failed to get blocked subreddits!")
        print("To prevent accidentally replying to messages in a subreddit that should be blacklisted it's recommended to stop and check if everything is properly set up, but if you know what you're doing you can continue running this script.")
        while True:
            answer = input("Continue (y/n): ")
            if answer.lower().startswith('y'):
                break #Breaks out of the while loop and continues execution of the script
            elif answer.lower().startswith('n'):
                raise #Lets python handle the exception (Generally by printing the exception to console and then stopping the program)
    
    print("Getting blacklisted users...", end=' ')
    blocked_users = []
    try:
        #blockedusers.txt formatting:
        #subreddit\n
        #empty lines (lines that only contain '\n') are ignored
        #e.g.:
        #user1
        #user2
        #
        #user3
        #
        #returns ["user1", "user2", "user3"]
        with open("D:/Reddit Bots/Respect Trans Women/blockedusers.txt", "r") as fs: #Path to blockedusers.txt
            blocked_users = list(filter(None, fs.read().lower().split('\n'))) #Read all the users in the file, then create a list where a new element is marked by a newline, then remove any empty strings
        print("done!")
    except Exception:
        print("Failed to get blocked users!")
        print("To prevent accidentally replying to messages from an author that should be blacklisted it's recommended to stop and check if everything is properly set up, but if you know what you're doing you can continue running this script.")
        while True:
            answer = input("Continue (y/n): ")
            if answer.lower().startswith('y'):
                break #Breaks out of the while loop and continues execution of the script
            elif answer.lower().startswith('n'):
                raise #Lets python handle the exception (Generally by printing the exception to console and then stopping the program)
    
    print("Getting list of slurs...", end=' ')
    trigger_words = []
    try:
        #triggerwords.txt formatting:
        #word\n
        #empty lines (lines that only contain '\n') are ignored
        #e.g.:
        #word1
        #word2
        #
        #word3
        #
        #returns ["word1", "word2", "word3"]
        with open("D:/Reddit Bots/Respect Trans Women/triggerwords.txt", "r") as fs: #Path to triggerwords.txt
            trigger_words = list(filter(None, fs.read().lower().split('\n'))) #Read all the trigger words in the file, then create a list where a new element is marked by a newline, then remove any empty strings
        print("done!")
    except Exception:
        print("Failed to get the list of words that cause the bot to comment!")
        print("Since the bot doesn't know what words to look for and therefore probably wont do anything it's recommended to stop and check if everything is properly set up, but if you know what you're doing you can continue running this script.")
        while True:
            answer = input("Continue (y/n): ")
            if answer.lower().startswith('y'):
                break #Breaks out of the while loop and continues execution of the script
            elif answer.lower().startswith('n'):
                raise #Lets python handle the exception (Generally by printing the exception to console and then stopping the program)
    

    print("Getting comments we've already replied to...", end=' ')
    reply_ids = []
    try:
        #replyids.txt formatting:
        #commentid\n
        #empty lines (lines that only contain '\n') are ignored
        #e.g.:
        #id1
        #id2
        #
        #id3
        #
        #returns ["id1", "id2", "id3"]
        with open("D:/Reddit Bots/Respect Trans Women/replyids.txt", "r") as fs: #Path to replyids.txt
            reply_ids = list(filter(None, fs.read().lower().split('\n'))) #Read all the id's in the file, then create a list where a new element is marked by a newline, then remove any empty strings
        new_reply_index = len(reply_ids) #Used later so we know from which index new reply_ids start
        print("done!")
    except Exception:
        print("Failed to get id's of comments we've replied to!")
        print("To prevent accidentally replying to messages we've already replied to it's recommended to stop and check if everything is properly set up, but if you know what you're doing you can continue running this script.")
        while True:
            answer = input("Continue (y/n): ")
            if answer.lower().startswith('y'):
                break #Breaks out of the while loop and continues execution of the script
            elif answer.lower().startswith('n'):
                raise #Lets python handle the exception (Generally by printing the exception to console and then stopping the program)
    
    comments = subreddit.stream.comments()
    
    print("Bot initialized, starting main loop")

    with GracefulExiter() as exiter: #Used to check if we need to exit
        for comment in comments: #Current comment being processed is an object called comment . See https://praw.readthedocs.io/en/latest/code_overview/models/comment.html for more details on the comment object
            if isValidComment(comment, blocked_subreddits, blocked_users, reply_ids, trigger_words): #Preliminary check to see if we might be allowed to post on this comment
                #Further checking to verify we actually caught a slur
                formatted_comment = formatComment(comment)
                caught_words = slur_check(formatted_comment, trigger_words)
                if caught_words:
                    #Valid slur detected
                    message = formatReply(caught_words)
                    if reddit.read_only == False:
                        try:
                            comment.reply(message)
                            reply_ids.append(str(comment.id).lower())
                        except praw.exceptions.Forbidden: #Cannot post comment
                            print("Failed to post comment. Check if you are allowed to comment in the subreddit and if your login credentials are correct.")
                            print("Subreddit: /r/" + str(comment.subreddit)) #DEBUG INFORMATION
                            #raise #If problem persists uncomment raise so you can check the full error
                    else: #DEBUG MODE
                        print("Subreddit: /r/" + str(comment.subreddit))
                        print("Comment id:", str(comment.id))
                        try:
                            print("Author:", str(comment.author))
                        except AttributeError:
                            print("Author Deleted")
                        print("Original comment:")
                        print(str(comment.body))
                        print("Formatted comment:")
                        print(formatted_comment)
                        print("Caught words:")
                        print(caught_words)
                        print("Message reply:")
                        print(message)
            if exiter.get_exit_flag(): #SIGINT has been raised so we need to exit gracefully ASAP
                #Append new reply_ids to replyids.txt
                try:
                    with open("D:/Reddit Bots/Respect Trans Women/replyids.txt", "a") as fs: #Path to replyids.txt
                        while new_reply_index < len(reply_ids):
                            fs.write('\n' + reply_ids[new_reply_index]) #Preferred over reply_ids[new_reply_index] + '\n' since this guarantees all new ids will not be corrupted if writing is not interrupted
                            new_reply_index += 1
                    exit(0) #Reply ids are stored so we can send exit code zero, signalling "successful termination"
                except Exception:
                    print("Failed to store new reply ids to replyids.txt!")
                    exit(1) #Since we couldn't store replys we send a non-zero exit code, signalling "abnormal termination"

def isValidComment(comment, blocked_subreddits, blocked_users, reply_ids, trigger_words):
    #Fully checks if the comment is valid based on everything but the body of the comment and partially checks if the comment might be valid based on the body of the comment
    subreddit = str(comment.subreddit).lower()
    for blocked_subreddit in blocked_subreddits: #Check if the subreddit is blacklisted
        if subreddit == blocked_subreddit:
            return False

    try:
        author = str(comment.author).lower()
        if author == "RespectTransWomenBot".lower():
            return False
        for blocked_user in blocked_users: #Check if the user is blacklisted
            if author == blocked_user:
                return False
    except AttributeError: #If the comment object doesn't contain the author attribute then that means the account which posted the comment is deleted
            #return False

    id = str(comment.id).lower()
    for reply_id in reply_ids: #Check if we've already replied to the comment
        if id == reply_id:
            return False

    body = str(comment.body).lower()
    for trigger_word in trigger_words:
        if trigger_word in body: #Basic check to see if a slur could even possibly be present, more detailed checks should be done later to verify it's actually a slur
            return True

    return False

def formatComment(comment):
    body = str(comment.body)
    #Collapse quotes >Text
    #Collapse links [Text](www.example.com) IMPORTANT: Be careful with links such as [Pica (disorder)](http://en.wikipedia.org/wiki/Pica_\(disorder\)) as escape backslashes should be handled properly
    #Collapse strikethrough ~~Text~~
    #Collapse spoilers >!Text!<
    #Remove escape blackslashes 50\. Text   (Reddit would normally interpret 50. Text as a numbered list 1. Text but since we get the comment source text we need to clean that up)
    return body

def slurCheck(comment, trigger_words):
    caught_words = []
    #TODO: Implement this
    return caught_words

def formatReply(caught_words):
    message = "Please do not use "
    caught_len = len(caught_words)
    if caught_len == 1:
        message += caught_words[0] #Format the message in the form of "Please do not use a. It is..."
    elif caught_len == 2:
        message += caught_words[0] + " or " + caught_words[1] #Format the message in the form of "Please do not use a or b. It is..."
    else:
        caught_iter = 1
        for i in caught_words:
            if caught_len - caught_iter > 0: #Format the message in the form of "Please do not use a, b, or c. It is..."
                message += i + ", "
            else:
                message += "or " + i
            caught_iter += 1
    message += ". It is derogatory and a slur. Please use 'trans woman' instead.\n\n_____\n\n This is a bot."
    return message

main()
