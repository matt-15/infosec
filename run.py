##from multiprocessing import Process
##
##
##def Application():
##  print('starting')
##  import Application
##  print ('func1: finishing')
##
##def updateLog():
##  print('starting')
##  Application.test()
##  print ('func2: finishing')
##
##if __name__ == '__main__':
##  p1 = Process(target=Application)
##  p1.start()
##  p2 = Process(target=updateLog)
##  p2.start()
##  p1.join()
##  p2.join()
##
f = open("log/logCommits.txt", "r")
f.readlines()[0]
