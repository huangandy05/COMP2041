#!/bin/bash

# Variable assignment
name="World"
echo "Hello, $name!" # Using double quotes

# Usage of single quotes
echo 'Single quotes will not expand $name'

# Command-line arguments
echo "The script name is $0"
echo "The first argument is $1"

# Globbing
echo "Listing .txt files in the current directory:"
echo *.txt

# If statements
if [ -f "$1" ]
then
    echo "The first argument is a file!"
else
    echo "The first argument is not a file!"
fi

# For loops
echo "Listing arguments:"
for arg in "$@"
do
    echo "Argument: $arg"
done

# Nesting
echo "Nested for loops:"
for i in 1 2 3
do
    for j in a b c
    do
        echo "i: $i, j: $j"
    done
done

# Combining features
echo "If-else inside a loop:"
for file in *.txt
do
    if [ -f "$file" ]
    then
        echo "$file is a file."
    else
        echo "$file does not exist."
    fi
done
