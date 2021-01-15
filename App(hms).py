from flask import Flask, render_template, request, redirect, url_for, escape, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from Forms import RegisterUserForm, CreateProjectForm, SearchForm, CreateComment
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import re
from passlib.hash import pbkdf2_sha256
import os
import datetime
from log import log
import logging
import random
import atexit
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
logonly = logging.getLogger('werkzeug')
logonly.setLevel(logging.ERROR)
app = Flask(__name__)



global cryptokey
cryptokey = b'W\xdf\xfb\x1dn\xc0\xd3\xe1\xce/\x08P\xe6P\rS\xe7\x07\xa6\xebyHwN,P\x0c\x08\x88\xd8\x9e\xda'
file = 'Hotel(new).db'
buffer_size = 65536

#==========================================================================
#============decrypt here=============
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
#=============encrypt===========================
#==========================================================
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
#==================================================================
decrypt("Hotel(new).db")

ALPHABET = [" ","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
# Set the ALPHABET array (containing a space on position 0) and the OTP array to empty
OTP = []
def generatekey():
    ranInst = random.SystemRandom() # Random so harder to reverse and decrypt
    for i in range(336):# range 336 because it is 48x8
        OTP.append(ALPHABET[ranInst.randint(1,26)]) # Random letter from list (1 to 26 because 0 is a space)
    cd = 0 # Counting the letters
    cl = 0 # Counting each group of 6 letters
    stringOTP = ""
    for i in range(336):
        cd += 1
        stringOTP += OTP[i]

    return stringOTP.lower()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///Hotel.db'
kyt = generatekey()
app.config['SECRET_KEY'] = kyt# supasecret
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_SQLALCHEMY'] = True
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1 per second"]
)

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

##For email unique=True
##class User(UserMixin, db.Model):
##    u_id = db.Column(db.Integer, primary_key=True)
##    u_email = db.Column(db.Text(50))
##    u_username = db.Column(db.Text(35))
##    u_password = db.Column(db.Text(200)) #200 is for encryption
##    u_credit_card = db.Column(db.Text(16))


