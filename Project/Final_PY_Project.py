import PySimpleGUI as sg
import sqlite3
from email.message import EmailMessage
from smtplib import SMTP
con1 = sqlite3.connect('EVENT.db')
con2 = sqlite3.connect('TICKETS.db')
cur1 = con1.cursor()
cur2 = con2.cursor()
cur1.execute('''CREATE TABLE IF NOT EXISTS EVENTS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT,
    DATE TEXT,
    HOUR TEXT,
    DESCRIPTION TEXT)''')


# starting from 3405
cur1.execute('UPDATE SQLITE_SEQUENCE SET seq = 3404 WHERE name = "EVENTS"')
cur1.execute('DELETE FROM SQLITE_SEQUENCE WHERE name = "EVENTS"')
cur1.execute('INSERT INTO SQLITE_SEQUENCE (name, seq) VALUES ("EVENTS", 3404)')



cur2.execute('''CREATE TABLE IF NOT EXISTS TICKETS (
    id)''')


def email_verifier(email:str):
    numbers = "0123456789"
    symbols = "~!@#$%^&*()_+=-><|\\/.?"
    sym_num = numbers + symbols
    if email.count('@') == 1:
        email_li = email.split('@')
        if '.' in email_li[1]:
            email_li_2 = email_li[1].split('.')
            if (email_li_2[0] != 'gmail' and email_li_2[0] !='yahoo') or email_li_2[1] != 'com':
                return False
            elif email_li[0][0] in sym_num:
                return False  
            else:
                return True
        else:
            return False
    else:
        return False



def time_verifier(time:str):
    time_li = time.split(':')
    try:
        if int(time_li[0]) > 24 or int(time_li[1]) > 59:
            return True
        return False
    except Exception:
        return True


def date_verifier(date:str):
    date_li = date.split('/')
    try:
        if int(date_li[0]) < 2024 or int(date_li[1]) > 12 or int(date_li[2]) > 31:
            return True
        return False
    except Exception:
        return True


def sql_handler(data):
    cur1.execute('INSERT INTO EVENTS (NAME, DATE, HOUR, DESCRIPTION) VALUES(?,?,?,?)', data)
    con1.commit()

    # Send email to the manager rightly after the ticket is being ordered
    cur1.execute("SELECT * FROM EVENTS WHERE ID = last_insert_rowid()")
    event_data = cur1.fetchone()
    send_ticket_details(event_data)

def message_creator(message : tuple):
    the_text = f'''     
                        On {message[2]} at {message[3]}, you have a ticket to {message[1]}  
                        Don't forget!!! '''
    return the_text

def message_creator2(message : tuple):
    the_text = f'''     
            On {message[2]} at {message[3]}, a ticket has been ordered for {message[1]}  '''
    return the_text    



# SMTP (Simple Mail Transfer Protocol) server of Gmail
# 587 --> is used for secure email transmission 
def email_sender(email, message):
    with SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('hsenareh@gmail.com', 'hrfp obtv rnxy uipo')
        the_text = EmailMessage()
        the_text['From'] = 'hsenareh@gmail.com'
        the_text['To'] = email
        the_text['Subject'] ='-Your Ticket-'
        the_text.set_content(message)
        smtp.send_message(the_text)


def add_event():
    layout = [
                [sg.Text('Enter the name of the event:'), sg.Input(expand_x = True, key = '-NAME-')],
                [sg.Text('Enter the date of the event:(seprate with /)'), sg.Input(expand_x=True, key='-DATE-')],
                [sg.Text('Enter the time of the event:(seprate with :)'), sg.Input(expand_x=True, key='-TIME-')],
                [sg.Text('Enter the necessary description:'), sg.Input(expand_x=True, key='-DESCRIPTION-')],
                [sg.Button('OK'), sg.Button('Cancel')]
            ]
    window2 = sg.Window('Add your event:', layout,
                            location=(400, 200),
                            background_color='yellow',
                            font='italic'
                            )

    while True:
        event, values = window2.read()
        if event == 'OK':
            data = (values['-NAME-'], values['-DATE-'], values['-TIME-'], values['-DESCRIPTION-'])
            if date_verifier(data[1]):
                sg.popup_error('Enter the date correctly!')
            else:
                if time_verifier(data[2]):
                    sg.popup_error('Enter the time correctly!')
                else:
                    sql_handler(data)
                    window2.close()  

        elif event == 'Cancel' or event == sg.WIN_CLOSED:
            window2.close()
            break

    return  # Return to the main loop --> main_window



def show_all():
    cur1.execute('SELECT * FROM EVENTS')
    li = cur1.fetchall() #a list of tuples
    text = ''
    if len(li) == 0:
        text += 'Nothing has been found!'
    else:
        for i in li:
            text += f"'ID: {i[0]}' ---  'Name: {i[1]}' ---  'Date: {i[2]}' ---  'Hour: {i[3]}' ---  'Description: {i[4]}'\n\n"
    layout1 = [[sg.Text(text, expand_y = True, expand_x = True, pad = (10, 20))]]
    while True:
        window3 = sg.Window('All events', layout1,
                            font='italic',
                            location=(40, 40)
                            )
        r, v = window3.read()
        if r == 'Ok' or r == sg.WIN_CLOSED:
            break


