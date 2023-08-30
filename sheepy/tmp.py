#!/usr/bin/env python3

import sys, subprocess, glob

def flatten_nested_array(arr):
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten_nested_array(item))
        else:
            result.append(item)
    return result

# This file will contain all the wacky edge cases I accounted for

a = "variable" 
num = "68" 
print_ = "python keyword" 

## echo commands
# Join double and single quote together
print("'\"") 
# Join double and single quote together with variable substitution
print(f"'{a}'\"") 
# Spaces in double and single quotes
print("empty   space   empty space at start") 
# Fake comments in double and single qutoes
print(" # fake comment  # another fake comment") # real comment
# Replacing python keyword
print(f"{print_}") 
# Echo with comma after keyword
print(f"{print_}, hi") 
# Empty echo
print()
# Empty echo with comment
print() # comment
# This absolute monstrosity
print(f" '' {sys.argv[1]} {a},") 
# Absolute monstrosity inside double quotes
print(f"{sys.argv[1]}{len(sys.argv[1:])}{a},random var{a}{subprocess.run(['pwd'], text=True, stdout=subprocess.PIPE).stdout.strip()}{subprocess.run(['pwd'], text=True, stdout=subprocess.PIPE).stdout.strip()}") 
# Arithmetic expression
print(f"{int(num) + 1} {int(num) + 1}") 
# Globbing inside double quotes and outside
print(f"{' '.join(sorted(glob.glob('*.py')))} *.py") 


## For loop edge cases
# Glob, var, glob
for i in flatten_nested_array([sorted(glob.glob('*.py')), 'cbsss', sorted(glob.glob('*.py'))]): 
	print(f"{i} ", end="") 
