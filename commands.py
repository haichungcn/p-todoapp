import sqlite3
import os
from datetime import datetime
from termcolor import colored
from tabulate import tabulate

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

conn = sqlite3.connect(DEFAULT_PATH)
cur = conn.cursor()
temp_user = []

def createUser(currentUser):
    sql_create_user = """
        INSERT INTO users (
            user_name,
            user_email,
            user_password,
            birthday,
            phone_number,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    sql_list = f"""
        SELECT *
            FROM users
            WHERE user_name = ?
        """

    while True:
        print(colored("> What's the username ? ", 'cyan', attrs=['bold', 'blink']), end = '» ')
        name = input() 
        cur.execute(sql_list, (name,))
        result = cur.fetchall()
        if not result:
            break
        else:
            print(colored("> This username is already taken, plz choose another one.", 'red', attrs=['bold', 'blink']))

    while True:
        print(colored("> What's the user's email ? ", 'cyan', attrs=['bold', 'blink']), end = '» ')
        email = input()
        sql_list = f"""
        SELECT *
            FROM users
            WHERE user_email = ?
        """
        cur.execute(sql_list, (email,))
        result = cur.fetchall()
        if not result:
            break
        else:
            print(colored("> This email is already taken, plz choose another one.", 'red', attrs=['bold', 'blink']))

    print(colored("> What's the password ? ", 'cyan', attrs=['bold', 'blink']), end = '» ')
    password = input()
    print(colored("> What's the user's birthday ? ", 'cyan', attrs=['bold', 'blink']), end = '» ')
    birthday = input()
    print(colored("> What's the user's phone number ? ", 'cyan', attrs=['bold', 'blink']), end = '» ')
    phone = input()
    time = datetime.now()
    
    cur.execute(sql_create_user,(name, email, password, birthday, phone, time,))
    conn.commit()

    # adding lastest action to history
    temp_user = getUser(name)
    if temp_user:
        if not currentUser: currentUser[0] = 1
        history_push(f"create user {name}", "users", temp_user[0], currentUser[0]) 
        print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" successfully created user: {name}", 'cyan'))
        return temp_user
    else:
        print("\n", colored("[X]", 'red', attrs=['bold']), colored(f" unsuccessfully created user: {name}", 'red'))


def create(user_input, currentUser):
    if "-p" in user_input:
        print(colored("> What's the name of the project ? ", 'cyan', attrs=['bold', 'blink']), end = '» ')
        proj_name = input()
        creator = currentUser[0]
        time = datetime.now()
        sql_create_proj = """
            INSERT INTO projects (
                project_name,
                status,
                creator_id,
                timestamp
            ) VALUES (?, "unfinished", ?, ?)
        """
        cur.execute(sql_create_proj,(proj_name, creator, time,))
        conn.commit()
        
        # adding lastest action to history
        cur.execute("""SELECT id FROM projects""")
        result = cur.fetchall()
        proj_id = result[0][0]
        history_push("crete new project", 'projects', proj_id, currentUser[0])
        
        print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" finished creating new project named: {proj_name}", 'cyan'))
    
    elif "-u" in user_input:
        createUser(currentUser)
    else:
        print('\n', colored("> You didn't enter any flag, please type 'create' followed by a tag ('-u' or '-p')", "cyan", attrs=['bold']))

def add_task(currentUser):
    sql_add = """
            INSERT INTO todos (
                body,
                due_date,
                project_id,
                creator_id,
                assigned_id,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        """

    print(colored('> What is your task ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
    body = input()

    print(colored('> What is its due date? (you can skip this) ', 'cyan', attrs=['bold', 'blink']), end = '» ')
    due_date = input()
    if due_date == '': due_date = datetime.now()

    print(colored('> What project is this belongs to? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
    project_id = input()

    print(colored('> What user is this assigned to? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
    user_id = input()
    if user_id =='': user_id = currentUser[0]

    timestamp = datetime.now()

    cur.execute(sql_add, (body, due_date, project_id, currentUser[0], user_id, timestamp ))
    conn.commit()

    # adding lastest action to history
    cur.execute("""SELECT id FROM todos WHERE body = ?""", (body,))
    result = cur.fetchall()
    taskId = result[0][0]
    history_push("added new task", "todos", taskId, currentUser[0])
    
    print("\n", colored("[√]", 'red', attrs=['bold']), colored(" finished adding task", 'cyan'))

def list_task(user_input, currentUser):
    # display all to-dos assigned to the current user:
    if '-a' in user_input:
        sql_list = """
            SELECT *
                FROM todos
                WHERE assigned_id = ?
                AND status != "removed"
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()

    # display all to-dos created by the current user:
    elif '-c' in user_input:
        sql_list = """
            SELECT *
                FROM todos
                WHERE creator_id = ?
                AND status != "removed"
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()

    # display all to-dos assigned to a user:
    elif '-user' in user_input:
        user_list = list_user("-a", currentUser)    
        while True:
            print(colored('> Which user do you want to see their assigned tasks ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
            assigned_user = int(input())
            if assigned_user in user_list:
                print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" got it, user#{assigned_user}", 'cyan'))
                break
            else:
                print('\n', colored("> You didn't enter any user id has been listed, plz try again.", "cyan", attrs=['bold']), '\n')
        sql_list = f"""
            SELECT todos.id, body, status, due_date, project_id, creator_id, user_name, todos.timestamp
                FROM todos
                LEFT JOIN users ON todos.assigned_id = users.id
                WHERE status != "removed"
                AND creator_id = ?
                AND assigned_id = {assigned_user}
                ORDER BY todos.id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()
    
    # display all undone to-dos assigned the current user:
    elif '-u' in user_input:
        sql_list = """
            SELECT *
                FROM todos
                WHERE status = "undone"
                AND assigned_id = ?
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()
    
    # display all done to-dos created by the current user:
    elif '-d' in user_input:
        sql_list = """
            SELECT *
                FROM todos
                WHERE status = "done"
                AND assigned_id = ?
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()

    # display all removed to-dos created by the current user:
    elif '-r' in user_input:
        sql_list = """
            SELECT *
                FROM todos
                WHERE status = "removed"
                AND creator_id = ?
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()
    
    # display all to-dos in a project:
    elif '-p' in user_input:
        print(colored('> Here are the projects that you currently envolved in: ', 'cyan', attrs=['bold', 'blink']), '\n')
        list_projects(currentUser)
        print(colored('> Which project id do you want to see ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
        project = input()
        sql_list = f"""
            SELECT *
                FROM todos
                WHERE status != "removed"
                AND creator_id = ?
                OR assigned_id = ?
                AND project_id = {project}
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],currentUser[0],))
        result = cur.fetchall()
    else:
        sql_list = """
            SELECT *
                FROM todos
                WHERE creator_id = ?
                AND status != "removed"
                ORDER BY id DESC
            """
        cur.execute(sql_list, (currentUser[0],))
        result = cur.fetchall()
    
    if result :
        print('\n', colored("your tasks:","cyan"))
        print(tabulate(result,headers=[
                colored('Id', 'yellow', attrs=['bold']),
                colored('Body', 'red', attrs=['bold']),
                colored('Status', 'cyan', attrs=['bold']),
                colored('Due Date', 'blue', attrs=['bold']),
                colored('Project Id', 'green', attrs=['bold']),
                colored('Creator Id', 'magenta', attrs=['bold']),
                colored('Assigned To', 'yellow', attrs=['bold']),
                colored('Timestamp', 'green', attrs=['bold'])
            ],
            tablefmt='psql')
        )
        # taking out all the id
        id_list = []
        for i in result: id_list.append(i[0])
        return(id_list)
    else:
        print('\n', colored("> You don't have any task yet, please start by creating one", "cyan", attrs=['bold']))

    print('\n', colored("[√]", 'red', attrs=['bold']), colored(" finished listing", 'cyan'))

