from __future__ import print_function
from tkinter import *
import schedule
import datetime
import threading
import time
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import scipy
from scipy import stats
import statistics as st
from combolist import ChecklistCombobox
import webbrowser

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import sqlite3
import shutil
import os
import io

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
file = ' '
FileIDnamelist = []
def auth():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    global service
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)", q="fullText contains '.db'").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            fileDict = {}
            fileDict[item['name']] = item['id']
            FileIDnamelist.append(fileDict)
            print(u'{0} ({1})'.format(item['name'], item['id']))

auth()

FileNamelist = []

for i in FileIDnamelist:
    for key in i:
        FileNamelist.append(key)

window = Tk()
window.title("Application")
window.geometry('550x350')
OPTIONS = ["Low","Medium","High"]

def backup():
    try:
        # Open sqlite3 db for checking
        conn = sqlite3.connect(pathVAR)

        cur = conn.cursor()

        conn.row_factory = sqlite3.Row

        conn.close()

        # backup part

        shutil.copy(pathVAR, 'bkup.db')

        # ----------------------date time thingy----------------------
        now = datetime.datetime.now()

        # format --> year-month-day_hour-min-sec
        global filename
        filename = '{}~{}-{}-{}_{}-{}.db'.format(pathVAR[:-3], now.year, now.month, now.day, now.hour, now.minute)
        # ------------------------------------------------------------

        file = 'bkup.db'

        file_id = uploadFile()
        print(file_id)

        # ------------------------------------------------------------
        os.remove(file)
        #decrypt()  #if db was decrypted
    except:
        print('No DB active!')
    



def uploadFile():
    mimetype = 'application/x-sqlite3'
    file_path = PATH.get()
    file_metadata = {'name': filename}
    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    return file_id


def dl_recover(file_id, fileName):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(fileName[fileName.find('~')+1:], 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))


def update():
    global pathVAR
    pathVAR = PATH.get()
    freqVAR = FREQ.get()
    timeVAR = TIME1.get()
    print(pathVAR, freqVAR, timeVAR)  #For debugging, can remove later

    try:
        for x in freqVAR:
            if x == 'Monday':
                schedule.every().monday.at(timeVAR).do(backup)
            if x == 'Tuesday':
                schedule.every().tuesday.at(timeVAR).do(backup)
            if x == 'Wednesday':
                schedule.every().wednesday.at(timeVAR).do(backup)
            if x == 'Thursday':
                schedule.every().thursday.at(timeVAR).do(backup)
            if x == 'Friday':
                schedule.every().friday.at(timeVAR).do(backup)
            if x == 'Saturday':
                schedule.every().saturday.at(timeVAR).do(backup)
            if x == 'Sunday':
                schedule.every().sunday.at(timeVAR).do(backup)
    except:
        print('invalid time format')

    backup_schedule()

def backup_schedule():
    schedule.run_pending()
    threading.Timer(30, backup_schedule).start()

def update_log():
    l = open("log/logCommits.txt", "r")
    for logs in l:
        LOG.configure(state='normal')
        LOG.insert(END, logs)
        LOG.configure(state='disabled')
        # Autoscroll to the bottom
        LOG.yview(END)
def callback(url):
    webbrowser.open_new(url)

def dwnldbackup():
    specbackVAR = specbackList.get()

    for i in FileIDnamelist:
        if specbackVAR in i:
            file_ID = i[specbackVAR]
            fileName = specbackVAR

    dl_recover(file_ID, fileName)

#=====================================================================================
#====================get key=========
def dlFile():
    file_id = '1uEJlqgapyxZCp8wphId8eeY7wAGu67b3'
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO('key.txt', 'w')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
def generateKey():
    dlFile()
    keyfile = open('key.txt',"rb")
    key = keyfile.readline()
    key = key.strip()
    keyfile.close()
    os.remove('key.txt')
    return key
global cryptokey
cryptokey = generateKey()
#cryptokey = bytes(cryptokey,"utf-8")

file = 'Hotel.db'
buffer_size = 65536
# === Encrypt ===
def encrypt():
    # Open the input and output files
    input_file = open(file, 'rb')
    output_file = open(file + '(encrypted)', 'wb')
    # Create the cipher object and encrypt the data
    cipher_encrypt = AES.new(cryptokey, AES.MODE_CFB)

    # Initially write the iv to the output file
    output_file.write(cipher_encrypt.iv)

    # Keep reading the file into the buffer, encrypting then writing to the new file
    buffer = input_file.read(buffer_size)
    while len(buffer) > 0:
        ciphered_bytes = cipher_encrypt.encrypt(buffer)
        output_file.write(ciphered_bytes)
        buffer = input_file.read(buffer_size)

    # Close the input and output files
    input_file.close()
    output_file.close()
    os.remove(file)
    os.rename(file + '(encrypted)',file)
    #======================count ====================
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count += 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()
    #====================update=================
    if count == 1:
        DNBTN.config(state=NORMAL)
        ENBTN.config(state=DISABLED)
    elif count != 0 and count != 1:
        print("count is",count)
    else:
        ENBTN.config(state=NORMAL)
        DNBTN.config(state=DISABLED)

