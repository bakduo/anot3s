#!/bin/bash

if [ $UID -eq 0 ];then
 echo "Proceeding"
 install --mode=755 * /opt/atnot3s/
 ln -s /opt/atnot3s/execAnot3s /usr/bin/execAnot3s
 install --mode=755 anot3s.desktop /usr/share/applications/
 gxmessage "En hora buena usted instalo atnot3e GPL"
else
    gxmessage "Requiere permisos de root para instalar"
fi

