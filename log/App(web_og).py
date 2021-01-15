from flask import Flask, render_template, request, redirect, url_for, escape, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import form
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from Forms import RegisterUserForm, CreateProjectForm, SearchForm, CreateComment
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import re
from passlib.hash import pbkdf2_sha256
import stripe
import os
import datetime
import random
from Classes import check
import log

import logging
logonly = logging.getLogger('werkzeug')
logonly.setLevel(logging.ERROR)

context = ('cert.pem', 'key.pem')

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///db.sqlite3'


db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text(50), unique=True)
    username = db.Column(db.Text(35), unique=True)
    password = db.Column(db.Text(200)) #200 is for encryption
    paid = db.Column(db.Text(1)) #Either 1 or 0 for paid or unpaid user (string)
    role = db.Column(db.Text(15))#Either expert or user
    projects = db.relationship('Project', backref='owner')
    comments = db.relationship('Comment', backref='owner')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.Text(70))
    field = db.Column(db.Text(70)) #field of expertise
    description = db.Column(db.Text(70))
    content = db.Column(db.Text(30000))
    help = db.Column(db.Text(1)) # 0 for help not needed, 1 for help needed, user can change this at any time
    view = db.Column(db.Text(17)) #Public (Everyone is free to view), Unlisted (You + Expert) or Private (Only you)
    comments = db.relationship('Comment', backref='proj')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projectid = db.Column(db.Integer, db.ForeignKey('project.id'))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text(4000))

class iptable(db.Model):
    ip = db.Column(db.Text(17), primary_key=True)
    retry = db.Column(db.Integer)
    time = db.Column(db.Text(300))

db.create_all()

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

@app.route('/')
def index():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM User')
    for row in c.fetchall():
        print(row)
    print(session.get("logged_in"))
    return render_template('index.html')


@app.route('/projects')
@login_required
def projects():
    project = Project.query.filter_by(userid=int(session['_user_id'])).all()
    return render_template('projects.html',project_obj=project)

@app.route('/search', methods=['GET','POST']) #Not implemented yet, use register user logic but backwards, create filter for type, project must be public, fit name, and field criterion
@login_required
def search():
    Searchform = SearchForm(request.form)
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    if request.method == 'POST':
        searchQuery = str(Searchform.name.data).lower()
        c.execute('SELECT * FROM Project')

        for row in c.fetchall():
            print(row[2],row[3])

        if searchQuery in row[2].lower():
            project = Project.query.filter_by(name=searchQuery).first()

        elif row[3].lower() == searchQuery:
            project = Project.query.filter_by(field=searchQuery).first()

        else:
            return "No projects with this name/field found"


        ProjectID = [] #Append to list to send to javascript if they meet the given criteria in the search.
        ProjectIMG = []


    return render_template('search.html', form=Searchform)

@app.route('/requestexpert') #Not implemented yet, function.
@login_required
def requestexpert():
    if session['logged_in'] == 1:
        project = Project.query.filter_by(userid=load_user).first()
        if project.help == '0':
            project.help = '1'
            db.session.commit()
            print("Successfully requested")
        elif project.help == '1':
            project.help = '0'
            db.session.commit()
            print("Successfully rescinded request")
    else:
        return 'You are not allowed to access this page'

@app.route('/clientprojects') #Not implemented yet
@login_required
def clientprojects():

    if session['logged_in'] == 2:
        return render_template('clientprojects.html')
    else:
        return 'You are not allowed to access this page'

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

@app.route('/addcomment') #Not implemented yet, this is a function, on click it will execute and add the comment to the project database
@login_required
def addcomment(): #Follow how a user is added to add stuff to the db!

    if session['logged_in'] == 1:
        pass
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'super secret kyt'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="127.0.0.1", port=int("5000"), debug=False, use_reloader=False)