# === Decrypt ===
def decrypt():
    # Open the input and output files
    input_file = open(file, 'rb')
    output_file = open(file + '(decrypted)', 'wb')
    # Read in the iv
    iv = input_file.read(16)

    # Create the cipher object and encrypt the data
    cipher_encrypt = AES.new(cryptokey, AES.MODE_CFB, iv=iv)

    # Keep reading the file into the buffer, decrypting then writing to the new file
    buffer = input_file.read(buffer_size)
    while len(buffer) > 0:
        decrypted_bytes = cipher_encrypt.decrypt(buffer)
        output_file.write(decrypted_bytes)
        buffer = input_file.read(buffer_size)

    # Close the input and output files
    input_file.close()
    output_file.close()
    os.remove(file)
    os.rename(file + '(decrypted)',file)
    #===========count=========
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count -= 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()
    #============update======
    if count == 0:
        ENBTN.config(state=NORMAL)
        DNBTN.config(state=DISABLED)
    elif count != 0 and count != 1:
        print("count is",count)
    else:
        DNBTN.config(state=NORMAL)
        ENBTN.config(state=DISABLED)
    #==========================
def encryptcheck():
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    print("encryptcheck count:",count)
    return count
#=======================================================================================

tab_parent = ttk.Notebook(window)
tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="Backup/Crypt")
tab_parent.add(tab2, text="Logs")
tab_parent.grid(column=0, row=0)

lbl = Label(tab1, text="Enter Database PATH")
lbl.grid(column=0,row=1)
PATH = Entry(tab1,width=20)
PATH.grid(column=1,row=1)

lbl2 = Label(tab1, text="Enter backup time (05:00) (24h)")
lbl2.grid(column=0,row=2)
TIME1 = Entry(tab1, width=20)
TIME1.grid(column=1,row=2)

lbl3 = Label(tab1, text="Enter backup days")
lbl3.grid(column=0,row=3)
FREQ = ChecklistCombobox(tab1, values=('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'))
FREQ.grid(column=1,row=3)

UpdateBTN = Button(tab1, text="Update", command=update)
UpdateBTN.grid(column=1, row=5)

DBKBTN = Button(tab1, text="Download Backup", command=dwnldbackup)
DBKBTN.grid(column=0, row=7)
lbl6 = Label(tab1, text="Select backup file")
specbackList = StringVar(tab1)
specbackList.set(FileNamelist[0])
specback = OptionMenu(tab1, specbackList, *FileNamelist)
specback.grid(column=0,row=6)

BKNBTN = Button(tab1, text="Backup Now", command=backup)
BKNBTN.grid( column=1, row=7)

if encryptcheck() == 1:
    ENBTN = Button(tab1, text="Encrypt Database", command=encrypt, state=DISABLED)
    ENBTN.grid(column=2, row=5)
else:
    ENBTN = Button(tab1, text="Encrypt Database", command=encrypt)
    ENBTN.grid(column=2, row=5)
if encryptcheck() == 0:
    DNBTN = Button(tab1, text="Decrypt Database", command=decrypt, state=DISABLED)
    DNBTN.grid(column=3, row=5)
else:
    DNBTN = Button(tab1, text="Decrypt Database", command=decrypt)
    DNBTN.grid(column=3, row=5)

lbl5 = Label(tab2, text="Log events:")
lbl5.grid(column=0,row=0)
LOG = ScrolledText(tab2,width=100,height=10,wrap=WORD)
LOG.grid(column=0,row=1,columnspan=4)
LOG.configure(state='disabled')

RE = Button(tab2, text="Refresh", command=update_log)
RE.grid(column=0, row=2)
splunk = Button(tab2, text="Go see splunk dashboard")
splunk.grid(column=1, row=2)
splunk.bind("<Button-1>", lambda e: callback("http://127.0.0.1:8000/en-US/app/search/ispj"))
##es = Button(tab2, text="Go see ElasticSearch dashboard")
##es.grid(column=2, row=2)
##es.bind("<Button-1>", lambda e: callback("http://127.0.0.1:8000/en-US/app/search/ispj"))

PATH.focus()
window.mainloop()

