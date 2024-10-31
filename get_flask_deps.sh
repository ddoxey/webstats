#!/bin/bash
##
# Python-Flask dependencies on Centos 8
##

declare -A has_for
has_for["Flask-SocketIO"]="3f7ef81fee05be6b674521bd5850676bb2021897"
has_for["python-socketio"]="11b6f1a08d4840cc2f20a644bd9db7d5d95496bf"
has_for["python-engineio"]="28fe975daf239a2612e59843f06c52a72cfea84b"
has_for["bidict"]="a38d51e4b559be0b82faefdfa6677788cfcd92fb"
has_for["gevent-websocket"]="35cba7aa107f183acfc954b713718b3630509e8a"

for url in https://github.com/miguelgrinberg/Flask-SocketIO.git  \
           https://github.com/miguelgrinberg/python-socketio.git \
           https://github.com/miguelgrinberg/python-engineio.git \
           https://github.com/jab/bidict.git                     \
           https://gitlab.com/noppo/gevent-websocket.git
do
    if git clone "$url"
    then
        dir="$(awk -F'[./]' '{print $(NF-1)}' <<< "$url")"
        if [[ -d "$dir" ]]
        then
            if cd "$dir"
            then
                echo git checkout "${has_for[${dir}]}"
                cd ..
            fi
        fi
    fi
done
