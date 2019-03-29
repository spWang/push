#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import subprocess

reload(sys)  
sys.setdefaultencoding('utf8')

CAMMAND_PULL_TARGET_BRANCE = "git pull" #rebase拉代码


def main():
	updatejob()
	
def updatejob():
	print "开始检查升级"	
	#记录当前路径
	currentPath = os.getcwd()
	
	#切换到脚本仓库路径
	jobPath = os.path.realpath(__file__);
	fileName = __file__.split("/")[-1]
	jobRepoPath = jobPath.replace(fileName, '')
	os.chdir(jobRepoPath)
	
	#执行拉代码的操作
	print ("更新脚本:"+CAMMAND_PULL_TARGET_BRANCE)
	cammand_out_put(CAMMAND_PULL_TARGET_BRANCE, True, None)
	
	#切回当前路径
	os.chdir(currentPath)
	
	print "检查升级完毕"


def cammand_out_put(cammand, can_raise, raise_return_value):
	try:
		return subprocess.check_output(cammand, shell=True).strip()
		pass
	except subprocess.CalledProcessError as e:
		if can_raise:
			raise(e)
		else:
			return raise_return_value
			pass
	pass

if __name__ == "__main__":
	main()