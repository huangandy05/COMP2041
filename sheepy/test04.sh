#!/bin/dash

# Combine test, [] and external command in if statement
number=1
file='sheepy.py'
if [ 1 -lt 3 ] || test -r dev/null || fgrep -x -q $number $file
then
    echo "great"
fi
