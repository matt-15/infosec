from Crypto.Cipher import AES
import os
import io

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
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

def decrypt(file):
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
    #=========count============
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count -= 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()
def encrypt(file):
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
    os.rename(file + '(encrypted)', file)
    # =========count============
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count += 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()

#https://nitratine.net/blog/post/python-encryption-and-decryption-with-pycryptodome/#file-example-proof
#https://developers.google.com/drive/api/v3/manage-downloads#python
#    #replace replacement\/
#     X = string
#     Y = number of repetitions
#     replace(substr(quote(zeroblob((Y + 1) / 2)), 3, Y), '0', X)
#     select all the fields by name(not *) to change 1 or 2
#     substr(column, - x, x) to get last x chars
#    c.execute("SELECT u_id, replace(substr(quote(zeroblob((length(u_email) - 11) / 2)), 3, length(u_email)-12), '0', 'X') || substr(u_email, - 12, 12), u_username, u_password, 'XXXX XXXX XXXX ' || substr(u_credit_card, - 4, 4) FROM user;") #proof of concept
#    cryptokey = b'W\xdf\xfb\x1dn\xc0\xd3\xe1\xce/\x08P\xe6P\rS\xe7\x07\xa6\xebyHwN,P\x0c\x08\x88\xd8\x9e\xda'
#keyfile = open('key.txt','wb')
#keyfile.write(b'W\xdf\xfb\x1dn\xc0\xd3\xe1\xce/\x08P\xe6P\rS\xe7\x07\xa6\xebyHwN,P\x0c\x08\x88\xd8\x9e\xda')
#keyfile.close()
