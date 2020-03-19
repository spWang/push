#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import subprocess
import time
from biplist import *

REVIEWER_FILE = "reviewer.plist"

def main():
	print "main"
	print reviewer_with_name(unicode("王帅朋","utf-8"))
	print "结束"

	
def reviewer_with_name(name):
	
	if not name:
		return name

	plist = reviewer_plist()
	try:
		return plist[name]
	except(KeyError, Exception),e:
		return name

def reviewer_plist():
	reviewer_path = current_path()+REVIEWER_FILE
	
	if not (os.path.exists(reviewer_path) and os.path.isfile(reviewer_path)):
		print "reviewer.plist不存在"
		return None

	try:
		return readPlist(reviewer_path)
	except (InvalidPlistException, NotBinaryPlistException), e:
		print reviewer_path+"不是plist文件,无法读取"
		print e
		return None
		
def current_path():
	currentPath = os.path.realpath(__file__);
	fileName = os.path.basename(__file__);
	return currentPath.replace(fileName,"");
	
if __name__ == "__main__":
	main()
