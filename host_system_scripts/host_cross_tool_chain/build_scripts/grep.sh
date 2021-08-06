#!/bin/bash
set -euo pipefail

unpack_src() {
    tar xf grep-3.6.tar.xz
    cd grep-3.6
    return
}

configure() {
    ./configure --prefix=/usr   \
                --host=$LFS_TGT \
                --bindir=/bin
    return
}

make_install() {
    make && make DESTDIR=$LFS install
    return
}

unpack_src && configure && make_install
