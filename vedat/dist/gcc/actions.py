#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

import os


verMajor = "5.1.0"

arch = get.ARCH().replace("x86_64", "x86-64")

#opt_unwind = "--with-system-libunwind" if get.ARCH() == "x86_64" else "--without-system-libunwind"
opt_arch = "--with-arch_32=i686" if get.ARCH() == "x86_64" else "--with-arch=i686"
opt_multilib = "--enable-multilib" if get.ARCH() == "x86_64" else ""

# WARNING: even -fomit-frame-pointer may break the build, stack protector, fortify source etc. are off limits
cflags = "-O2 -g"


def removePisiLinuxSection(_dir):
    for root, dirs, files in os.walk(_dir):
        for name in files:
            # FIXME: should we do this only on nonshared or all ?
            # if ("crt" in name and name.endswith(".o")) or name.endswith("nonshared.a"):
            if ("crt" in name and name.endswith(".o")) or name.endswith(".a"):
                i = os.path.join(root, name)
                shelltools.system('objcopy -R ".comment.PISILINUX.OPTs" -R ".note.gnu.build-id" %s' % i)

def exportFlags():
    # we set real flags with new configure settings, these are just safe optimizations
    shelltools.export("CFLAGS", cflags)
    shelltools.export("CXXFLAGS", cflags)
    # shelltools.export("LDFLAGS", "")

    # FIXME: this may not be necessary for biarch
    shelltools.export("CC", "gcc")
    shelltools.export("CXX", "g++")
    shelltools.export("LC_ALL", "en_US.UTF-8")

def setup():
    exportFlags()
    # Maintainer mode off, do not force recreation of generated files
    #shelltools.system("contrib/gcc_update --touch")
    pisitools.dosed("gcc/Makefile.in", "\.\/fixinc\.sh", "-c true")
    pisitools.dosed("gcc/configure", "^(ac_cpp='\$CPP\s\$CPPFLAGS)", r"\1 -O2")
    pisitools.dosed("libiberty/configure", "^(ac_cpp='\$CPP\s\$CPPFLAGS)", r"\1 -O2")

    shelltools.cd("../")
    shelltools.makedirs("build")
    shelltools.cd("build")

    shelltools.system('.././gcc-%s/configure \
                       --with-system-zlib \
                       --with-bugurl=http://bugs.pisilinux.org \
                       --with-linker-hash-style=gnu \
                       --with-pkgversion="Pisi Linux" \
                       --with-multilib-list=m32,m64 \
                       --with-system-libunwind \
                       --with-gxx-include-dir=/usr/include/c++/4.9.2 \
                       --disable-libunwind-exceptions \
                       --disable-libstdcxx-pch \
                       --disable-libssp \
                       --disable-werror \
                       --disable-cloog-version-check \
                       --disable-libgcj \
                       --disable-build-poststage1-with-cxx \
                       --disable-build-with-cxx \
                       --enable-gnu-unique-object \
                       --enable-bootstrap \
                       --enable-__cxa_atexit \
                       --enable-libstdcxx-allocator=new \
                       --enable-java-awt="xlib,qt" \
                       --disable-libstdcxx-pch \
                       --enable-libstdcxx-threads \
                       --enable-libstdcxx-time=rt \
                       --enable-libstdcxx-visibility \
                       --enable-symvers=gnu \
                       --enable-languages=c,c++,fortran,lto,objc,obj-c++,java,go \
                       --enable-shared \
                       --enable-decimal-float \
                       --enable-gnu-unique-object \
                       --enable-gnu-indirect-function \
                       --enable-initfini-array \
                       --enable-threads=posix \
                       --enable-clocale=gnu \
                       --enable-linker-build-id \
                       --enable-cloog-backend=isl \
                       --enable-plugin \
                       --enable-checking=release \
                       --enable-c99 \
                       --enable-lto \
                       --enable-libitm \
                       --enable-linker-build-id \
                       --enable-linux-futex \
                       --enable-long-long \
                       --enable-nls \
                       --prefix=/usr \
                       --bindir=/usr/bin \
                       --libdir=/usr/lib \
                       --libexecdir=/usr/lib \
                       --includedir=/usr/include \
                       --mandir=/usr/share/man \
                       --infodir=/usr/share/info \
                       --x-libraries=/usr/lib/X11 \
                       --host=x86_64-pc-linux-gnu \
                       --build=x86_64-pc-linux-gnu \
                       --build=%s \
                               %s \
                               %s ' % ( verMajor , get.HOST(), opt_arch, opt_multilib))

def build():
    exportFlags()

    shelltools.cd("../build")
    autotools.make('BOOT_CFLAGS="%s" profiledbootstrap' % cflags)

def install():
    shelltools.cd("../build")
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    #autotools.install()

    for header in ["limits.h","syslimits.h"]:
        pisitools.insinto("/usr/lib/gcc/%s/%s/include" % (get.HOST(), verMajor) , "gcc/include-fixed/%s" % header)

    # Not needed
    pisitools.removeDir("/usr/lib/gcc/*/*/include-fixed")
    pisitools.removeDir("/usr/lib/gcc/*/*/install-tools")

    # This one comes with binutils
    #pisitools.remove("/usr/lib*/libiberty.a")

    # cc symlink
    pisitools.dosym("/usr/bin/gcc" , "/usr/bin/cc")

    # /lib/cpp symlink for legacy X11 stuff
    pisitools.dosym("/usr/bin/cpp", "/lib/cpp")

    # Remove our options section from crt stuff
    removePisiLinuxSection("%s/usr/lib/" % get.installDIR())
    if get.ARCH() == "x86_64":
        removePisiLinuxSection("%s/usr/lib32/" % get.installDIR())


    # autoload gdb pretty printers
    gdbpy_dir = "/usr/share/gdb/auto-load/usr/lib/"
    pisitools.dodir(gdbpy_dir)

    gdbpy_files = shelltools.ls("%s/usr/lib/libstdc++*gdb.py*" % get.installDIR())
    for i in gdbpy_files:
        pisitools.domove("/usr/lib/%s" % shelltools.baseName(i), gdbpy_dir)

    if arch == "x86-64":
        pisitools.remove("/usr/lib32/libstdc++*gdb.py*")

