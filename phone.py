#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import subprocess
import time
from biplist import *

PHONE_FILE = "phone.plist"

def main():
	print "main"
	print phone_with_name("xxx")
	print "结束"

	
def phone_with_name(name):
	
	if not name:
		print "名字不存在"
		return ""
	plist = phone_plist()
	try:
		return plist[name]
	except(KeyError, Exception),e:
		print e
		return ""

def phone_plist():
	phone_path = current_path()+PHONE_FILE
	
	if not (os.path.exists(phone_path) and os.path.isfile(phone_path)):
		print "phone.plist不存在"
		return None

	if not check_file_is_plsit(phone_path):
		print phone_path+"不是plist文件,无法读取"
		return None
		
	return readPlist(phone_path)
	
def check_file_is_plsit(plist_path):
	try:
		plist = readPlist(plist_path)
		return True
	except (InvalidPlistException, NotBinaryPlistException), e:
		return False
		
def current_path():
	currentPath = os.path.realpath(__file__);
	fileName = os.path.basename(__file__);
	return currentPath.replace(fileName,"");
	
if __name__ == "__main__":
	main()