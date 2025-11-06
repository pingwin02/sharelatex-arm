#!/bin/bash
set -e

rm -rf ../overleaf

if [[ "$1" == "clean" ]]; then
    docker system prune -af
    exit 0
fi

git clone https://github.com/overleaf/overleaf ../overleaf

read -p "Press enter to continue"

cp -r ../server-ce/. ../overleaf/server-ce/

( cd ../overleaf/server-ce && make )