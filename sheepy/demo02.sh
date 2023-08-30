#!/bin/bash

# Using ${} for variable assignment
filename="sheepy"
extension=".py"
full_filename=${filename}${extension} # Appending strings using ${}
echo "Full filename is: $full_filename"

# Test operators
# File operators
if [ -e "$full_filename" ]
then
    echo "File exists."
    if [ -f "$full_filename" ]
    then 
        echo "It's a regular file."
    fi
    if [ -d "$full_filename" ]
    then 
        echo "It's a directory."
    fi
    if [ -r "$full_filename" ]
    then 
        echo "File is readable."
    fi
    if [ -w "$full_filename" ]
    then 
        echo "File is writable."
    fi
    if [ -x "$full_filename" ]
    then 
        echo "File is executable."
    fi
    if [ -s "$full_filename" ]
    then 
        echo "File is not empty."
    fi
else
  echo "File does not exist."
fi

# String comparisons
str1="Hello"
str2="World"

if [ "$str1" = "$str2" ]
then
    echo "Strings are equal."
elif [ "$str1" != "$str2" ]
then
    echo "Strings are not equal."
fi

# Numeric comparisons
num1=10
num2=20

if [ $num1 -eq $num2 ]
then
    echo "Numbers are equal."
elif [ $num1 -ne $num2 ]
then
    echo "Numbers are not equal."
    if [ $num1 -lt $num2 ]
    then
        echo "$num1 is less than $num2"
    fi
    if [ $num1 -le $num2 ]
    then
        echo "$num1 is less than or equal to $num2"
    fi
    if [ $num1 -gt $num2 ]
    then
        echo "$num1 is greater than $num2"
    fi
    if [ $num1 -ge $num2 ]
    then
        echo "$num1 is greater than or equal to $num2"
    fi
fi

# While loop with nesting
count=1
while [ $count -le 3 ]
do
    echo "Outer loop: $count"
    inner_count=1
    while [ $inner_count -le 3 ]
    do
        echo "  Inner loop: $inner_count"
        inner_count=$((inner_count + 1))
    done
    count=$((count + 1))
done

# Using backticks
echo "Current directory is: `pwd`"
