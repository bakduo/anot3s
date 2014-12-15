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
import gobject
import gtk
import time
import os
import shutil
import sys
import subprocess
from modules.AnotesModel import AnotesModel

COLUMN_TEXT=0

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


def foreach(model, path, iter, selected):
    selected.append(model.get_value(iter, COLUMN_TEXT))

class AnotesGui(object):
  def __init__(self,model):
    # Cargamos el constructor de gtk y lo llamamos builder
    if model is None:
      self.model=AnotesModel()
    else:
      self.model=model
    
    self.tray=None
    self.enabledFileAttach=-1
    self.multipleEnabled=False
    self.envioMultiple=[]
    self.modelSelection = gtk.ListStore(gobject.TYPE_STRING)
    self.guiContact = gtk.Builder()
    path=os.path.dirname(os.path.realpath(__file__))
    self.guiContact.add_from_file(path+"/add-contact-gui.glade")
    self.guiContact.connect_signals({
    "commitContact" : self.addContact,
    "backMenu" : self.backMainMenu
    })
    self.guiAdjunto = gtk.Builder()
    self.guiAdjunto.add_from_file(path+"/gui-adjunto.glade")
    self.guiAdjunto.connect_signals({
    "setAdjunto": self.setAdjunto,
    "sendFile": self.sendAdjunto,
    "hideAdjunto": self.backAdjunto
    })
    self.guiMessage = gtk.Builder()
    self.guiMessage.add_from_file(path+"/gui-message.glade")
    self.guiMessage.connect_signals({
    "sendMessage" : self.sendMessage,
    "backMenu" : self.backMenu,
    "backMenuClose": self.backMenuClose
    })

    self.messageWindow = self.guiMessage.get_object("window1")
    self.messageWindow.set_size_request(424, 240)
    self.messageWindow.set_title("Anotes Message")

    self.contactWindow = self.guiContact.get_object("dialog1")
    self.contactWindow.set_size_request(200, 80)
    self.contactWindow.set_title("Anotes Contact")
    
    self.adjuntoWindow = self.guiAdjunto.get_object("dialog1")
    self.adjuntoWindow.set_size_request(200, 80)
    self.adjuntoWindow.set_title("Anotes agregar adjunto")

    self.builder = gtk.Builder()
    self.builder.add_from_file(path+"/anotes-gtk.glade")
    # Conectamos signal de cerrar ventana
    self.builder.connect_signals({
    "exitApp" : self.salir,
    "exitAppSalir": self.salirExit,
    "enabledServer" : self.enabledServer,
    "addContact" : self.contactGui,
    "sendMessage" : self.messageGui,
    "hideWindow": self.hide,
    "seleccionDestino": self.seleccionGui,
    "showAdjunto": self.adjuntoGui
    })

    self.hostlabel = self.builder.get_object("label1")
    self.hostlabel.set_text(self.model.getHostName())

    self.combo = self.builder.get_object("combobox1")
    self.loadIps()
    self.window = self.builder.get_object("window1")
    self.window.set_size_request(440, 280)
    self.window.set_title("Anotes GPL")
    self.window.show()

    self.treeview = gtk.TreeView(self.modelSelection)
    self.treeview.set_rules_hint(gtk.TRUE)
    column = gtk.TreeViewColumn('Destinos', gtk.CellRendererText(),text=COLUMN_TEXT)
    self.treeview.append_column(column)
    self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    self.windowSelection = gtk.Window()
    #self.windowSelection.connect("hideSelection", self.hideSelection())
    self.windowSelection.set_title('Seleccion multiple anotes')
    self.windowSelection.set_border_width(8)
    self.vbox = gtk.VBox(gtk.FALSE, 8)
    self.windowSelection.add(self.vbox)
    labelSelection = gtk.Label('Seleccione los destinos del mensaje')
    self.vbox.pack_start(labelSelection, gtk.FALSE, gtk.FALSE)
    self.sw = gtk.ScrolledWindow()
    self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    self.sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    self.vbox.pack_start(self.sw)
    self.sw.add(self.treeview)
    self.windowSelection.set_default_size(280, 250)

    self.buttonSelection = gtk.Button('OK')
    #self.button.show()
    self.buttonSelection.connect("clicked",self.ok_selection)
    self.vbox.pack_end(self.buttonSelection,gtk.FALSE)

  def ok_selection(self,event):
    self.windowSelection.hide();
    self.envioMultiple = []
    self.treeview.get_selection().selected_foreach(foreach, self.envioMultiple)
    print 'seleccionados: ...', self.envioMultiple
    print len(self.envioMultiple)
    self.multipleEnabled=True
    self.window.hide()
    self.messageWindow.show()
  def setTray(self,tray):
    self.tray=tray
  def salirApp(self):
    self.model.close_server()
    gtk.main_quit()

  def salir(self,evento):
    if self.tray is not None:
       self.model.close_server()
       gtk.main_quit()

  def salirExit(self,evento,evento2):
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
           orig = open(path+'/ips.txt','r')
           dest = open(path+'/ips-clean.txt', "w")
           uniquelines = set(orig.read().split("\n"))
           for line in uniquelines:
              #f2.write("".join([line + "\n" for line in uniquelines]))
              if line != '':
                 dest.write("".join([line + "\n"]))
           dest.close()
           orig.close()
        shutil.copy(path+'/ips-clean.txt', path+'/ips.txt')

        if os.path.isfile(path+'/ips.txt'):
            f = open(path+'/ips.txt','r')
            string = ""
            pos=0
            while 1:
                line = f.readline()
                if not line:break
                self.store.append([pos,line.rstrip('\n')])
                self.model.addContact(line.rstrip('\n'),24837)
                iter = self.modelSelection.append()
                self.modelSelection.set(iter, COLUMN_TEXT, line.rstrip('\n'))
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
  def setAdjunto(self,evento):
    print "setadjunto"
    dialog = gtk.FileChooserDialog("Open..",None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    filter = gtk.FileFilter()
    filter.set_name("All files")
    filter.add_pattern("*")
    dialog.add_filter(filter)
    filter = gtk.FileFilter()
    filter.add_pattern("*.*")
    dialog.add_filter(filter)
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
       print dialog.get_filename(), 'selected\n'
       self.enabledFileAttach = 0
       self.model.setAdjunto(dialog.get_filename(),os.path.basename(dialog.get_filename()))
       #print os.path.basename(dialog.get_filename())
    elif response == gtk.RESPONSE_CANCEL:
       print 'Closed, no files selected'
       self.enabledFileAttach = -1
    dialog.destroy()

  def sendAdjunto(self,evento):
    print "Enviando ..."
    model = self.combo.get_model()
    index = self.combo.get_active()
    print index
    if (index >= 0 and self.multipleEnabled==False and self.enabledFileAttach==0):
        valor_ip = model[index][1]# id 0 es indice id 1 contenido
        print valor_ip
        valor=self.model.sendFileToPatner(str(valor_ip))
        if (valor==0):
            print "enviado"
            mensaje_transfer="Enviado con exito %s." % self.model.getNombreArchivoAdjunto()
            newenv = os.environ.copy()
            newenv['anotes_message'] = 'True'
            args = ['/usr/bin/gxmessage','-bg','black','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes transfirio Ok",mensaje_transfer]
            proc = subprocess.Popen(args, env=newenv)
        else:
             newenv = os.environ.copy()
             newenv['anotes_message'] = 'True'
             args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",str(valor)]
             proc = subprocess.Popen(args, env=newenv)
        self.adjuntoWindow.hide()
        self.window.show()
    elif (len(self.envioMultiple)>0):
        for ip in self.envioMultiple:
          print "Enviar a : %s" %ip
          valor=self.model.sendFileToPatner(str(ip))
          if (valor==0):
             print "enviado"
          else:
             newenv = os.environ.copy()
             newenv['anotes_message'] = 'True'
             args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",str(valor)]
             proc = subprocess.Popen(args, env=newenv)
        self.multipleEnabled=False
        self.adjuntoWindow.hide()
        self.window.show()
    else:
        args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",str('Debe seleccionar un destino y un archivo')]

    
  def addContact(self,evento):
    print "Agrega un contacto"
    entry_texto=self.guiContact.get_object("entry1")
    existe = self.model.getContact(entry_texto.get_text())
    print existe
    if existe is None:
       self.store.append([self.model.getCantContact(),entry_texto.get_text()])
       iter = self.modelSelection.append()
       self.modelSelection.set(iter, COLUMN_TEXT, entry_texto.get_text())
       path=os.path.dirname(os.path.realpath(__file__))
       f = open(path+'/ips.txt','a')
       print entry_texto.get_text()+str("\n")
       f.write(entry_texto.get_text()+str("\n"))
       f.close()
       self.model.addContact(entry_texto.get_text(),24837)
       entry_texto.set_text("")
    else:
       newenv = os.environ.copy()
       newenv['anotes_message'] = 'True'
       args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes aviso",str('La ip esta duplicada')]
       proc = subprocess.Popen(args, env=newenv)
 
    
  def messageGui(self,evento):
    print "Abriendo popup"
    self.window.hide()
    self.messageWindow.show()

  def contactGui(self,evento):
    print "Abriendo agregar contacto"
    self.window.hide()
    self.contactWindow.show()
    
  def adjuntoGui(self,evento):
    print "Abriendo adjuntogui"
    self.window.hide()
    self.adjuntoWindow.show()

  def seleccionGui(self,evento):
    # self.buttonSelection.show()
    self.multipleEnabled=True
    self.windowSelection.show_all()

  # when you click ok, call this function for each selected item
  def foreach(model, path, iter, selected):
    selected.append(model.get_value(iter, COLUMN_TEXT))

  def sendMessage(self,evento):
    model = self.combo.get_model()
    index = self.combo.get_active()
    if (index >= 0 and self.multipleEnabled==False):
        valor_ip = model[index][1]# id 0 es indice id 1 contenido
        texto_item=self.guiMessage.get_object("textview1")
        buffer_text = texto_item.get_buffer()
        valor=self.model.sendMessageToPatner(str(valor_ip),str(buffer_text.get_text(buffer_text.get_start_iter(),buffer_text.get_end_iter())))
        if (valor==0):
            print "enviado"
        else:
             newenv = os.environ.copy()
             newenv['anotes_message'] = 'True'
             args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",str(valor)]
             proc = subprocess.Popen(args, env=newenv)

        buffer_text.set_text("")
        self.messageWindow.hide()
        self.window.show()
    elif (len(self.envioMultiple)>0):
        for ip in self.envioMultiple:
          print "Enviar a : %s" %ip
          texto_item=self.guiMessage.get_object("textview1")
          buffer_text = texto_item.get_buffer()
          valor=self.model.sendMessageToPatner(ip,str(buffer_text.get_text(buffer_text.get_start_iter(),buffer_text.get_end_iter())))
          if (valor==0):
             print "enviado"
          else:
             newenv = os.environ.copy()
             newenv['anotes_message'] = 'True'
             args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",str(valor)]
             proc = subprocess.Popen(args, env=newenv)
             
        buffer_text.set_text("")
        self.multipleEnabled=False
        self.messageWindow.hide()
        self.window.show()
    else:
        #print "Error"
        args = ['/usr/bin/gxmessage','-bg','red','-fg','white','-noescape','-buttons','cerrar','-wrap','-geometry','220x80','-sticky', '-ontop', '-title',"Anotes Error",str('Debe seleccionar un destino')]


  def backMenu(self,evento):
    print "volviendo al menu"
    self.messageWindow.hide()
    #self.guiMessage.hide()
    self.window.show()

  def backMenuClose(self,evento,evento2):
    print "volviendo al menu"
    self.messageWindow.hide()
    #self.guiMessage.hide()
    self.window.show()

  def backMainMenu(self,evento):
    print "Volviendo al menu gral"
    self.contactWindow.hide()
    self.window.show()
    
  def backAdjunto(self,evento):
    print "Volviendo al menu gral"
    self.adjuntoWindow.hide()
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

