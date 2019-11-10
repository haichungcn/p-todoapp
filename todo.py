import os
import sys
import fire
import code
import sqlite3
from datetime import datetime
from termcolor import colored
from acsii import header
import threading
import re
from setupDatabase import setup
from tabulate import tabulate
from commands import add_task, list_task, mark_task, remove_task, edit_task, create, list_user, checkUser, checkPassword, getUser, createUser, get_task_name, list_projects, list_history, who_to_fire

screenLock = threading.Lock()
screenLock.acquire()
setup()
screenLock.release()

currentUser = []

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

conn = sqlite3.connect(DEFAULT_PATH)
cur = conn.cursor()

isExit = False
isMenuShowed = True

def userLogin():
    global currentUser
    while not currentUser:
        print('\n', colored(f"""> Please type '1' to sign in \n or '2' to create a new user account \n or '3' to exit: \n """, "yellow", attrs=['bold']), end = colored('» ', 'yellow', attrs=['bold']))
        cmd = input()
        if '1' in cmd:
            print('\n', colored(f"""> Please enter your username: """, "cyan", attrs=['bold']), end = colored('» ', 'yellow', attrs=['bold']))
            userName = input()
            if checkUser(userName):
                print('\n', colored(f"""> Please enter your password: """, "magenta", attrs=['bold']), end = colored('» ', 'yellow', attrs=['bold']))
                userPassword = input()
                if checkPassword(userName, userPassword):
                    currentUser = getUser(userName)
                else:
                    print(colored(f"> You entered a wrong password for {userName}, please try again", 'red', attrs=['bold', 'blink']))
            else:
                print(colored(f"> You entered an unregistered username, please try again or start by creating new one", 'red', attrs=['bold', 'blink']))
        elif '2' in cmd:
            currentUser = createUser(currentUser)
        elif '3' in cmd:
            print(colored('\n' + 'Thank you for using the app, see you again soon, byebye ! \n ლ(╥﹏╥ლ)', 'red', attrs=['bold', 'blink']), "\n")
            sys.exit()            
        else:
            print('\n', colored(f"""> Enter either '1', '2' or '3' """, "yellow", attrs=['bold']))


def print_menu():
    print('\n', colored(f"""> Hi there, {currentUser[1]}, here are the commands you can use: """, "red", attrs=['bold']))
    print(f"""
        
        ┌ {colored("1.", "yellow", attrs=['bold'])} To create new project/user: {colored("create", "red", attrs=['bold'])}
        │                                ├ {colored("-u", "red", attrs=['bold'])} to create new user
        │                                └ {colored("-p", "red", attrs=['bold'])} to create new project
        ├ {colored("2.", "yellow", attrs=['bold'])} To display to-dos/projects : {colored("list", "red", attrs=['bold'])}    
        │                                ├ {colored("-a", "red", attrs=['bold'])} to display all
        │                                ├ {colored("-c", "red", attrs=['bold'])} to display all created by you                                             
        │                                ├ {colored("-u", "red", attrs=['bold'])} to display all undone
        │                                ├ {colored("-d", "red", attrs=['bold'])} to display all done
        │                                ├ {colored("-user", "red", attrs=['bold'])} to display all assigned to a user
        │                                └ {colored("-p", "red", attrs=['bold'])} to display all tasks in a project
        ├ {colored("3.", "yellow", attrs=['bold'])} To add new task: {colored("add", "red", attrs=['bold'])}                 
        ├ {colored("4.", "yellow", attrs=['bold'])} To change a task's status: {colored("mark", "red", attrs=['bold'])}      
        │                                ├ {colored("-u", "red", attrs=['bold'])} to mark it as undone
        │                                └ {colored("-d", "red", attrs=['bold'])} to mark it as done
        ├ {colored("5.", "yellow", attrs=['bold'])} To remove task: {colored("remove", "red", attrs=['bold'])}               
        ├ {colored("6.", "yellow", attrs=['bold'])} To edit task: {colored("edit", "red", attrs=['bold'])}                   
        ├ {colored("7.", "yellow", attrs=['bold'])} To display user: {colored("user", "red", attrs=['bold'])}   
        │                    ├ {colored("-a", "red", attrs=['bold'])} to see all registered users 
        │                    └ {colored("-i", "red", attrs=['bold'])} to see your user info
        ├ {colored("8.", "yellow", attrs=['bold'])} To display projects: {colored("project", "red", attrs=['bold'])} or {colored("proj", "red", attrs=['bold'])}
        ├ {colored("9.", "yellow", attrs=['bold'])} To display history: {colored("history", "red", attrs=['bold'])}
        ├ {colored("10.", "yellow", attrs=['bold'])} To see who hasn't been assigned to any task: {colored("who-to-fire", "red", attrs=['bold'])}                 
        └ {colored("11.", "yellow", attrs=['bold'])} To exit: {colored("exit", "red", attrs=['bold'])}                        
    """)

class messages:
    def __init__(self, message):
        self.message = message
    def alert(self, message):
        screenLock.acquire()
        print(colored(message, 'red'))
        screenLock.release()

def handle_input():
    global currentUser
    user_input = str
    print(colored(f'What do you want to do now, {currentUser[1]} ? ', 'red', attrs=['bold', 'blink']), end = colored('» ', 'yellow', attrs=['bold']))
    user_input =  input()
    if user_input == 'exit':
        print(colored('\n' + 'Thank you for using the app, see you again soon, byebye ! \n ლ(╥﹏╥ლ)', 'red', attrs=['bold', 'blink']), "\n")
        sys.exit()
    elif 'create' in user_input:
        create(user_input, currentUser)
    elif 'list' in user_input:
        list_task(user_input, currentUser)
    elif "add" in user_input:
        add_task(currentUser)
    elif 'mark' in user_input:
        mark_task(user_input, currentUser)
    elif 'remove' in user_input:
        remove_task(currentUser)
    elif 'edit' in user_input:
        edit_task(currentUser)
    elif 'user' in user_input:
        list_user(user_input, currentUser)
    elif 'project' in user_input or "proj" in user_input:
        list_projects(currentUser)
    elif 'history' in user_input:
        list_history(currentUser)
    elif 'who-to-fire' in user_input:
        who_to_fire()
    elif 'help' in user_input:
        print_menu()
        handle_input()
    else:
        print(colored("""Sorry, I don't understand that command, please input the right command or type 'help' for the list of commands, thanks! """, 'red', attrs=['bold', 'blink']))

if __name__ == '__main__':
    print(colored(header, 'yellow', attrs=['bold']))
    userLogin()
    try:
        while True:
            print_menu() if isMenuShowed == True else print('\n' + colored("""Enter 'help' for the list of commands""", 'yellow'))
            handle_input()
            isMenuShowed = False           

    except IndexError as Error:
        print(colored(f'''can't handle {Error}, sorry''', 'red', attrs=['bold']), '\n')
    # except Exception as Error:
    #     print(colored(f''''can't handle {Error}, sorry''', 'red', attrs=['bold']))
        