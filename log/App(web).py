from flask import Flask, render_template, request
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from log import log
import logging
logonly = logging.getLogger('werkzeug')
logonly.setLevel(logging.ERROR)
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///User.db'


db = SQLAlchemy(app)

##For email unique=True
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text(50), )
    username = db.Column(db.Text(35))
    password = db.Column(db.Text(200)) #200 is for encryption
    credit_card = db.Column(db.Text(16))

db.create_all()
conn = sqlite3.connect('user.db')
c = conn.cursor()

@app.route('/')
def index():
    c.execute('SELECT * FROM User')
    for row in c.fetchall():
        print(row)
    return render_template('index.html')


@app.route('/sendnudes')
def insert(mail, uname, pword, cc):
    insert = '''
INSERT INTO user (email, username, password, credit_card)
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

@app.route('/select', methods=['GET','POST'])
def select():
    c.execute('SELECT * FROM user')
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
