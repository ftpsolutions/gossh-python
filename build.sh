#!/bin/bash

which go 2>/dev/null 1>/dev/null
if [[ $? -ne 0 ]]; then
    echo "error: failed to find go binary- do you have Go 1.9 or Go 1.10 installed?"
    exit 1
fi

GOVERSION=`go version`
if [[ $GOVERSION != *"go1.9"* ]] && [[ $GOVERSION != *"go1.10"* ]]; then
    echo "error: Go version is not 1.9 or 1.10 (was $GOVERSION)"
    exit 1
fi

export GOPATH=`pwd`

export PYTHONPATH=`pwd`/src/github.com/go-python/gopy/

echo "cleaning up output folder"
rm -frv gosnmp_ssh/*.pyc
rm -frv gosnmp_ssh/py2/*.pyc
rm -frv gosnmp_ssh/py2/gossh_python.so
rm -frv gosnmp_ssh/cffi/*.pyc
rm -frv gosnmp_ssh/cffi/_gossh_python.so
rm -frv gosnmp_ssh/cffi/gossh_python.py
echo ""

if [[ "$1" != "fast" ]]; then
    echo "getting assert"
    go get -v -a github.com/stretchr/testify/assert
    echo ""

    echo "getting gossh"
    go get -v -a golang.org/x/crypto/ssh
    echo ""

    echo "building gossh"
    go build -a -x golang.org/x/crypto/ssh
    echo ""

    echo "getting gopy"
    go get -v -a github.com/go-python/gopy
    echo ""

    if [[ $GOVERSION == *"go1.10"* ]]; then
        echo "fix errant pkg-config call in gopy (because we're running Go1.10)"
        sed 's^//#cgo pkg-config: %\[2\]s --cflags --libs^//#cgo pkg-config: %\[2\]s^g' src/github.com/go-python/gopy/bind/gengo.go > temp.go
        mv temp.go src/github.com/go-python/gopy/bind/gengo.go
    fi

    echo "building gopy"
    go build -x -a github.com/go-python/gopy
    echo ""

    echo "building gosnmp_ssh"
    go build -x -a gosnmp_ssh
    echo ""
fi

echo "build gossh_python bindings for py2"
./gopy bind -lang="py2" -output="gossh_python/py2" -symbols=true -work=false gossh_python
echo ""

echo "build gossh_python bindings for cffi"
./gopy bind -lang="cffi" -output="gossh_python/cffi" -symbols=true -work=false gossh_python
echo ""

echo "fix broken cffi output (this is yuck)"
sed 's/py_kwd_011, \[\]int/py_kwd_011, list/g' gossh_python/cffi/gossh_python.py > temp.py
mv temp.py gossh_python/cffi/gossh_python.py
