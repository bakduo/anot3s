'''
#############################################################################
#                                                                           #
#   AnotesModel.py                                                          #
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


#Importamos la libreria gtk
import optparse
import gtk
import time
import os
import sys
import threading
from Client import ClientAnotes
from Server import ReceptAnotes


class AnotesModel(object):
    def __init__(self):
        self.state=0
        self.contacts={}
        self.cantContact=0
        self.server=ReceptAnotes()
        self.server_message_thread=None

    def getContact(self,id):
        return self.contacts[id]

    def addContact(self,ip,port):
        patner = ClientAnotes();
        patner.setPort(port)
        patner.setServer(ip)
        self.cantContact = self.cantContact + 1
        self.contacts[ip]=patner

    def sendMessageToPatner(self,ip,message):
        patner=self.getContact(ip)
        print str(patner)
        patner.setMessage(message)
        patner.send()

    def setCantContact(self,cant):
       self.cantContact = cant

    def getCantContact(self):
       return self.cantContact
        
    def configServer(self,port,ip):
        if (self.server==null):
            self.server=ReceptAnotes()
        self.server.setPort(port)
        self.server.setIp(ip)

    def launchServer(self):
        self.server.run()

    def runServer(self):
        self.server_message_thread = threading.Thread(target=self.server.run_command())
        self.server_message_thread.start()
        #self.launchServer()

    def stopServer(self):
        self.server.setState(1)
        if self.server_message_thread is None:
             print "Sin thread"
             if int(self.server.pid) <> int(-1):
                 self.server.close_process()
        else:
             try:
                 if self.server_message_thread.isAlive():
                     self.server_message_thread.stop()
                 #self.server.close_process()
                 os.system("kill -9 "+str(self.server.getPid()));
                 gtk.main_quit
             except:
                 e = sys.exc_info()[0]
                 print( "<p>Error: %s</p>" % e )

    def close_server(self):
        self.stopServer()

