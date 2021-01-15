from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
Base = declarative_base()
import sqlite3
import subprocess
import sys
import requests

import shelve

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
def read_from_db():
    c.execute('SELECT * FROM User')
    for row in c.fetchall():
        print(row)

def install(package, ver):
    line = '{} -m pip install {}=={}'.format(sys.executable, package, ver)
    # print(line)
    subprocess.check_call(line)

def check(namelist):
    for name in namelist:
        latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(name)], capture_output=True, text=True))
        latest_version = latest_version[latest_version.find('(from versions:')+15:]
        latest_version = latest_version[:latest_version.find(')')]
        latest_version = latest_version.replace(' ','').split(',')[-1]

        current_version = str(subprocess.run([sys.executable, '-m', 'pip', 'show', '{}'.format(name)], capture_output=True, text=True))
        current_version = current_version[current_version.find('Version:')+8:]
        current_version = current_version[:current_version.find('\\n')].replace(' ','')

        currentchk = is_it_safe('', name, current_version)
        latestchk = is_it_safe('', name, latest_version)

        #  true = safe  false = no safe
        if latestchk == False:
            print(name, latest_version, 'is not safe!')
        elif current_version == latest_version:
            print(name, current_version, 'is already the safest!')
        else:
            install(name, latest_version)


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
def is_it_safe(vendor, product, version):
    r = requests.get(
        "https://www.cvedetails.com/version-search.php?"
        "vendor={vendor}&product={product}&version={version}".format(
            vendor=vendor, product=product, version=version
        ),
        headers={"User-Agent": USER_AGENT},
    )

    reply = r.text[7577:7587]
    reply2 = r.text[14870:14892]
    # print(reply, '1', reply2, '2', ' findme')

    if reply == 'No matches':
        return True

    elif reply2 == 'searchresults sortable':
        return False