def mark_task(user_input, currentUser):
    if "-u" in user_input or "-d" in user_input:
        taskId = get_task_name(currentUser)
        state = "undone"
        sql_mark = """
                UPDATE todos
                    SET status = ?
                    WHERE id = ?
                        AND assigned_id = ?
                """
        if "-u" in user_input:
            state = "undone"
        elif "-d" in user_input:
            state = "done"
        cur.execute(sql_mark, (state, taskId, currentUser[0],))
        conn.commit()

        # adding lastest action to history
        change_made = "mark " + state
        history_push(change_made, "todos", taskId, currentUser[0])
        print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" finished marking {state} to task: #{taskId}", 'cyan'))
    else:
        print(colored("""Sorry, plz enter 'mark' with flag '-u' or '-d', thanks! """, 'red', attrs=['bold', 'blink']))
        
def remove_task(currentUser):
    taskId = get_task_name(currentUser)
    sql_remove = """
            UPDATE todos
                SET status = "removed"
                WHERE id = ?
                    AND creator_id = ?
            """
    cur.execute(sql_remove, (taskId, currentUser[0],))
    conn.commit()
    
    # adding lastest action to history
    history_push("removed task", "todos", taskId, currentUser[0])
    print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" removed task: #{taskId}", 'cyan'))

