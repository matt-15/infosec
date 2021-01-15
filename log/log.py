import logging
from log import send_gmail as g
logging.basicConfig(filename="log\logCommits.txt",
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S%z',
                    level=logging.DEBUG)

def dbInsert(db,table,mail, uname, pword, cc):
    logging.info('action"INSERT"; databse: "{0}"; table:"{1}"; message: "Insert in the following data to database"; data: "{2}, {3}, {4},{5}"'.format(db,table,mail, uname, pword, cc))

def dbCommit(db,table):
    logging.info('action"Commit"; databse: "{0}"; table:"{1}"; message: "previous action has been commited to the database"'.format(db,table))

def dbSelect(db,table):
    logging.info('action"SELECT"; databse: "{0}"; table:"{1}"'.format(db,table))

def login_report(ip):
    g.main(ip)

##dbInsert()
##dbCommit()
##logino('tes')
##login_report('192.168.1.69420')
##payment_made('tes')
