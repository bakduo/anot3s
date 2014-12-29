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
from Client import ClientAnotes

class ShowMessage():
    def __init__(self,address,msj,nombre):
    	  #ip="%s:%d" % (address)
        #self.address = ip.split(':')[0]#self.client.getpeername()#str(address)
        self.address = address
        self.size = 8096
        self.TCPPORT=24838
        self.msj = msj
        self.nombre = nombre
        self.guiResponse = gtk.Builder()
        self.path=os.path.dirname(os.path.realpath(__file__))
        self.guiMessage = gtk.Builder()
        self.guiMessage.add_from_file(self.path+"/../gui-message.glade")
        self.guiMessage.connect_signals({
        "sendMessage" : self.sendMessage,
        "backMenu" : self.backMenu,
        "backMenuClose": self.backMenuClose
        })
        self.messageWindow = self.guiMessage.get_object("window1")
        self.messageWindow.set_size_request(424, 240)
        self.messageWindow.set_resizable(False)
        self.messageWindow.set_title("Anotes Message")
        self.guiResponse = gtk.Builder()
        self.guiResponse.add_from_file(self.path+"/../gui-answer.glade")
        self.guiResponse.connect_signals({
        "sendResponse" : self.sendResponse,
        "closeResponse" : self.hideResponse
        })
        
        self.messageWindow.connect('delete_event', gtk.main_quit)
        self.messageWindow.connect('destroy', self.backMenu)


        self.responseWindow = self.guiResponse.get_object("window1")
        self.responseWindow.connect('delete_event', gtk.main_quit)
        self.responseWindow.connect('destroy', self.hideResponse)
        self.responseWindow.set_size_request(352, 230)
        self.responseWindow.set_resizable(False)
        self.responseWindow.set_title("Anotes Message Response")
        self.hostRemote = self.guiResponse.get_object("label1")
        self.textResponse=self.guiResponse.get_object("textview1")
        self.messageResponse = ""

    def sendMessage(self,evento):
        texto_item=self.guiMessage.get_object("textview1")
        buffer_text = texto_item.get_buffer()
        self.messageResponse = str(buffer_text.get_text(buffer_text.get_start_iter(),buffer_text.get_end_iter()))
        patner = ClientAnotes()
        patner.setPort(self.TCPPORT)
        patner.setServer(self.address)
        patner.setHostName(self.nombre)
        print "Mensaje respuesta: %s" % self.messageResponse
        patner.setMessage(str(self.messageResponse))
        respuesta_code = patner.send()
        if (respuesta_code!=0):
            newenv = os.environ.copy()
            newenv['anotes_message_thread'] = 'True'
            valor = "Error al tratar de enviar el mensaje de respuesta %s " % respuesta_code
            args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",valor]
            proc = subprocess.Popen(args, env=newenv)
            print "Pid envio de mensaje: %s\n" % proc.pid
        self.messageWindow.hide()
        gtk.main_quit()

    def setTextResponse(self,texto):
        buffer_text = self.textResponse.get_property('buffer')
        i = buffer_text.get_end_iter()
        buffer_text.insert(i, texto)
        #self.textResponse.set_text(str(texto))

    def setTextHostRemote(self,texto):
        try:
            self.hostRemote.set_text(texto)
        except:
            print "Error al generar ip"

    def showResponse(self,msj,host):
        self.setTextResponse(str(msj))
        self.setTextHostRemote(host)
        self.responseWindow.show()
        gtk.main()

    def hideResponse(self,evento):
        self.setTextResponse('')
        self.setTextHostRemote('')
        gtk.main_quit()
        #self.responseWindow.hide()
        #self.messageWindow.hide()


    def backMenu(self,evento):
        print "volviendo al menu"
        self.messageWindow.hide()
        self.responseWindow.show()

    def backMenuClose(self,evento,evento2):
        print "volviendo al menu"
        self.messageWindow.hide()
        self.responseWindow.show()

    def sendResponse(self,evento):
        self.messageWindow.show()

    def run(self):
        self.showResponse(self.msj,self.address)

def main():
   msj = ''
   address = ''
   nombre = ''
   try:
      if len(sys.argv) < 3:
          print 'Por ahora solo permite 3 argumentos atnotes -s server -p port'
          return 2
      opts, args = getopt.getopt(sys.argv[1:],"hm:c:n:")

   except getopt.GetoptError:
      print 'ShowMessage.py -m <message> -c <address> -n <nombre>'
      return 2
   for opt, arg in opts:
      print " %s : %s" % (opt,arg)
      if opt == '-h':
         print 'ShowMessage.py -m <message> -c <address> -n <nombre>'
         sys.exit()
      elif opt in ("-m"):
         msj = str(arg)
      elif opt in ("-c", "--client"):
         address = str(arg)
      elif opt in ("-n"):
         nombre = str(arg)

   smsj = ShowMessage(address,msj,nombre)
   smsj.run()
   gtk.main()
   return 0

if __name__ == '__main__':
   status = main()
   sys.exit(status)