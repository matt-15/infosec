from flask import Flask, render_template, request
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from log import log
import logging
import atexit
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes




global cryptokey
cryptokey = b'W\xdf\xfb\x1dn\xc0\xd3\xe1\xce/\x08P\xe6P\rS\xe7\x07\xa6\xebyHwN,P\x0c\x08\x88\xd8\x9e\xda'
file = 'Hotel(new).db'
buffer_size = 65536

#============decrypt here=============
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
#=========================================

logonly = logging.getLogger('werkzeug')
logonly.setLevel(logging.ERROR)
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///Hotel(new).db'
db = SQLAlchemy(app)

##For email unique=True
class User(db.Model):
    u_id = db.Column(db.Integer, primary_key=True)
    u_email = db.Column(db.Text(50))
    u_username = db.Column(db.Text(35))
    u_password = db.Column(db.Text(200)) #200 is for encryption
    u_credit_card = db.Column(db.Text(16))
class Guest(db.Model):
    g_id = db.Column(db.Integer, primary_key=True)
    g_name = db.Column(db.Text(25))
    g_gender = db.Column(db.Text(6))
    g_countryname = db.Column(db.Text(10))
    g_roomReserved = db.Column(db.Text(9))
    g_checkstatus = db.Column(db.Text(10))
    g_deposit = db.Column(db.Integer)
    room = db.relationship('Room')
class Room(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    r_checkstatus = db.Column(db.Text(25))
    r_cleanstatus = db.Column(db.Text(1))
    r_price = db.Column(db.Integer)
    r_bedtype = db.Column(db.Text(25))
    r_roomNumber = db.Column(db.Integer)
    r_guestid = db.Column(db.Integer, db.ForeignKey('guest.g_id'))
    check = db.relationship('CheckStatus')
class CheckStatus(db.Model):
    c_guestid = db.Column(db.Integer, primary_key=True)
    c_roomid = db.Column(db.Float(9), db.ForeignKey('room.r_id'))
    c_CheckStatus = db.Column(db.Text(10))
    c_date = db.Column(db.DateTime(50))
    c_paymentstatus = db.Column(db.Text(1))
class Department(db.Model):
    d_id = db.Column(db.Integer, primary_key=True)
    d_name = db.Column(db.Text(25))
    d_managerid = db.Column(db.Integer, db.ForeignKey('manager.m_id'))
    d_budget = db.Column(db.Float)
class Driver(db.Model):
    dr_id = db.Column(db.Integer, primary_key=True)
    dr_age = db.Column(db.Integer)
    dr_name = db.Column(db.Text(25))
    dr_gender = db.Column(db.Text(1))
    dr_style = db.Column(db.Text(25))
    pickupcar = db.relationship('PickUpCar')
class Employee(db.Model):
    e_employeeid = db.Column(db.Integer, primary_key=True)
    e_departmentid = db.Column(db.Integer, db.ForeignKey('department.d_id'))
    e_salary = db.Column(db.Integer)
    e_job = db.Column(db.Text(25))
    e_name = db.Column(db.Text(25))
    e_department = db.Column(db.Text(25))
    driver = db.relationship('Driver')
class Manager(db.Model):
    m_id = db.Column(db.Integer, primary_key=True)
    m_name = db.Column(db.Text(25))
    m_salary = db.Column(db.Integer)
    m_age = db.Column(db.Integer)
    m_gender = db.Column(db.Text(10))
    m_department = db.Column(db.Text(9))
    password = db.Column(db.Text(200))
    department = db.relationship('Department')
class PickUpCar(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    p_year = db.Column(db.Text(4))
    p_brand = db.Column(db.Text(25))
    p_driverid = db.Column(db.Integer, db.ForeignKey('driver.dr_id'))
    p_availability = db.Column(db.Text(10))
    p_airport = db.Column(db.Text(25))


db.create_all()
conn = sqlite3.connect('Hotel(new).db')
c = conn.cursor()

def OnExitApp():  #encrypt here
    #Open the input and output files
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
    conn.close()
    os.remove(file)
    os.rename(file + '(encrypted)',file)
    #=========count============
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count += 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()
    #==========================
atexit.register(OnExitApp)

@app.route('/')#tosee the db on python side
def index():
    c.execute('SELECT * FROM User')
    for row in c.fetchall():
        print(row)
    return render_template('index.html')


@app.route('/sendnudes')
def insert(mail, uname, pword, cc):
    insert = '''
INSERT INTO user (u_email, u_username, u_password, u_credit_card)
VALUES
( ?, ?, ?, ?)
'''
    value=[(mail, uname, pword, cc)]
    c.executemany(insert,value)
    log.dbInsert("User.db","User",mail, uname, pword, cc)
    conn.commit()
    log.dbCommit("User.db","User")
    try:
        return render_template('query.html')
    except AttributeError as e:
        print("The Error: [ "+str(e)+" ] has occured")
    except Exception:
        print("Idk smt went wrong")

@app.route('/select', methods=['GET','POST']) #employee select so no masking
def select():
    #replace replacement\/
    #-- X = string
    #-- Y = number of repetitions
    #replace(substr(quote(zeroblob((Y + 1) / 2)), 3, Y), '0', X)
    #select all the fields by name(not *) to change 1 or 2
    #substr(column, - x, x) to get last x chars
    c.execute("SELECT u_id, replace(substr(quote(zeroblob((length(u_email) - 11) / 2)), 3, length(u_email)-12), '0', 'X') || substr(u_email, - 12, 12), u_username, u_password, 'XXXX XXXX XXXX ' || substr(u_credit_card, - 4, 4) FROM user;") #proof of concept
    log.dbSelect("User.db","User")
    for row in c.fetchall():
        print(row)
    try:
        return render_template('search.html')
    except AttributeError as e:
        print("The Error: [ "+str(e)+" ] has occured")
    except Exception:
        print("Idk smt went wrong")
insert("emailee@email.com","userman","password123","1234567890123456")
select()



##if __name__ == '__main__':
##    app.config['SESSION_TYPE'] = 'filesystem'
##    app.run(host="127.0.0.1", port=int("5000"), debug=False, use_reloader=False)
