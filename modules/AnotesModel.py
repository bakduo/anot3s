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
import socket
import time
import os
import sys
import threading
from scapy.all import *
from Client import ClientAnotes
from Server import ReceptAnotes

class PortScan(object):
    def __init__(self):
        self.ip="0.0.0.0"
        self.dst="0.0.0.0"
        self.port_dst=1024
        self.port_src=1024
    def setPortDst(self,port):
        self.port_dst=port
    def setIpDst(self,ip):
        self.dst=ip


    def scan_service(self):
        #ip_packet = IP(src=self.ip, dst=self.dst)
        #TCP_SYN_packet = TCP(sport=RandShort(), dport=int(self.port_dst), flags='S', seq=100)
        #TCP_SYNACK_reply = sr(ip_packet/TCP_SYN_packet,timeout=1)
        #if TCP_SYNACK_reply is None:
        #    print "\nPort " + self.port_dst + " is closed on host " + self.dst
        #    return 1
        #if TCP_SYNACK_reply and TCP_SYNACK_reply[TCP].flags == 18:
        #    print "\nPort " + self.port_dst + " is OPEN on host " + self.dst
        #    return 0
        s = socket.socket()
        return os.strerror(s.connect_ex((self.dst, self.port_dst)))

class AnotesModel(object):
    def __init__(self):
        self.state=0
        self.contacts={}
        self.cantContact=0
        self.server=ReceptAnotes()
        self.server_message_thread=None
        self.hostname=socket.gethostname()

    def getContact(self,id):
        return self.contacts[id]
    def getHostName(self):
        return self.hostname

    def addContact(self,ip,port):
        patner = ClientAnotes();
        patner.setPort(port)
        patner.setServer(ip)
        self.cantContact = self.cantContact + 1
        self.contacts[ip]=patner

    def sendMessageToPatner(self,ip,message):
        scan=PortScan()
        scan.setPortDst(24837)
        scan.setIpDst(ip)
        value=scan.scan_service()
        if (value==0):
            patner=self.getContact(ip)
            print str(patner)
            patner.setHostName(self.hostname)
            patner.setMessage(message)
            patner.send()
            return 0
        else:
            return value

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

