#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import time
import subprocess
import phone
from dingding import DingDing
	
	
CAMMAND_GIT_CONFIG_ACCESS_TOKEN = "git config --global pushconfig.accesstoken" #连接gitlab的 token

ding = None

def main():
	print "main"
	
	
def setup():
	global ding
	if ding:
		return;
		
	access_token = get_access_token()
	if len(access_token)<=0:
		print "未设置钉钉群的access_token,无法启用钉钉功能"
		return
	
	ding = DingDing(access_token)

def sendToDingDing(reviewer, mrUrl, msg="", sender="",icon=""):
	#延时下 把消息置顶
	time.sleep(0.5)
	
	setup()
	
	if not ding:
		print "钉钉初始化失败"
		return
	if not reviewer:
		print "未指定reviewer人,不发送机器人消息"
		return;	
	if not mrUrl:
		print "merge request链接不存在,不发送机器人消息"
		return;	
	if reviewer == sender:
		print "指定reviewer的人是自己,不发送钉钉消息"
		return
	
	print "发送消息给钉钉好友"
	mobile = phone.phone_with_name(reviewer)
	
	print reviewer+"的手机号是:"+mobile
	title = reviewer+":"+sender+"向你发了一个merge request"
	text = msg
	message_url = mrUrl;
	pic_url = icon

	result1 = ding.send_link(title, text, message_url, pic_url)
	print result1
	result2 = ding.send_text(text="点击链接查看",at_mobiles=[mobile])
	print result2

def get_access_token():
	return cammand_out_put(CAMMAND_GIT_CONFIG_ACCESS_TOKEN,False,"")


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
