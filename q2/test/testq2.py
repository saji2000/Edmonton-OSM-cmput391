'''
Checks the output of the solution for Q2
'''

import sys
import subprocess

import os
cwd = os.getcwd()


print ("testing Q2")

output = subprocess.check_output(["python3" , "q2.py", "../q1/edmonton.db", "651244271", "664182573"])
output = output.decode('utf-8')
lines = output.strip().split('\n')

if len(lines) > 1:
	print ("====> ERROR: the output has more lines than expected")
	exit(1)

if len(lines) == 0:
	print ("====> ERROR: there is no output")
	exit(1)

try:
	number = float(lines[0])
	print ("====> SUCCESS: output is formatted correctly")
except:
	if lines[0] != 'error':
		print ("====> ERROR: output does not look like a number")
		exit(1)

