#!/usr/bin/env python

'''
#############################################################################
#                                                                           #
#   Server.py                                                               #
#   Copyright (C) 2013 linuxknow                                            #
#   linuxknow [at] gmail dot com                                            #
#   This program is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   (at your option) any later version.                                     #
#                                                                           #
#   This program is distributed in the hope that it will be useful,         #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>    #
#                                                                           #
#############################################################################
'''

import socket
import sys, getopt
import subprocess
import threading
import os
import time
import datetime


class SocketServerMessage(threading.Thread):
    def __init__(self, funcion_server):
        threading.Thread.__init__(self)
        self.runnable = function_server
    def run(self):
        self.runnable()


class ReceptAnotes(object):
    def __init__(self):
        self.TCP_IP = '0.0.0.0'
        self.TCP_PORT = 24837
        self.BUFFER_SIZE = 4096  # Normally 1024, but we want fast response
        self.state = 0
        self.pid=-1
        self.newenv=None

    def getPid(self):
       return self.pid

    def setPort(self,port):
        self.TCP_PORT=port
    
    def setIp(self,ip):
        self.TCP_IP=ip

    def setState(self,estado):
        self.state = estado

    def saveMessage(self,message):
        path=os.path.dirname(os.path.realpath(__file__))
        try:
            if os.path.isfile(path+'/history.txt'):
                f = open(path+'/history.txt','a')
                f.writelines(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
                f.writelines("\n")
                f.writelines(message)
                f.writelines("\n")
                f.close()
            else:
                f = open(path+'/history.txt','w')
                f.writelines(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
                f.writelines("\n")
                f.writelines(message)
                f.writelines("\n");
                f.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]


    def run_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.TCP_IP, self.TCP_PORT))
        s.listen(1)
        while self.state==0:
             conn, addr = s.accept()
             print 'Connection address:', addr
             while self.state==0:
                data = conn.recv(self.BUFFER_SIZE)
                if not data: 
                    break
                print len(data)
                self.newenv = os.environ.copy()
                self.newenv['anotes_message'] = 'True'
                args = ['/usr/bin/gxmessage','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes message",data]
                self.saveMessage(data)
                proc = subprocess.Popen(args, env=self.newenv)
                print "received data: \n", data
             conn.close()

    def run(self):
       thread = SocketServerMessage(self.run_server())
       thread.start()
       thread.join()

    def run_command(self):
       self.newenv = os.environ.copy()
       self.newenv['anotes_run'] = 'True'
       path=os.path.dirname(os.path.realpath(__file__))
       path = path + '/Server.py'
       args = ['/usr/bin/python',path,'-s', '0.0.0.0', '-p','24837','2>1 >/dev/null &']
       proc = subprocess.Popen(args, env=self.newenv)
       self.pid = proc.pid
       print "Pid: "+str(self.pid)

    def close_process(self):
       args = ['/bin/kill','-9',self.pid]
       self.newenv['anotes_run'] = 'False'
       proc=subprocess.call(args,env=self.newenv)
       print "Proceso de borrado: "+str(proc)


def main():
   ip = ''
   puerto = ''
   try:
      if len(sys.argv) < 2:
          print 'Por ahora solo permite 3 argumentos atnotes -s server -p port' 
          return 2
      opts, args = getopt.getopt(sys.argv[1:],"hs:p:")

   except getopt.GetoptError:
      print 'atnotes.py -s <ip> -p <puerto>'
      return 2
   for opt, arg in opts:
      print " %s : %s" % (opt,arg)
      if opt == '-h':
         print 'atnotes.py -s <ip> -p <puerto>'
         sys.exit()
      elif opt in ("-s"):
         ip = arg
      elif opt in ("-p", "--puerto"):
         puerto = arg

   '''
   print 'ip is %s' % ip
   print 'puerto is %s' % puerto
   '''
   server = ReceptAnotes()
   server.setPort(int(puerto))
   server.setIp(ip)
   server.run()
   return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
