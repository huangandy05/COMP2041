#!/usr/bin/env python3

import sys, subprocess, glob, os

def flatten_nested_array(arr):
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten_nested_array(item))
        else:
            result.append(item)
    return result

i = "!" 
while f"{i}" != "!!!!!!": 
	j = "!" 
	while f"{j}" != "!!!!!!": 
		print(". ", end="") 
		j = f"!{j}" 
	subprocess.run(['echo']) 
	i = f"!{i}" 

for file in flatten_nested_array([sorted(glob.glob('*.txt'))]): 
	if os.path.isfile(f"{file}"): 
		subprocess.run(['dos2unix', f'{file}']) 
