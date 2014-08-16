#!/bin/bash

if [ $UID -eq 0 ];then
 echo "Proceeding"
 mkdir -p /opt/atnot3s/
 cp -r * /opt/atnot3s/
 chmod -R 755 /opt/atnot3s/
 if [ ! -e /usr/bin/execAnot3s ];then
  ln -s /opt/atnot3s/execAnot3s /usr/bin/execAnot3s 2>/dev/null 2>&1
 fi
 if [ -x /usr/bin/gxmessage ];then
   install --mode=755 anot3s.desktop /usr/share/applications/
   gxmessage "En hora buena usted instalo atnot3e GPL"
 else
   echo "Debe instalar gxmessage: apt-get install gxmessage"
 fi
else
   echo "Requiere permisos de root para instalar"
fi

