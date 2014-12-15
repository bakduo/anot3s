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
import random

class SocketServerMessage(threading.Thread):
    def __init__(self, (client,address)):
        threading.Thread.__init__(self)
        #self.runnable = function_server
        self.client = client
        self.address = address
        self.size = 8096
        self.running = 1
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
    def run(self):
        #self.runnable()
        while self.running==1:
            data = self.client.recv(self.size)
            if not data:
                break
            print len(data)
            newenv = os.environ.copy()
            newenv['anotes_message'] = 'True'
            args = ['/usr/bin/gxmessage','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes message",data]
            self.saveMessage(data)
            proc = subprocess.Popen(args, env=newenv)
            print "received data: \n", data
        self.client.close()
    def stop(self):
        self.running=0

class SocketServerFile(threading.Thread):
    def __init__(self, (client,address)):
        threading.Thread.__init__(self)
        #self.runnable = function_server_file
        self.client = client
        self.address = address
        self.size = 8096
        self.running = 1

    def run(self):
        #self.runnable()
        #print "corriendo fileserver"
        archivo_path=os.path.dirname(os.path.realpath(__file__))
        archivo_nombre=random.randrange(0, 100000, 1)
        #print archivo_path
        #print archivo_path
        nombre_archivo_remoto = self.client.recv(self.size)
        archivo_path = archivo_path + "/../adjuntos/"  + str(archivo_nombre) + nombre_archivo_remoto +".adjunto"
        file_handle = open(archivo_path, "wb")
        while self.running==1:
            data = self.client.recv(self.size)
            if not data:
                break
            print len(data)
            file_handle.write(data)
            #print "server received data: \n", data
        self.client.close()
        file_handle.close()
        
    def stop(self):
        self.running=0

class ReceptAnotes(object):
    def __init__(self):
        self.TCP_IP = '0.0.0.0'
        self.TCP_PORT = 24838
        self.TCP_PORTFILE = 24839
        self.BUFFER_SIZE = 8096  # Normally 1024, but we want fast response
        self.state = 0
        self.pid=-1
        self.pidFile = -1
        self.FILE = None
        self.newenv= None
        self.serverFile= None
        self.serverMessage = None
        self.threads = []

    def getPid(self):
       return self.pid

    def getPidFile(self):
       return self.pidFile
    def setPort(self,port):
        self.TCP_PORT=port        
    def setPortFile(self,port):
        self.TCP_PORTFILE=port

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


    def open_socketMessage(self,port): 
        try:
            self.serverMessage = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverMessage.bind((self.TCP_IP, port))
            self.serverMessage.listen(5) 
        except socket.error, (value,message): 
            if self.serverMessage: 
                self.serverMessage.close()
            print "Could not open socket: " + message 
            sys.exit(1) 
    def open_socketFile(self,port): 
        try:
            self.serverFile = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverFile.bind((self.TCP_IP, port))
            self.serverFile.listen(5) 
        except socket.error, (value,message): 
            if self.serverFile: 
                self.serverFile.close()
            print "Could not open socket: " + message 
            sys.exit(1) 

    def run_server(self):
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.bind((self.TCP_IP, self.TCP_PORT))
        #s.listen(1)
        self.open_socketMessage(self.TCP_PORT)
        while self.state==0:
             c = SocketServerMessage(self.serverMessage.accept())
             c.start()
             self.threads.append(c)
             #conn, addr = s.accept()
             #print 'Connection address:', addr
             #while self.state==0:
             #   data = conn.recv(self.BUFFER_SIZE)
             #   if not data:
             #       break
             #   print len(data)
             #   self.newenv = os.environ.copy()
             #   self.newenv['anotes_message'] = 'True'
             #   args = ['/usr/bin/gxmessage','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes message",data]
             #   self.saveMessage(data)
             #   proc = subprocess.Popen(args, env=self.newenv)
             #   print "received data: \n", data
             #conn.close()
        self.serverMessage.close()
        for c in self.threads:
            c.join()

    def run_serverFile(self):
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.bind((self.TCP_IP, self.TCP_PORTFILE))
        #s.listen(1)
        self.open_socketFile(self.TCP_PORTFILE)
        print "Iniciando server file..."
        while self.state==0:
            c = SocketServerFile((self.serverFile.accept()))
            c.start()
            self.threads.append(c)
            #conn, addr = s.accept()
            #print 'Connection address:', addr
            #archivo_path=os.path.dirname(os.path.realpath(__file__))
            #archivo_nombre=random.randrange(0, 100000, 1)
            #archivo_path = archivo_path + archivo_nombre + ".adjunto"
            #file_handle = open(archivo_path, "wb")
            #while self.state==0:
            #    data = conn.recv(self.BUFFER_SIZE)
            #    if not data:
            #        break
            #    print len(data)
            #    file_handle.write(data)
            #    print "received data: \n", data
            #conn.close()
            #file_handle.close()
        self.serverFile.close()
        for c in self.threads:
            c.join()

    def runFileServer(self):
      self.run_serverFile()
    def run(self):
      self.run_server()
      #self.run_server()
      #threads = []
      #for n in range(2):
      #    print n
      #    if (n==0):
      #        thread = threading.Thread(target=self.run_server())
      #    if (n==1):
      #        thread = threading.Thread(target=self.run_serverFile())
      #    thread.start()
      #    threads.append(thread)        
      #for thread in threads:
      #    thread.join()

    def closeThread(self):
       for thread in self.threads:
           if thread.isAlive():
               thread.stop()

    def run_command(self):
       self.newenv = os.environ.copy()
       self.newenv['anotes_run'] = 'True'
       path=os.path.dirname(os.path.realpath(__file__))
       path = path + '/Server.py'
       args = ['/usr/bin/python',path,'-s', '0.0.0.0', '-p','24838','2>1 >/dev/null &']
       proc = subprocess.Popen(args, env=self.newenv)
       self.pid = proc.pid
       print "Pid message: "+str(self.pid)
    def run_commandFile(self):
       self.newenv = os.environ.copy()
       self.newenv['anotes_run'] = 'True'
       path=os.path.dirname(os.path.realpath(__file__))
       path = path + '/Server.py'
       args = ['/usr/bin/python',path,'-s', '0.0.0.0', '-f','24839','2>1 >/dev/null &']
       proc = subprocess.Popen(args, env=self.newenv)
       self.pidFile = proc.pid
       print "Pid file: "+str(self.pid)

    def close_process(self):
       args = ['/bin/kill','-9',self.pid]
       self.newenv['anotes_run'] = 'False'
       proc=subprocess.call(args,env=self.newenv)
       print "Proceso de borrado: "+str(proc)


def main():
   ip = ''
   puerto =''
   puertoarchivo=''
   try:
      if len(sys.argv) < 2:
          print 'Por ahora solo permite 3 argumentos atnotes -s server -p port' 
          return 2
      opts, args = getopt.getopt(sys.argv[1:],"hs:p:f:")

   except getopt.GetoptError:
      print 'atnotes.py -s <ip> -p <puerto> -f <puertoarchivo>'
      return 2
   for opt, arg in opts:
      print " %s : %s" % (opt,arg)
      if opt == '-h':
         print 'atnotes.py -s <ip> -p <puerto> -f <puertoarchivo>'
         sys.exit()
      elif opt in ("-s"):
         ip = arg
      elif opt in ("-p", "--puerto"):
         puerto = arg
      elif opt in ("-f", "--fpuerto"):
         puertoarchivo = arg

   '''
   print 'ip is %s' % ip
   print 'puerto is %s' % puerto
   print 'puertoarchivo is %s' % puertoarchivo
   '''
   server = ReceptAnotes()
   server.setIp(ip)

   if puertoarchivo != '':
       server.setPortFile(int(puertoarchivo))
       server.runFileServer()

   if puerto != '':
       server.setPort(int(puerto))
       server.run()
   return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