def get_task_name(currentUser, flag = '-a'):
    while True:
        taskId = list_task(flag, currentUser)
        print(colored('> What is the id of the task ? ', 'red', attrs=['bold', 'blink']), end = '» ')
        task = int(input())
        if task in taskId:
            return task
            break

def edit_task(currentUser):
    taskId = get_task_name(currentUser, '-c')

    print(colored('\n' + """> Please enter the body of your task here:""", 'cyan', attrs=['bold', 'blink']), end = colored('» ', 'yellow', attrs=['bold']))
    content = input()

    print(colored('\n' + """> Please enter the due_date for your task here:""", 'cyan', attrs=['bold', 'blink']), end = colored('» ', 'yellow', attrs=['bold']))
    due_date = input()
    
    print(colored('\n' + """> Please enter the project id for your task here:""", 'cyan', attrs=['bold', 'blink']), end = colored('» ', 'yellow', attrs=['bold']))
    project_id = input()

    print(colored('\n' + """> Please enter the user id for your task here:""", 'cyan', attrs=['bold', 'blink']), end = colored('» ', 'yellow', attrs=['bold']))
    user_id = input()

    if content or due_date or project_id or user_id:
        if not user_id:
            cur.execute("""SELECT assigned_id FROM todos WHERE id = ?""", (taskId,))
            result = cur.fetchall()
            user_id = result[0][0]
        sql_edit = f"""
                UPDATE todos
                    SET {content and ("body = " + f"'{content}'" + ',')}
                        {due_date and ("due_date = " + f"'{due_date}'" + ',')}
                        {project_id and ("project_id = " + f"'{project_id}'" + ',')}
                        {user_id and ("assigned_id = " + f"'{user_id}'")}
                    WHERE id = {taskId}
                        AND creator_id = ?
                """
        cur.execute(sql_edit,(currentUser[0],))
        conn.commit()

        # adding lastest action to history
        history_push(f"edited task (due_date:{due_date}, project_id:{project_id}, assigned to :{user_id})", "todos", taskId, currentUser[0])
        print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" updated task: #{taskId}", 'cyan'))
    else:
        print("\n", colored(f"> Nothing is done to: #{taskId}", 'cyan'))

def list_user(user_input, currentUser):
    if "-i" in user_input or "-a" in user_input:
        if "-i" in user_input:
            sql_list = f"""
                SELECT *
                    FROM users
                    WHERE id = ?
                    ORDER BY id DESC
                """

            cur.execute(sql_list, (currentUser[0],))
            result = cur.fetchall()
            print('\n', colored("your user info:","cyan"))
            print(tabulate(result,headers=[
                    colored('Id', 'yellow', attrs=['bold']),
                    colored('User Name', 'red', attrs=['bold']),
                    colored('Email', 'blue', attrs=['bold']),
                    colored('Password', 'green', attrs=['bold']),
                    colored('Birthday', 'magenta', attrs=['bold']),
                    colored('Phone Number', 'cyan', attrs=['bold']),
                    colored('Timestamp', 'grey', attrs=['bold'])
                ],
                tablefmt='psql')
            )

        elif "-a" in user_input:
            sql_list = """
                SELECT id,
                    user_name,
                    user_email,
                    birthday,
                    phone_number,
                    timestamp
                FROM users
                """

            cur.execute(sql_list)
            result = cur.fetchall()
            print('\n', colored("all users listed below:","cyan"))
            print(tabulate(result,headers=[
                    colored('Id', 'yellow', attrs=['bold']),
                    colored('User Name', 'red', attrs=['bold']),
                    colored('Email', 'blue', attrs=['bold']),
                    colored('Birthday', 'magenta', attrs=['bold']),
                    colored('Phone Number', 'cyan', attrs=['bold']),
                    colored('Timestamp', 'green', attrs=['bold'])
                ],
                tablefmt='psql')
            )
        print('\n',colored("[√]", 'red', attrs=['bold']), colored(" finished listing", 'cyan'))
        # taking out all the id
        id_list = []
        for i in result: id_list.append(i[0])
        return id_list
    else:
        print('\n', colored("> You didn't enter any flag, please type 'user' followed by a tag ('-i' or '-a')", "cyan", attrs=['bold']))


