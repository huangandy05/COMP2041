#!/bin/dash

# This file will contain all the wacky edge cases I accounted for

a='variable'
num=68
print='python keyword'

## echo commands
# Join double and single quote together
echo "'"'"'
# Join double and single quote together with variable substitution
echo "'$a'"'"'
# Spaces in double and single quotes
echo "empty   space"'   empty space at start'
# Fake comments in double and single qutoes
echo " # fake comment"   ' # another fake comment' # real comment
# Replacing python keyword
echo $print
# Echo with comma after keyword
echo "$print, hi"
# Empty echo 
echo
# Empty echo with comment
echo # comment
# This absolute monstrosity
echo " '' "$1' '$a,
# Absolute monstrosity inside double quotes
echo "$1$#$a,random var${a}`pwd`$(pwd)"
# Arithmetic expression
echo $((num + 1)) "$((num + 1))"
# Globbing inside double quotes and outside
echo *.py "*.py"


## For loop edge cases
# Glob, var, glob
for i in *.py cbsss *.py
do
    echo -n "$i "
done