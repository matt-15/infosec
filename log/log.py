import logging
##from log import send_gmail as g
##from log import log_in
logging.basicConfig(filemode='a',
                    datefmt='%Y-%m-%dT%H:%M:%S%z',
                    )

format_1 = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')
format_2 = logging.Formatter('%(asctime)s%(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')

def setup_logger1(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(format_1)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_logger2(name, log_file, level=logging.DEBUG):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(format_2)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

##init loggers--
logC=setup_logger1('commit','log/logCommits.txt')
logS=setup_logger1('security','log/logSecurity.txt')
logIN=setup_logger2('IDSin','log/IDSin.txt')


##logs for dbcommits--
def dbInsert(db,table,mail, uname, cc, row):
    ##dbInsertIN(row,db)
    logC.info('action"INSERT"; databse: "{0}"; table:"{1}"; rows:"{2}"; message: "Insert in the following data to database"; data: "{3}, {4}, {5}"'.format(db, table, row, mail, uname, cc))
    
def dbCommit(db,table,row):
    ##dbCommitIN(row,db)
    logC.info('action"Commit"; databse: "{0}"; table:"{1}"; rows:"{2}"; message: "previous action has been commited to the database"'.format(db,table,row))

def dbSelect(db,table,row):
    dbSelectIN(row,db)
    logC.info('action"SELECT"; databse: "{0}"; table:"{1}"; rows: "{2}"; message: "Rows were queried"'.format(db,table,row))

##logs for security--
def loginp(user):
    logS.info('User({user:s}) has logged In.'.format(user=user))
    
def loginf(user):
    logS.error('User({user:s}) failed login attempt.'.format(user=user))

def logino(user):
    logS.info('User({user:s}) has logged Out.'.format(user=user))

def reg_new(user):
    logS.info('User({user:s}) has registered a new account.'.format(user=user))

def login_report(ip):
    g.main(ip)

##logs for commit for sean ingest format--
def get_id():
    try:
        file=open("log/IDSin.txt", "r")
        for line in file:
            last=line
        print(last)
        print(last.split(",")[1])
        idsnuts=int(last.split(",")[1])+1
        file.close()
    except NameError:
        print("NameError in assigning ID for log in IDSin defult=0 (maybe cause by first start of empty log file)")
        idsnuts=0
    return idsnuts

def dbInsertIN(row,db):
    logIN.info(',{0},INSERT,{1},{2}'.format(get_id(),row,db))

def dbCommitIN(row,db):
    logIN.info(',{0},Commit,{1},{2}'.format(get_id(),row,db))

def dbSelectIN(row,db):
    logIN.info(',{0},SELECT,{1},{2}'.format(get_id(),row,db))


##dbInsert("db","table","mail", "uname", "pword", "cc","row")
##dbCommit()
##logino('tes')
##login_report('192.168.1.69420')
##payment_made('tes')
#dbSelect("db","table","rows")
