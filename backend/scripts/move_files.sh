#!/bin/bash

cp files/* ../../../avyukd.github.io/files/
cd ../../../avyukd.github.io
git add .
git commit -m "[auto] new files added"
git push
cd ../stocks/uip/backend/scripts
