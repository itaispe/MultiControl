import tkinter as tk
from functools import partial
from Admin_client import start_pressed,end_pressed,call_last_pressed
FINISHED_LOGIN = False
ERROR_LABEL = None
OLD_USER = True

CONT_PRESS = False

def wait_for_start(root,sock):
    """showing the screen containing the end button"""
    head = tk.Label(text="press the button to start controlling")
    head.config(font=("Courier", 44), bg='#856ff8')
    head.place(relx=0.5, rely=0.05, anchor='center')
    start_var = tk.StringVar()
    start_var.set('False')
    start_press_func = partial(start_pressed, start_var)
    start_but = tk.Button(root, text='start', command=start_press_func)
    start_but.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    start_but.place(relx=0.5, rely=0.3)

    call_last_func = partial(call_last_pressed,sock)
    call_but = tk.Button(root,text='call last users',command=call_last_func)
    call_but.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    call_but.place(relx=0.5,rely=0.5)

    num_cli_var = tk.StringVar()
    num_cli_var.set('Number of connected clients: 0')
    num_cli_label = tk.Label(textvariable=num_cli_var)
    num_cli_label.config(font=("Courier", 44), bg='#856ff8')
    num_cli_label.place(relx=0.5, rely=0.7, anchor='center')

    return num_cli_var, start_var


def wait_for_end(root):
    """showing the screen containing the end button"""
    clean_screen(root)

    head = tk.Label(text="press the button to stop controlling")
    head.config(font=("Courier", 44), bg='#856ff8')
    head.place(relx=0.5, rely=0.05, anchor='center')
    end_var = tk.StringVar()
    end_var.set('False')
    end_press_func = partial(end_pressed, end_var)
    end_but = tk.Button(root, text='end', command=end_press_func)
    end_but.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    end_but.place(relx=0.5, rely=0.5)

    return end_var

def error_cont():
    """called when admin pressed continue on the error screen"""
    global CONT_PRESS
    CONT_PRESS = True

def clean_screen(window):
    """cleaning the screen that is now being showed"""
    _list = window.winfo_children()
    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())
    for item in _list:
        item.destroy()


def submit_sign_up(username ,password, confirm):
    """called when sign in submit is pressed"""
    global FINISHED_LOGIN
    global ERROR_LABEL
    if ERROR_LABEL:
        ERROR_LABEL.destroy()
        ERROR_LABEL = None
    user_lower = username.get().lower()
    pass_lower = password.get().lower()
    if pass_lower.islower() and user_lower.islower():
        if password.get() == confirm.get():
            FINISHED_LOGIN = True
        else:
            error_label = tk.Label(text='passwords do not match')
            error_label.config(font=("Courier", 22), bg='#856ff8')
            error_label.place(relx=0.3, rely=0.8)
            ERROR_LABEL = error_label
    else:
        error_label = tk.Label(text='password and username must contain letters')
        error_label.config(font=("Courier", 22), bg='#856ff8')
        error_label.place(relx=0.3, rely=0.8)
        ERROR_LABEL = error_label


def submit(username, password, root):
    """called when submit button is pressed"""
    global FINISHED_LOGIN
    global ERROR_LABEL
    if ERROR_LABEL:
        ERROR_LABEL.destroy()
        ERROR_LABEL = None
    print("The name is : " + username.get())
    print("The password is : " + password.get())
    user_lower = username.get().lower()
    pass_lower = password.get().lower()
    if pass_lower.islower() and user_lower.islower():
        FINISHED_LOGIN = True
    else:
        error_label = tk.Label(text='password and username must contain letters')
        error_label.config(font=("Courier", 22), bg='#856ff8')
        error_label.place(relx=0.3, rely=0.9)
        ERROR_LABEL = error_label


