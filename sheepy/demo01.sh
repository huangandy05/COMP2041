#!/bin/bash

# Using echo with -n option
echo -n "Enter your name: "
read name # Using read to get user input
echo "Hello, $name!"

# Variable assignment with command-line args
file_name=$1 # Assigning the first command-line argument to a variable

# Comment after echo
echo "You provided the file name: $file_name" # This is a comment

# For loop with globbing, double quotes, and strings
echo "Listing all .txt files:"
for file in *.py fake_file
do
    echo "File found: $file" # Using double quotes inside echo
done

# Changing directory using cd
echo "Changing to home directory"
cd /tmp # Using cd to change directory
echo "Current directory: $(pwd)"

# Exit with a specific code
echo "Exiting with code 5"
exit 5 # Using exit to terminate the script
