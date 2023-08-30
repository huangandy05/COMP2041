#!/bin/dash

## For loop edge cases
# Glob, var, glob
for i in *.py cbsss *.py $# "a string"
do
    echo -n "$i "
done