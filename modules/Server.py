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

#Importamos la libreria pygtk
import pygtk
#Especificamos la version de pygtk a usar, normalmente la 2.0
pygtk.require("2.0")
#Importamos la libreria gtk
import optparse
import gobject
import gtk
import socket
import sys, getopt
import subprocess
import threading
import os
import time
import datetime
import random
import shutil
import psutil
from Client import ClientAnotes

class SocketServerMessage(threading.Thread):
    #def __init__(self, (client,address),nombre):
    def __init__(self,nombre,port,ip):
        threading.Thread.__init__(self)
        #self.runnable = function_server
        self.address = None
        self.TCP_PORT = port
        self.TCP_IP = ip
        self.nombre = nombre
        self.size = 8096
        self.running = 1
        self.serverMessage= None
        self.path=os.path.dirname(os.path.realpath(__file__))
        self.open_socketMessage(self.TCP_PORT)

    def savePid(self,pid):
      try:
          archivo_path = self.path + "/../pid_enabled"
          file_handle = open(archivo_path, "a")
          file_handle.writelines(str(pid)+"\n")
          file_handle.close()
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

    def saveMessage(self,message):
        try:
            path=os.path.dirname(os.path.realpath(__file__))
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
             client, addr = self.serverMessage.accept()
             ip="%s:%d" % (addr)
             self.address = ip.split(':')[0]#self.client.getpeername()#str(address)
             print "Conectado cliente: %s\n" % self.address
             msj = "";
             while self.running==1:
                 data = client.recv(self.size)
                 if not data:
                    break
                 print len(data)
                 print "received data: \n", data
                 msj=msj + str(data)
             client.close()
             self.saveMessage(msj)
             newenv = os.environ.copy()
             newenv['anotes_message_answer'] = 'True'
             path=os.path.dirname(os.path.realpath(__file__))
             programa_app = path + "/../ShowAnswer.py"
             args = [str(programa_app),'-c',str(self.address),'-m',str(msj), '-n',str(self.nombre)]
             proc = subprocess.Popen(args, env=newenv)
             print "Pid showmessage: %s " % proc.pid
             self.savePid(proc.pid)
             #   self.newenv = os.environ.copy()
             #   self.newenv['anotes_message'] = 'True'
             #   args = ['/usr/bin/gxmessage','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes message",data]
             #   self.saveMessage(data)
             #   proc = subprocess.Popen(args, env=self.newenv)
             #   print "received data: \n", data
             #conn.close()

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
        print "corriendo fileserver"
        archivo_path=os.path.dirname(os.path.realpath(__file__))
        archivo_nombre=random.randrange(0, 100000, 1)
        nombre_archivo_remoto = self.client.recv(self.size)
        archivo_path = archivo_path + "/../adjuntos/"  + str(archivo_nombre) + nombre_archivo_remoto +".adjunto"
        file_handle = open(archivo_path, "wb")
        while self.running==1:
            data = self.client.recv(self.size)
            if not data:
                break
            print len(data)
            file_handle.write(data)
        self.client.close()
        file_handle.close()

    def stop(self):
        self.running=0