def event_choose(id):
    cur1.execute('SELECT * FROM EVENTS WHERE ID = ?',(id,))
    cur2.execute('SELECT * FROM TICKET WHERE id = ?',(id,))
    li = cur1.fetchone()
    li1 = cur2.fetchone()
    if li1 != None:
        sg.popup_error('Event has already been chosen!')
    else:
        cur2.execute('INSERT INTO TICKET (id) VALUES(?)',(id,))
        return li


def choose(email, id):
    choose = event_choose(id)
    if choose != None:
        message = message_creator(choose)
        if email_verifier(email):
            email_sender(email, message)
        else:
            sg.popup_error('Enter your email correctly!')


def search(date):
    cur1.execute('SELECT * FROM EVENTS WHERE DATE = ?', (date,))
    found_list = cur1.fetchall()
    text = ''
    if len(found_list) == 0:
        text += 'Nothing has been found!'
    else:
        for i in found_list:
            text += f"ID: {i[0]}, Name: {i[1]}, Date: {i[2]}, Hour: {i[3]}, Description: {i[4]}\n"
    return text



def win1():
    layout = [
                [sg.Text('Enter the date:')],
                [sg.Input(key = 'input')],
                [sg.Text(key = 'output')],
                [sg.Button('Ok')],
                [sg.Button('Choose')]
            ]
    return sg.Window('Search the events', layout, finalize = True,
                    location = (100,100),
                    background_color ='yellow',
                    font = 'italic'
                    )


def win2():
    layout = [
                [sg.Text('Enter the id:')],
                [sg.Input(key='in2')],
                [sg.Text('Enter your email:')],
                [sg.Input(key='in3')],
                [sg.Button('Ok')]
            ]
    return sg.Window('Choose the ticket', layout, finalize = True,
                    location = (100,400),
                    background_color ='yellow',
                    font = 'italic',
                    size = (400, 200)
                    )

def delete_event():
    cur1.execute('SELECT ID, NAME FROM EVENTS')
    events = cur1.fetchall()

    if not events:
        sg.popup_error("No events found to delete.")
        return  # Exit and back to the main loop

    event_names = [f"{i[0]}: {i[1]}" for i in events]
    layout = [
        [sg.Text("Select event to delete:")],
        [sg.Listbox(values = event_names, size = (40, 10), key = '-EVENT-LIST-')],
        [sg.Button('Delete'), sg.Button('Cancel')]
    ]
    window = sg.Window('Delete Event', layout)

    while True:
        event, values = window.read() #event --> str / values --> dict
        if event == 'Delete':
            selected_event = values['-EVENT-LIST-']
            if selected_event:
                event_id = int(selected_event[0].split(":")[0]) #id
                cur1.execute('DELETE FROM EVENTS WHERE ID = ?', (event_id,))
                con1.commit()
                sg.popup("Event deleted successfully!")
                window.close()
                break
            else:
                sg.popup_error("Please select an event to delete.")
        elif event == 'Cancel' or event == sg.WIN_CLOSED:
            window.close()
            break

    return 


def send_ticket_details(event_data):
    email = "hsenareh@gmail.com"
    message = message_creator2(event_data)
    email_sender(email, message)

#-------------------------------------------------------------


layout = [
            [sg.Button('Add an event')],
            [sg.Button('Show all the events')],
            [sg.Button('Search the events')],
            [sg.Button("Delete Event")],
            [sg.Button('Exit')]    
        ]

main_window = sg.Window('*Welcome here*', layout, background_color = 'yellow', font = 'italic', size = (400, 200))

while True:
    event, values = main_window.read()
    if event == 'Exit' or event == sg.WIN_CLOSED:
        break
    elif event == 'Add an event':
        add_event()
    elif event == 'Show all the events':
        show_all()
    elif event == "Delete Event":
        delete_event() 
    elif event == 'Search the events':
        window2 = win1()
        window3_open = False
        while True:
            event1, values = window2.read()
            if event1 == 'Ok':
                text = search(values['input'])
                if date_verifier(values['input']):
                    sg.popup_error('Enter the date correctly!')
                else:
                    window2['output'].update(text)
            elif event1 == 'Choose':
                if not window3_open:
                    window3 = win2()
                    window3_open = True
                    win3_event, win3_values = window3.read()
                    if win3_event == 'Ok':
                        choose(win3_values['in3'], win3_values['in2'])
                    window3.close()
                    window3_open = False
            elif event1 == sg.WIN_CLOSED:
                if window3_open:
                    window3.close()
                break

        window2.close() 

main_window.close()