def checkUser(userName):
    sql_list = """
        SELECT *
            FROM users
            WHERE user_name = ?
        """

    cur.execute(sql_list, (userName,))
    result = cur.fetchall()
    if result :
        temp_user = result[0]
        print('\n', colored("[√] username","cyan"))
        return True
    else:
        print('\n', colored("[X] username","red"))
        return False

def checkPassword(userName, userPassword):
    sql_list = """
        SELECT *
            FROM users
            WHERE user_name = ?
        """

    cur.execute(sql_list, (userName,))
    result = cur.fetchall()
    if result:
        temp_user = result[0]
        if temp_user[3] == userPassword :
            print('\n', colored("[√] password","cyan"), '\n')
            return True
        else:
            print('\n', colored("[X] password","red"))
            return False

def getUser(userName):
    sql_list = f"""
        SELECT *
            FROM users
            WHERE user_name = ?
        """

    cur.execute(sql_list, (userName,))
    result = cur.fetchall()
    if result[0]:
        temp_user = result[0]
        print(temp_user[:2])
        return temp_user[:2]

def history_push(change_made,table_name,row_id,owner_id):
    sql_history_push = """
            INSERT INTO history (
                action,
                table_name,
                row_id,
                owner_id,
                timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """
    time = datetime.now()
    cur.execute(sql_history_push, (change_made, table_name, row_id, owner_id, time,))
    conn.commit()

def list_history(currentUser):
    sql_list_history = """
        SELECT * from history
            WHERE owner_id = ?
    """
    cur.execute(sql_list_history, (currentUser[0],))
    result = cur.fetchall()
    print('\n', colored("Your history:","cyan"))
    print(tabulate(result,headers=[
            colored('Id', 'yellow', attrs=['bold']),
            colored('Action', 'red', attrs=['bold']),
            colored('Applied to', 'blue', attrs=['bold']),
            colored('Row Id', 'green', attrs=['bold']),
            colored('Owner Id', 'magenta', attrs=['bold']),
            colored('Timestamp', 'cyan', attrs=['bold'])
        ],
        tablefmt='psql')
    )
    print('\n',colored("[√]", 'red', attrs=['bold']), colored(" finished listing", 'cyan'))

def list_projects(currentUser, flag = '-c'):
    if '-u' in flag:
        sql_list_proj = """
        SELECT projects.id,
            project_name,
            status,
            creator_id,
            user_name
            FROM projects
            LEFT JOIN project_users
                ON project_users.project_id = projects.id
            LEFT JOIN users
                ON project_users.assigned_id = users.id
            WHERE project_users.user_id = ?
                OR projects.creator_id = ?
        """
        cur.execute(sql_list_proj, (currentUser[0],currentUser[0],))
        result = cur.fetchall()
        print('\n', colored("These are projects that either assigned to you or created by you:","cyan"))
        print(tabulate(result,headers=[
                colored('Id', 'yellow', attrs=['bold']),
                colored('Project Name', 'red', attrs=['bold']),
                colored('Status', 'blue', attrs=['bold']),
                colored('Creator Id', 'green', attrs=['bold']),
                colored('Assigned To', 'cyan', attrs=['bold'])
            ],
            tablefmt='psql')
        )
    elif "-a" in flag:
        sql_list_proj = """
        SELECT projects.id,
            project_name,
            status,
            creator_id,
            user_id
            FROM projects
            LEFT JOIN project_users
                ON project_users.project_id = projects.id
            WHERE project_users.user_id = ?
        """
        cur.execute(sql_list_proj, (currentUser[0],))
        result = cur.fetchall()
        print('\n', colored("These projects are assigned to you:","cyan"))
        print(tabulate(result,headers=[
                colored('Id', 'yellow', attrs=['bold']),
                colored('Project Name', 'red', attrs=['bold']),
                colored('Status', 'blue', attrs=['bold']),
                colored('Creator Id', 'green', attrs=['bold']),
                colored('Assigned To', 'cyan', attrs=['bold'])
            ],
            tablefmt='psql')
        )
    elif "-c" in flag:
        sql_list_proj = """
            SELECT * FROM projects
                WHERE creator_id = ?
        """
        cur.execute(sql_list_proj, (currentUser[0],))
        result = cur.fetchall()
        print('\n', colored("Your created projects:","cyan"))
        print(tabulate(result,headers=[
                colored('Id', 'yellow', attrs=['bold']),
                colored('Project Name', 'red', attrs=['bold']),
                colored('Status', 'blue', attrs=['bold']),
                colored('Creator Id', 'green', attrs=['bold']),
                colored('Timestamp', 'cyan', attrs=['bold'])
            ],
            tablefmt='psql')
        )
    # taking out all the id
    id_list = []
    for i in result: id_list.append(i[0])
    print('\n',colored("[√]", 'red', attrs=['bold']), colored(" finished listing", 'cyan'))
    return(id_list)