def sign_in(root, name_var, pass_var):
    """showing the sign in screen"""
    global OLD_USER
    OLD_USER = False
    clean_screen(root)

    head = tk.Label(text="Welcome to multi-Control !!!")
    head.config(font=("Courier", 44), bg='#856ff8')
    head.place(relx=0.5, rely=0.05, anchor='center')

    msg = tk.Label(text=" create new user and start using multi-control!")
    msg.config(font=("Courier", 22), bg='#856ff8')
    msg.place(relx=0, rely=0.2, anchor='sw')

    log_label = tk.Label(text='Sign Up')
    log_label.config(font=("Courier", 30), bg='#856ff8')
    log_label.place(relx=0.5, rely=0.3, anchor='center')

    name_label = tk.Label(text='username')
    name_label.config(font=("Courier", 30), bg='#856ff8')
    name_label.place(relx=0.4, rely=0.4, anchor='center')

    password_label = tk.Label(text='password')
    password_label.config(font=("Courier", 30), bg='#856ff8')
    password_label.place(relx=0.4, rely=0.5, anchor='center')

    confirm_label = tk.Label(text='confirm password')
    confirm_label.config(font=("Courier", 30), bg='#856ff8')
    confirm_label.place(relx=0.46, rely=0.6, anchor='center')

    name_entry = tk.Entry(root, textvariable=name_var, font=("Courier", 30))
    name_entry.place(relx=0.5, rely=0.37)

    passw_entry = tk.Entry(root, textvariable=pass_var, font=("Courier", 30), show='*')
    passw_entry.place(relx=0.5, rely=0.47)

    confirm_var = tk.StringVar()

    confirm_entry = tk.Entry(root, textvariable=confirm_var, font=("Courier", 30), show='*')
    confirm_entry.place(relx=0.6, rely=0.57)

    sign_up_act = partial(submit_sign_up, name_var, pass_var, confirm_var)

    sign_submit = tk.Button(root, text='Sign Up', command=sign_up_act)
    sign_submit.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    sign_submit.place(relx=0.5, rely=0.7)


def login_screen(root):
    """showing the login page and returning the details of the admin"""
    global FINISHED_LOGIN
    global OLD_USER
    global ERROR_LABEL
    OLD_USER = True
    root.configure(bg='#856ff8')

    head = tk.Label(text="Welcome to multi-Control !!!")
    head.config(font=("Courier", 44), bg='#856ff8')
    head.place(relx=0.5, rely=0.05, anchor='center')

    msg = tk.Label(text=" Please Login to start using multi-control")
    msg.config(font=("Courier", 22), bg='#856ff8')
    msg.place(relx=0, rely=0.2, anchor='sw')

    log_label = tk.Label(text='Log In')
    log_label.config(font=("Courier", 30), bg='#856ff8')
    log_label.place(relx=0.5, rely=0.3, anchor='center')

    name_label = tk.Label(text='username')
    name_label.config(font=("Courier", 30), bg='#856ff8')
    name_label.place(relx=0.4, rely=0.4, anchor='center')

    password_label = tk.Label(text='password')
    password_label.config(font=("Courier", 30), bg='#856ff8')
    password_label.place(relx=0.4, rely=0.5, anchor='center')

    name_var = tk.StringVar()
    pass_var = tk.StringVar()

    name_entry = tk.Entry(root, textvariable=name_var, font=("Courier", 30))
    name_entry.place(relx=0.5, rely=0.37)

    passw_entry = tk.Entry(root, textvariable=pass_var, font=("Courier", 30), show='*')
    passw_entry.place(relx=0.5, rely=0.47)

    submit_action = partial(submit, name_var, pass_var, root)

    login_but = tk.Button(root, text='login', command=submit_action)
    login_but.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    login_but.place(relx=0.5, rely=0.6)

    create_msg = tk.Label(text="don't have an account?  click ")
    create_msg.config(font=("Courier", 25), bg='#856ff8')
    create_msg.place(relx=0.1, rely=0.8, anchor='w')

    sign_in_act = partial(sign_in, root, name_var, pass_var)

    sign_in_but = tk.Button(root, text='here', command=sign_in_act)
    sign_in_but.config(height=1, width=5, bg='#856ff8', font=("Courier", 25), anchor='center')
    sign_in_but.place(relx=0.49, rely=0.76)

    cont_create = tk.Label(text='to create one.')
    cont_create.config(font=("Courier", 25), bg='#856ff8')
    cont_create.place(relx=0.57, rely=0.8, anchor='w')

    root.update()
    while not FINISHED_LOGIN:
        try:
            root.update()
        except tk.TclError:
            break

    FINISHED_LOGIN = False
    ERROR_LABEL = None

    return name_var.get(), pass_var.get(), OLD_USER


def login_error(root, is_old):
    """showing the error screen"""
    global CONT_PRESS
    if is_old:
        var = 'username or password are wrong'
    else:
        var = 'username unavailable'
    lab = tk.Label(root,text=var)
    lab.config(font=("Courier", 44), bg='#856ff8')
    lab.pack()

    cont_but = tk.Button(root, text='continue', command=error_cont)
    cont_but.config(height=1, width=20, bg='#856ff8', font=("Courier", 30), anchor='center')
    cont_but.pack()
    while not CONT_PRESS:
        root.update()
    clean_screen(root)
    CONT_PRESS = False



