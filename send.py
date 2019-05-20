#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import subprocess
from dingding import DingDing


def main():
	url = "bbb"
	sendToDingDing("xxx", url, "feat:test提交信息","xxx")
	
def sendToDingDing(reviewer, mrUrl, msg="", sender="",):
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
	access_token="0076d8f46623015061a159ca87071721e5cc821c7ebdb6718ebf64299abb5adc"
	ding = DingDing(access_token)
	phone = toMobileWithName(sender)
	
	title = sender+"向"+reviewer+"发了一个merge request请求"
	text = msg
	message_url = mrUrl;
	pic_url = ""

	result1 = ding.send_link(title, text, message_url, pic_url)
	result2 = ding.send_text(text="点击上边的链接查看",at_mobiles=phone)
	print result1,result2

def toMobileWithName(name):
	return ["12211"]


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