class ReceptAnotes(object):
    def __init__(self):
        self.TCP_IP = '0.0.0.0'
        self.TCP_PORT = 24837
        self.TCP_PORTFILE = 24839
        self.BUFFER_SIZE = 8096
        self.state = 0
        self.pid=-1
        self.pidFile = -1
        self.path=os.path.dirname(os.path.realpath(__file__))
        self.FILE = None
        self.newenv= None
        self.newenvfile= None
        self.serverFile= None
        self.serverMessage = None
        self.serverNotesName =""
        self.clients = []
        self.threads = []
        self.pids=[]

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
        #path=os.path.dirname(os.path.realpath(__file__))
        try:
            if os.path.isfile(self.path+'/history.txt'):
                f = open(self.path+'/history.txt','a')
                f.writelines(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
                f.writelines("\n")
                f.writelines(message)
                f.writelines("\n")
                f.close()
            else:
                f = open(self.path+'/history.txt','w')
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

    def savePid(self,pid):
      try:
          archivo_path = self.path + "/../pid_enabled"
          file_handle = open(archivo_path, "a")
          file_handle.writelines(str(pid)+"\n")
          file_handle.close()
          self.pids.append(pid)
      except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
      except:
            print "Unexpected error:", sys.exc_info()[0]

    def run_server(self):
        #thread = SocketServerMessage(self.serverNotesName,self.TCP_PORT,self.TCP_IP)
        #self.threads.append(thread)
        #thread.start()
        #thread.join()
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.bind((self.TCP_IP, self.TCP_PORT))
        #s.listen(1)
        self.open_socketMessage(self.TCP_PORT)
        address_normal = ''
        while self.state==0:
             client,addr = self.serverMessage.accept()
             ip="%s:%d" % (addr)
             address_normal = ip.split(':')[0]
             print "Conectado cliente: %s\n" % address_normal
             msj = "";
             while self.state==0:
                 data = client.recv(self.BUFFER_SIZE)
                 if not data:
                    break
                 print len(data)
                 print "received data: \n", data
                 msj=msj + str(data)
             client.close()
             self.saveMessage(msj)
             newenv = os.environ.copy()
             newenv['anotes_message_answer'] = 'True'
             #path=os.path.dirname(os.path.realpath(__file__))
             programa_app = self.path + "/ShowAnswer.py"
             args = [str(programa_app),'-c',str(address_normal),'-m',str(msj), '-n',str(self.serverNotesName)]
             proc = subprocess.Popen(args, env=newenv)
             print "Pid showmessage: %s \n" % proc.pid
             self.savePid(proc.pid)
             #c = SocketServerMessage(self.serverMessage.accept(),self.serverNotesName)
             #self.threads.append(c)
             #c.start()
             #   self.newenv = os.environ.copy()
             #   self.newenv['anotes_message'] = 'True'
             #   args = ['/usr/bin/gxmessage','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes message",data]
             #   self.saveMessage(data)
             #   proc = subprocess.Popen(args, env=self.newenv)
             #   print "received data: \n", data
             #conn.close()
        self.serverMessage.close()
        #for c in self.threads:
        #    c.join()

    def run_serverFile(self):
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.bind((self.TCP_IP, self.TCP_PORTFILE))
        #s.listen(1)
        self.open_socketFile(self.TCP_PORTFILE)
        print "Iniciando server file..."
        while self.state==0:
            #c = SocketServerFile((self.serverFile.accept()))
            #self.threads.append(c)
            #c.start()
            conn, addr = self.serverFile.accept()
            print 'Connection address:', addr
            nombre_archivo = conn.recv(self.BUFFER_SIZE)
            #conn.send(self.BUFFER_SIZE)
            conn.send(nombre_archivo)
            print "Nombre archivo recibido: %s\n" % nombre_archivo
            archivo_path=os.path.dirname(os.path.realpath(__file__))
            archivo_nombre=random.randrange(0, 100000, 1)
            archivo_path = archivo_path + "/../adjuntos/"  + str(archivo_nombre) + nombre_archivo +".adjunto"
            #archivo_path = archivo_path+"/../adjuntos/"+"_"+nombre_archivo+"_"+str(archivo_nombre)+".adjunto"
            file_handle = open(archivo_path, "wb")
            while self.state==0:
                data = conn.recv(self.BUFFER_SIZE)
                if not data:
                    break
                print len(data)
                file_handle.write(data)
                #print "received data: \n", data
            conn.close()
        self.serverFile.close()

    def runFileServer(self):
      self.run_serverFile()
    def run(self):
      self.run_server()

    def closeThread(self):
       for thread in self.threads:
           thread.join()

    def run_command(self,nombre):
       if (self.pid==-1):
          if (self.newenv):
              self.newenv['anotes_run'] = 'True'
          else:
              self.newenv = os.environ.copy()
              self.newenv['anotes_run'] = 'True'
          #path=os.path.dirname(os.path.realpath(__file__))
          path = self.path + '/Server.py'
          args = ['/usr/bin/python',path,'-s', '0.0.0.0', '-p',str(self.TCP_PORT),'-n',str(nombre)]
          proc = subprocess.Popen(args, env=self.newenv)
          self.pid = proc.pid
          print "Pid message: "+str(self.pid)

    def run_commandFile(self,nombre):
       if (self.pidFile==-1):
          if (self.newenvfile):
              self.newenvfile['anotes_run_file'] = 'True'
          else:
              self.newenvfile = os.environ.copy()
              self.newenvfile['anotes_run_file'] = 'True'

          #path=os.path.dirname(os.path.realpath(__file__))
          path = self.path + '/Server.py'
          args = ['/usr/bin/python',path,'-s', '0.0.0.0', '-f',str(self.TCP_PORTFILE),'-n',str(nombre)]
          proc = subprocess.Popen(args, env=self.newenvfile)
          self.pidFile = proc.pid
          print "Pid file: "+str(self.pidFile)

    def getPidsMessage(self):
       return self.pids

    def close_process(self):

       for pid_message in self.pids:
           if psutil.pid_exists(pid_message):
               print "Pid showmessage : %s" % str(pid_message)
               p = psutil.Process(pid_message)
               print "Proceso message: %s\n" % (str(p.get_num_threads()))
               print "Procesos info: %s\n" % (str(p.get_threads()))
               try:
                   os.system("kill -9 "+str(pid_message));
               except OSError:
                   print "Error al eliminar el programa showmessage."

       self.closeThread()
       for proces in 1,2:
           if proces == 1:
               pid = self.pid
               if pid > 0:
                  self.newenv['anotes_run'] = 'False'
                  #args = ['/bin/kill','-9',str(pid)]
                  #proc=subprocess.call(args,env=self.newenv)
                  #print "Proceso de borrado estado: %s proceso: %s: " %(str(proc),str(proces))
                  #print "Proceso pid: %s\n" % str(pid)
                  if psutil.pid_exists(pid):
                      p = psutil.Process(pid)
                      print "Proceso message: %s\n" % (str(p.get_num_threads()))
                      print "Procesos info message: %s\n" % (str(p.get_threads()))
                      try:
                          os.system("kill -9 "+str(pid));
                      except OSError:
                          print "Error al eliminar el proceso message desde server."
           elif proces == 2:
               pid = self.pidFile
               if pid > 0:
                  self.newenv['anotes_run_file'] = 'False'
                  if psutil.pid_exists(pid):
                      p = psutil.Process(pid)
                      print "Proceso file: %s\n" % (str(p.get_num_threads()))
                      print "Procesos file info: %s\n" % (str(p.get_threads()))
                      try:
                          os.system("kill -9 "+str(pid));
                      except OSError:
                          print "Error al eliminar el proceso file desde server."
                  #args = ['/bin/kill','-9',str(pid)]
                  #proc=subprocess.call(args,env=self.newenvfile)
                  #print "Proceso de borrado estado: %s proceso: %s: " %(str(proc),str(proces))
                  #print "Proceso pid: %s\n" % str(pid)

    def setServerNotesName(self,name):
      self.serverNotesName=name

def main():
   ip = ''
   puerto =''
   puertoarchivo=''
   nombre=''
   try:
      if len(sys.argv) < 2:
          print 'Por ahora solo permite 3 argumentos atnotes -s server -p port' 
          return 2
      opts, args = getopt.getopt(sys.argv[1:],"hs:p:f:n:")

   except getopt.GetoptError:
      print 'atnotes.py -s <ip> -p <puerto> -f <puertoarchivo> -n <nombre>'
      return 2
   for opt, arg in opts:
      print " %s : %s" % (opt,arg)
      if opt == '-h':
         print 'atnotes.py -s <ip> -p <puerto> -f <puertoarchivo> -n <nombre>'
         sys.exit()
      elif opt in ("-s"):
         ip = arg
      elif opt in ("-p", "--puerto"):
         puerto = arg
      elif opt in ("-f", "--fpuerto"):
         puertoarchivo = arg
      elif opt in ("-n"):
         nombre = arg

   '''
   print 'ip is %s' % ip
   print 'puerto is %s' % puerto
   print 'puertoarchivo is %s' % puertoarchivo
   '''
   server = ReceptAnotes()
   server.setIp(ip)
   server.setServerNotesName(nombre)

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