def assign_projects(currentUser):
    sql_assign = """
        INSERT INTO project_users (
            project_id,
            user_id
        ) VALUES (?, ?)
    """
    proj_list = list_projects(currentUser, "-c")
    while True:
        print(colored('> Which project do you want to assign ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
        proj = int(input())
        if proj in proj_list:
            print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" got it, project#{proj}", 'cyan'))
            break
        else:
            print('\n', colored("> You didn't enter any project id has been listed, plz try again.", "cyan", attrs=['bold']), '\n')

    user_list = list_user("-a", currentUser)    
    while True:
        print(colored('> Which user do you want to assign to ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
        user = int(input())
        if user in user_list:
            print("\n", colored("[√]", 'red', attrs=['bold']), colored(f" got it, user#{user}", 'cyan'))
            break
        else:
            print('\n', colored("> You didn't enter any user id has been listed, plz try again.", "cyan", attrs=['bold']), '\n')

    if proj and user:
        cur.execute(sql_assign, (str(proj), str(user),))
        conn.commit()
        print('\n',colored("[√]", 'red', attrs=['bold']), colored(f" successfully assigned project #{proj} to user #{user}", 'cyan'))
        
        # adding lastest action to history
        history_push(f"assigned project#{proj} to user#{user}", "project_users", proj, currentUser[0])

def mark_projects(currentUser):
    sql_mark= """
        UPDATE projects
            SET status = ?
        WHERE creator_id = ?
        AND id = ?
    """
    proj_list = list_projects(currentUser, "-c")

    while True:
        print(colored('> Which project do you want to change status ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
        proj = int(input())
        if proj in proj_list:
            break
        else:
            print(colored("""> You've entered a non-exist project number, plz try again """, 'cyan', attrs=['bold', 'blink']), '\n')
    
    status_list = [1,2]
    while True:
        print(colored('> Enter "1" if you want to mark the project "finished" or "2" otherwise ? ', 'cyan', attrs=['bold', 'blink']), end = '» ')
        user_input = int(input())
        if user_input in status_list:
            if user_input == 1:
                status = "finished"
            else:
                status = "unfinished"
            break
        else:
            print(colored("""> You've entered a wrong command, plz try again """, 'cyan', attrs=['bold', 'blink']), '\n')

    cur.execute(sql_mark, (status, currentUser[0], proj, ))
    conn.commit()
    print('\n',colored("[√]", 'red', attrs=['bold']), colored(f" successfully marked project #{proj} as {status}", 'cyan'))
    history_push(f"marked project#{proj} as {status}", "projects", proj, currentUser[0])


def who_to_fire():
    sql_list = """
        SELECT users.id,
            user_name,
            user_email,
            birthday,
            phone_number,
            users.timestamp
        FROM users
            LEFT JOIN todos ON todos.assigned_id = users.id
        WHERE body IS NULL
    """
    cur.execute(sql_list)
    result = cur.fetchall()
    if result:
        print('Ok, I found somebody to fire:', result)
        print(tabulate(result,headers=[
                colored('Id', 'yellow', attrs=['bold']),
                colored('Name', 'red', attrs=['bold']),
                colored('Email', 'blue', attrs=['bold']),
                colored('Birthday', 'green', attrs=['bold']),
                colored('Phone', 'cyan', attrs=['bold']),
                colored('Created on', 'magenta', attrs=['bold'])
            ],
            tablefmt='psql')
        )
        print('\n',colored("[√]", 'red', attrs=['bold']), colored(" finished listing", 'cyan'))
    else:
        print('\n', colored("> Sadly, there is no one to fire today...", "cyan", attrs=['bold']))
