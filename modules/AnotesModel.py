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
import psutil
import subprocess
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


class AnotesModel(object):
    def __init__(self):
        self.state=0
        self.contacts={}
        self.archivo = None
        self.nombreArchivo = None
        self.cantContact=0
        self.TCPPORTFILE = 24839
        self.server=ReceptAnotes()
        self.server_message_thread=None
        self.server_file_thread=None
        self.hostname=socket.gethostname()
        self.threads = []
        self.path=os.path.dirname(os.path.realpath(__file__))
        if os.path.isfile(self.path+'/../pid_enabled'):
            os.system("rm -rf "+str(self.path+'/../pid_enabled'));
        os.system("touch "+str(self.path+'/../pid_enabled'));

    def getContact(self,id):
        try:
            if (self.contacts[id]):
                return self.contacts[id]
            else:
                return None
        except KeyError:
            print "Key no existe"
            return None

    def getHostName(self):
        return self.hostname

    def addContact(self,ip,port):
        patner = ClientAnotes();
        patner.setPort(port)
        patner.setServer(ip)
        self.cantContact = self.cantContact + 1
        self.contacts[ip]=patner

    def sendFileToPatner(self,ip):
        patner=self.getContact(ip)
        if (self.archivo is not None):
            patner.setAttach(self.archivo,self.nombreArchivo)
            patner.setHostName(self.hostname)
            patner.setPortFile(self.TCPPORTFILE)
            retorno = patner.sendFile()
            #print "valor envio archivo : %s" % retorno
            if (retorno==0):
                mensaje="Archivo: %s se transfirio con exito." % self.nombreArchivo
                patner.setMessage(mensaje)
                patner.send()
                return 0
            else:
                return "Error de conexion en el vecino: %s" %(ip)
                     
    def sendMessageToPatner(self,ip,message):
        patner=self.getContact(ip)      
        patner.setHostName(self.hostname)
        patner.setMessage(message)
        if (patner.send()==0):
            return 0
        else:
            return "Error de conexion en el vecino: %s" %(ip)

    def setCantContact(self,cant):
       self.cantContact = cant

    def getCantContact(self):
       return self.cantContact

    def configServer(self,port,ip):
        if (self.server==None):
            self.server=ReceptAnotes()
        self.server.setPort(port)
        self.server.setIp(ip)

    def launchServer(self):
        self.server.run()

    def runServer(self):
        self.server.setServerNotesName(self.getHostName())
        self.server.run_command(self.getHostName())
        self.server.run_commandFile(self.getHostName())

    def stopServer(self):
        try:
            self.server.setState(1)
            print "Estado pids desde anotes: %s\n" % self.server.getPidsMessage()
            for c in self.threads:
                c.join()
            try:
                self.server.close_process()
            except:
                print "Error al realizar la llamada server.close_process()"
            #Si existen registros de aplicaciones se deben eliminar
            if os.path.isfile(self.path+'/../pid_enabled'):
                f = open(self.path+'/../pid_enabled','r')
                pid_program = f.readline()
                if (str(pid_program) != '' and pid_program != None and int(pid_program) > 0):
                    try:
                        print "Lectura pid: %s\n" % str(pid_program)
                        if psutil.pid_exists(int(pid_program)):
                            try:
                                os.system("kill -9 "+str(pid_program));
                            except OSError:
                                print "Error al eliminar con kill.\n"
                    except OSError:
                        print "Proceso %s no existe.\n" % (str(pid_program))
                    except psutil.NoSuchProcess:
                        print "Proceso no existe por medio de psutil\n"
                    except AccessDenied:
                        print "Acceso denegado el proceso.\n"
                    except TimeoutExpired:
                        print "Tiempo de espera agotado.\n"
            gtk.main_quit()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            e = sys.exc_info()[0]
            print( "<p>Error al salir del programa desde anotesmodel: %s</p>\n" % e)
            #print( "%s" % sys.exc_info())

    def close_server(self):
        self.stopServer()

    def setAdjunto(self,filesrc,nombre):
        self.archivo = filesrc
        self.nombreArchivo = nombre

    def getAdjunto(self):
        return self.archivo
    def getNombreArchivoAdjunto(self):
        return self.nombreArchivo
