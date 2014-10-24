#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

from pisi.actionsapi import cmaketools
from pisi.actionsapi import get
from pisi.actionsapi import pisitools


def setup():
    cmaketools.configure("-DCMAKE_BUILD_TYPE=release \
			  -DCMAKE_INSTALL_PREFIX=/usr \
			  -DUSE_QT5=OFF \
			  -DUSE_QTMIMETYPES=OFF \
			  -DCMAKE_INSTALL_LIBDIR=/usr/lib")

def build():
    cmaketools.make()

def install():
    cmaketools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("AUTHORS", "COPYING")
