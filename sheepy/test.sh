#!/bin/dash

i='!'
while test $i != '!!!!!!'
do
    j='!'
    while test $j != '!!!!!!'
    do
        echo -n ". "
        j="!$j"
    done
    echo
    i="!$i"
done

for file in *.txt
do
    if test -f "$file"
    then
        dos2unix "$file"
    fi
done