class Guest(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    g_name = db.Column(db.Text(25))
    g_email = db.Column(db.Text(25))
    g_password = db.Column(db.Text(200))
    g_countryname = db.Column(db.Text(10))
    g_roomReserved = db.Column(db.Text(9))
    g_checkstatus = db.Column(db.Text(10))
    g_phone = db.Column(db.Text(25))
    g_credit_card = db.Column(db.Text(16))
    g_deposit = db.Column(db.Integer)
    room = db.relationship('Room')

@login_manager.user_loader
def load_user(g_id):
    return Guest.query.get(int(g_id))
class Room(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    r_checkstatus = db.Column(db.Text(25))
    r_cleanstatus = db.Column(db.Text(1))
    r_price = db.Column(db.Integer)
    r_bedtype = db.Column(db.Text(25))
    r_roomNumber = db.Column(db.Integer)
    r_guestid = db.Column(db.Integer, db.ForeignKey('guest.id'))
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
conn = sqlite3.connect('Hotel.db')
c = conn.cursor()

def OnExitApp():  #encrypt function
    encrypt("Hotel(new).db")

atexit.register(OnExitApp)

@app.route('/')
def index():
##    c.execute('SELECT * FROM User')
##    for row in c.fetchall():
##        print(row)
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
@limiter.limit("1 per 1 second")
def register():
    letterloop = 0
    logdigit = 0
    loglower = 0
    logupper = 0
    logsymbol = 0
    RegisterUser = RegisterUserForm(request.form) #make sure to clear and check fields are ok before inserting into sql database
    with open('./BannedPasswords/banned-passwords-1.txt', 'r') as BannedPassList:
        found = False
        if request.method == 'POST' and RegisterUser.validate():

            for line in BannedPassList:
                if str(RegisterUser.password.data) in line:
                    print("This password is not allowed")
                    return 'This password is not allowed'
            if not found:
                logpass = str(RegisterUser.password.data)
                while letterloop < len(logpass):
                    if logpass[letterloop].isdigit():
                        logdigit += 1
                    elif logpass[letterloop].islower():
                        loglower += 1
                    elif logpass[letterloop].isupper():
                        logupper += 1
                    else:
                        logsymbol += 1
                    letterloop += 1
                if logdigit >= 1 and loglower >= 1 and logupper >= 1 and logsymbol >= 1 and len(logpass) >= 8:
                    logpass = pbkdf2_sha256.hash(logpass)
                    user = Guest(g_name=RegisterUser.name.data, g_email=RegisterUser.email.data, g_password=logpass, g_credit_card=RegisterUser.cc.data, g_phone=RegisterUser.num.data)
                    db.session.add(user)
                    db.session.commit()
                    print("Guest successfully registered")
                    session['logged_in'] = 1
                    login_user(user)
                    try:
                        log.reg_new(RegisterUser.name.data)
                    except Exception:
                        print("Error occurred while logging Registering new user.")
                    return redirect(url_for('index'))
                else:
                    return 'Password must contain at least 1 digit, 1 symbol, 1 uppercase character and 1 lowercase character'

    return render_template('register.html', form=RegisterUser)

@app.route('/login', methods=['GET','POST'])
@limiter.limit("10 per 1 second")
def login():
    ipaddr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    RegisterUser = RegisterUserForm(request.form)
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    try:
        if not session['logged_in'] == 0:
            return "User is already logged in please log out first"
    except:
        pass
    if request.method == 'POST':
        logUname = str(RegisterUser.name.data)
        logpass = str(RegisterUser.password.data)
        print(logpass)
        try:
            if db.session.query(Manager.m_id).filter_by(m_name=logUname).first() is not None:
                user = Manager.query.filter_by(m_name=logUname).first()
                session['logged_in'] = 2
        except Exception:
            pass
        if db.session.query(Guest.id).filter_by(g_name=logUname).first() is not None:
            user = Guest.query.filter_by(g_name=logUname).first()
            session['logged_in'] = 1
        print("User successfully logged in as")
        login_user(user)
        return redirect(url_for('index'))
        print("FAILURE")
        return redirect(url_for('login'))    #change redirect to here
    else:
        print('hrub')

    return render_template('login.html', form=RegisterUser)

@app.route('/logout')
@login_required
def logout():
    session['logged_in'] = 0
    logout_user()
    print("User logged out")
    return redirect(url_for('index'))

@app.route('/show')
@login_required
def projects():
    output = Guest.query.all()
    log.dbSelect(app.config['SQLALCHEMY_DATABASE_URI'],"Guest",Guest.query.count())
    return render_template('show.html',out=output)

@app.route('/startproject', methods=['GET','POST']) #Not implemented yet, use register user logic, follow the requirements in the Project class~
@login_required
def startproject():
    if session['logged_in'] == 1:
        Proj = CreateProjectForm(request.form) #make sure to clear and check fields are ok before inserting into sql database
        if request.method == 'POST' and Proj.validate():
            NewProj = Project(userid=int(session['_user_id']),name=Proj.name.data,field=Proj.field.data,description=Proj.description.data,content=Proj.content.data,view=Proj.view.data)
            db.session.add(NewProj)
            db.session.commit()
            return redirect(url_for('projects'))
        return render_template('startproject.html', form=Proj)
    else:
        return redirect(url_for('index'))

@app.route('/edit/<id>', methods=['GET','POST']) #In implementation
def editcontent(id):
    print("PUT PROJECTID IN USER ID AS A LIST THEN PROJECT DATABASE JUST CONTAINS RAW PROJECT INFO")
    if session['logged_in'] == 1:
        project = Project.query.filter_by(id=id).first()
        comments = Comment.query.filter_by(projectid=project.id).all()

        if int(project.userid) == int(session['_user_id']):
            editProj = CreateProjectForm(request.form)
            comment = CreateComment(request.form)
            if request.method == 'POST' and editProj.pSubmit.data and editProj.validate():
                print("posted")
                project = Project.query.get(id)
                project.name = editProj.name.data
                project.field = editProj.field.data
                project.description = editProj.description.data
                project.content = editProj.content.data
                project.view = editProj.view.data
                db.session.commit()
                return redirect(url_for('projects'))
            elif request.method == 'POST' and comment.cSubmit.data and comment.validate():
                print("in",comments)
                newComment = Comment(userid = int(session['_user_id']), content = comment.comment.data, projectid = id)
                db.session.add(newComment)
                db.session.commit()
                return redirect(url_for('projects'))
            else:
                editProj.name.data = project.name
                editProj.field.data = project.field
                editProj.description.data = project.description
                editProj.content.data = project.content
                editProj.view.data = project.view

                return render_template('editcontent.html',pForm=editProj,name=project.name,cForm=comment,comments=comments)
        else:
            return 'You are not authorized to edit this project'
    else:
        return 'You must logged in to edit this project'

##@app.route('/sendnudes')
##def insert(mail, uname, pword, cc):
##    insert = '''
##INSERT INTO user (u_email, u_name)
##VALUES
##( ?, ?, ?, ?)
##'''
##    value=[(mail, uname, pword, cc)]
##    c.executemany(insert,value)
##    log.dbInsert("User.db","User",mail, uname, pword, cc)
##    conn.commit()
##    log.dbCommit("User.db","User")
##    try:
##        return render_template('query.html')
##    except AttributeError as e:
##        print("The Error: [ "+str(e)+" ] has occured")
##    except Exception:
##        print("Idk smt went wrong")
##
##@app.route('/select', methods=['GET','POST'])
##def select():
##    #replace replacement\/
##     X = string
##     Y = number of repetitions
##     replace(substr(quote(zeroblob((Y + 1) / 2)), 3, Y), '0', X)
##     select all the fields by name(not *) to change 1 or 2
##     substr(column, - x, x) to get last x chars
##    c.execute("SELECT u_id, replace(substr(quote(zeroblob((length(u_email) - 11) / 2)), 3, length(u_email)-12), '0', 'X') || substr(u_email, - 12, 12), u_username, u_password, 'XXXX XXXX XXXX ' || substr(u_credit_card, - 4, 4) FROM user;") #proof of concept
##    log.dbSelect("User.db","User")
##    for row in c.fetchall():
##        print(row)
##    try:
##        return render_template('search.html')
##    except AttributeError as e:
##        print("The Error: [ "+str(e)+" ] has occured")
##    except Exception:
##        print("Idk smt went wrong")
##insert("emailee@email.com","userman","password123","1234567890123456")
##select()
if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="127.0.0.1", port=int("5000"), debug=True, use_reloader=False)
