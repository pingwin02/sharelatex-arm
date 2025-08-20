#!/bin/bash
set -e

rm -rf ../overleaf

git clone https://github.com/overleaf/overleaf ../overleaf

cp -r ../server-ce/. ../overleaf/server-ce/

( cd ../overleaf/server-ce && make )