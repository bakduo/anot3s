#!/usr/bin/python

'''
#############################################################################
#                                                                           #
#   gui.py                                                                  #
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
import gtk
import time
import os
import sys
from modules.AnotesModel import AnotesModel

class SystrayIconApp:
  def __init__(self,gui):
    self.tray = gtk.StatusIcon()
    self.tray.set_from_stock(gtk.STOCK_DND) 
    self.tray.connect('popup-menu', self.on_right_click)
    self.tray.set_tooltip(('Anotes GPL'))
    self.guiApp = gui
    self.guiApp.setTray(self.tray)
		
  def on_right_click(self, icon, event_button, event_time):
    self.make_menu(event_button, event_time)
  def make_menu(self, event_button, event_time):
    menu = gtk.Menu()
    # show about dialog
    about = gtk.MenuItem("About")
    about.show()
    show_app = gtk.MenuItem("Show App")
    show_app.show()
    menu.append(about)
    menu.append(show_app)
    about.connect('activate', self.show_about_dialog)
    show_app.connect('activate',self.show_app_gui)
    # add quit item
    quit = gtk.MenuItem("Quit")
    quit.show()
    menu.append(quit)
    quit.connect('activate', self.salirApp)
    menu.popup(None, None, gtk.status_icon_position_menu,event_button, event_time, self.tray)

  def  show_about_dialog(self, widget):
    about_dialog = gtk.AboutDialog()
    about_dialog.set_destroy_with_parent (True)
    about_dialog.set_icon_name ("SystrayIcon")
    about_dialog.set_name('Anotes GPL')
    about_dialog.set_version('0.1')
    about_dialog.set_copyright("(C) 2014 linuxknow, (C) 2010 <joao.pinto@getdeb.net>")
    about_dialog.set_comments(("Version Libre de anotes permite enviar notas por red"))
    about_dialog.set_authors(['Linuxknow <linuxknow@gmail.com>','Joao <joao.pinto@getdeb.net>'])
    about_dialog.run()
    about_dialog.destroy()

  def show_app_gui(self,widget):
    self.guiApp.show()

  def salirApp(self,widget):
    self.guiApp.salir(widget)
    gtk.main_quit()

class AnotesGui(object):
  def __init__(self,model):
    # Cargamos el constructor de gtk y lo llamamos builder
    if model is None:
      self.model=AnotesModel()
    else:
      self.model=model
    
    self.tray=None
    self.guiContact = gtk.Builder()
    path=os.path.dirname(os.path.realpath(__file__))
    self.guiContact.add_from_file(path+"/add-contact-gui.glade")
    self.guiContact.connect_signals({
    "commitContact" : self.addContact,
    "backMenu" : self.backMainMenu,
    })

    self.guiMessage = gtk.Builder()
    self.guiMessage.add_from_file(path+"/gui-message.glade")
    self.guiMessage.connect_signals({
    "sendMessage" : self.sendMessage,
    "backMenu" : self.backMenu,
    })

    self.messageWindow = self.guiMessage.get_object("dialog1")
    self.messageWindow.set_size_request(320, 140)
    self.messageWindow.set_title("Anotes Message")

    self.contactWindow = self.guiContact.get_object("dialog1")
    self.contactWindow.set_size_request(200, 80)
    self.contactWindow.set_title("Anotes Contact")

    self.builder = gtk.Builder()
    self.builder.add_from_file(path+"/anotes-gtk.glade")
    # Conectamos signal de cerrar ventana
    self.builder.connect_signals({
    "exitApp" : self.salir,
    "enabledServer" : self.enabledServer,
    "addContact" : self.contactGui,
    "sendMessage" : self.messageGui,
    "hideWindow": self.hide
    })

    self.combo = self.builder.get_object("combobox1")
    self.loadIps()
    self.window = self.builder.get_object("window1")
    self.window.set_size_request(440, 280)
    self.window.set_title("Anotes GPL")
    self.window.show()

  def setTray(self,tray):
    self.tray=tray
  def salirApp(self):
    self.model.close_server()
    gtk.main_quit()
  def salir(self,evento):
    if self.tray is not None:
       self.model.close_server()
       gtk.main_quit()

  def addStoreInCombo(self):
    cell=gtk.CellRendererText()
    self.combo.pack_start(cell, True)
    self.combo.set_model(self.store)
    self.combo.set_active(0)
    self.combo.add_attribute(cell, 'text',1)

  def getStore(self):
    return gtk.ListStore(int,str)

  def loadIps(self):
    self.store = self.getStore()
    path=os.path.dirname(os.path.realpath(__file__))
    try:
        if os.path.isfile(path+'/ips.txt'):
            f = open(path+'/ips.txt','r')
            string = ""
            pos=0
            while 1:
                line = f.readline()
                if not line:break
                self.store.append([pos,line])
                self.model.addContact(line,24837)
                pos=pos + 1
            f.close()
            self.model.setCantContact(pos)
            self.addStoreInCombo()
        else:
            f = open(path+'/ips.txt','w')
            self.addStoreInCombo()
            self.model.setCantContact(0)
            f.close()
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        print "Unexpected error:", sys.exc_info()[0]

  def addContact(self,evento):
    print "Agrega un contacto"
    entry_texto=self.guiContact.get_object("entry1")
    self.store.append([self.model.getCantContact(),entry_texto.get_text()])
    path=os.path.dirname(os.path.realpath(__file__))
    f = open(path+'/ips.txt','a')
    print entry_texto.get_text()+str("\n")
    f.write(entry_texto.get_text()+str("\n"))
    f.close()
    self.model.addContact(entry_texto.get_text(),24837)
    entry_texto.set_text("")
    
  def messageGui(self,evento):
    print "Abriendo popup"
    self.window.hide()
    self.messageWindow.show()

  def contactGui(self,evento):
    print "Abriendo agregar contacto"
    self.window.hide()
    self.contactWindow.show()

  def sendMessage(self,evento):
    model = self.combo.get_model()
    index = self.combo.get_active()
    if (index > 0):
        valor_ip = model[index][1]# id 0 es indice id 1 contenido
        texto_item=self.guiMessage.get_object("textview1")
        buffer_text = texto_item.get_buffer()
        self.model.sendMessageToPatner(str(valor_ip),str(buffer_text.get_text(buffer_text.get_start_iter(),buffer_text.get_end_iter())))
        buffer_text.set_text("")

  def backMenu(self,evento):
    print "volviendo al menu"
    self.messageWindow.hide()
    self.window.show()

  def backMainMenu(self,evento):
    print "Volviendo al menu gral"
    self.contactWindow.hide()
    self.window.show()

  def enabledServer(self,evento):
    boton=self.builder.get_object("button1")
    boton.hide()
    self.model.runServer()

  def disabledClickServer(self,evento):
    self.model.setEventServer(False)
    print "disabled run server click"
  def show(self):
    self.window.show()
  def hide(self,evento):
    self.window.hide()


def main():
  p = optparse.OptionParser()
  p.add_option('--console', '-c', default="false")
  options, arguments = p.parse_args()
  model=AnotesModel()
  if options.console=="true":
     print options.console
     #model.loadConfig(options.console)
  else:
     app = AnotesGui(model)
     SystrayIconApp(app)
     gtk.main()

if __name__ == "__main__":
  main()

