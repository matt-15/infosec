import os
import re
from flask import Flask
from wtforms import Form, StringField, TextAreaField, validators, DecimalField, RadioField, SelectField, FileField, BooleanField, SubmitField

class RegisterUserForm(Form):
    name = StringField('Name', [validators.Length(min=1,max=35), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=1,max=50), validators.Email()])
    password = StringField('Password', [validators.Length(min=1,max=40), validators.DataRequired()])
    cc = StringField('Credit Card', [validators.Length(min=14,max=16), validators.DataRequired()])
    num = StringField('Phone Number', [validators.Length(min=5,max=20), validators.DataRequired()])

class new_man(Form):
    name = StringField('Name', [validators.Length(min=1,max=70), validators.DataRequired()])
    salary = StringField('salary', [validators.Length(min=1,max=70)])
    age = StringField('age', [validators.Length(min=1,max=70)])
    gender = StringField('gender', [validators.Length(min=1,max=30000)])
    department = StringField('department', [validators.Length(min=1,max=17), validators.DataRequired()])
    password = StringField('password', [validators.Length(min=1,max=70)])
    submit = SubmitField("Add")
class CreateComment(Form):
    comment = StringField('Comment', [validators.Length(max=70)])
    cSubmit = SubmitField('Post')

class SearchForm(Form):
    name = StringField('Name', [validators.Length(min=1,max=80), validators.DataRequired()])
