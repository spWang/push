#!/usr/bin/env python
# coding=utf-8
#
#https://python-gitlab.readthedocs.io/en/stable/api-usage.html

__Author__ = '王帅朋'
__Date__ = '2019-01-10'


import os
import re
import sys
import subprocess
import webbrowser
import gitlab
import datetime
import pjconfig
import update
import send
from xpinyin import Pinyin


#脚本输入参数(全局变量)
inputAssiness = None #外部输入指定的review的人
inputSourceBranch = None #外部输入指定的源分支
inputTargetBranch = None #外部输入指定的目标分支

VERSION = " 1.0.0"

#全局变量
gl = None
project = None
GLOBAL_BEFORE_PULL_FILE_LIST = []
GLOBAL_BRANCH_SOURCE = None

DEFAULT_BRANCH_TARGET = "dev" #默认的目标分支
ASSINESS = "" #代码写死review的人 优先级: 外部输入 > 代码写死 > 获取git配置的提交者

CAMMAND_GIT_REMOTE_URL = "git config remote.origin.url" #获取当前仓库的SSH 或者HTTP URL
CAMMAND_GIT_ADD_ALL  = "git add ." #暂存
CAMMAND_GIT_COMMIT_MSG  = "git commit -m" #提交代码
CAMMAND_CURRENT_LOCAL_BRANCHS  = "git branch -l" #查看本地分支
CAMMAND_REMOTE_BRANCHS  = "git branch -r" #查看远程分支
CAMMAND_PULL_TARGET_BRANCE = "git pull --rebase" #rebase拉代码
CAMMAND_FORCE_DELETE_LOCAL_BRANCH = "git branch -D" #强制删除本地分支
CAMMAND_DELETE_BRANCH_ORIGIN = "git push origin -d" #删除远程分支
CAMMAND_CHECKOUT_BRANCH = "git checkout -b" #创建并切换到某分支
CAMMAND_SWITCH_BRANCH = "git checkout" #切换到某分支
CAMMAND_PUSH_BRANCH = "git push origin" #把某分支推到远端
CAMMAND_LAST_MY_COMMITID = "git rev-parse HEAD" #获取最后一次的提交的ID
CAMMAND_GIT_REBASE_ABORT = "git rebase --abort" #rebase的时候有冲突产生
CAMMAND_GIT_FETCH = "git fetch -p" #抓取更新
CAMMAND_GIT_LOG = "git log" #获取某分支的提交信息
CAMMAND_GIT_RESET = "git reset" #重置代码后边需要加上ID
CAMMAND_GIT_STASH = "git stash save" #暂存代码
CAMMAND_GIT_STASH_LIST = "git stash list" #拉取所有暂存代码列表
CAMMAND_GIT_STASH_POP = "git stash pop" #恢复暂存代码
CAMMAND_GIT_STASH_DROP = "git stash drop" #删除暂存代码
CAMMAND_POD_INSTALL = "pod install" #pod install
CAMMAND_GIT_CONFIG_DELETE_TARGET_BRANCH = "git config --unset pushconfig.targetbranch"#删除本地配置的默认目标分支
CAMMAND_GIT_CONFIG_TARGET_BRANCH = "git config pushconfig.targetbranch" #本地配置默认目标分支
CAMMAND_GIT_CONFIG_MERGEREQUEST_IDS = "git config pushconfig.mrids" #记录mr的ID
CAMMAND_GIT_CONFIG_PROJECT_ID = "git config pushconfig.projectid" ##缓存项目的ID
CAMMAND_GIT_CONFIG_PRIVATE_TOKEN = "git config --global pushconfig.privatetoken" #连接gitlab的 token
CAMMAND_GIT_CONFIG_GITLAB_URL = "git config --global pushconfig.url" #连接gitlab的域名

MSG_NOCHANGE = "nothing to commit, working tree clean" #没有改动
MSG_CHANGE_NOTADD = "Changes not staged for commit:" #有改动 但未add
MSG_CHANGE_ADD = "Changes to be committed:" #有改动 且已add
MSG_PULL = "(use \"git pull\" to" #有待拉取
MSG_NEEDPUSH1 = "(use \"git push\" to publish your local commits)" #有待push,第一种情况 
MSG_NEEDPUSH2 = "have diverged," #有待push,第二种情况


reload(sys)  
sys.setdefaultencoding('utf8')

def test():
	print "\ntest打印-------------"
#	print current_login_user_name()
#	print current_path()
#	mark_count_of_files()
#	pod_install_if_need()
#	dateTime = datetime.datetime.now().strftime('%m-%d_%H:%M:%S')
#	print "源分支是:"+source_branch()
#	print "目标分支是:"+target_branch()
	print "test打印完毕-------------\n"

def main():

	#检查是否是git仓库和其他配置
	check_git_repo()

	print("目标分支是:"+target_branch()+"  源分支是:"+source_branch())

	#初始化配置
	setup()
	
	#TODO:  
#	test()
#	return
		
	#检查当前所在分支必须在target分支
	check_current_branch()
	
	#目标分支是否在远端存在
	originTargetExist = check_origin_target_exist()
	
	if originTargetExist:
		case_normal_merge_push()
	else:
		push_branch_target()
	pass
	
def check_git_repo():
	
	#是否是git仓库
	path = os.getcwd()+"/.git"
	print "当前路径是:"+os.getcwd()
	localTargetBranch = cammand_out_put(CAMMAND_GIT_CONFIG_TARGET_BRANCH, False, None)
	if localTargetBranch:
		print "本地配置的默认目标分支是:"+localTargetBranch+"如需修改删除请执行push -h查看操作"
		
	if not os.path.exists(path):
		print "请在git仓库根目录下使用此命令"
		exit(0)
		
	#校验远程仓库地址
	if not len(git_config_remote_url()):
		print ("❌❌❌没有远程仓库地址!!!\n请先执行如下命令配置本仓库远程仓库的地址")
		print CAMMAND_GIT_REMOTE_URL+" "+"xxx"
		exit(0)
			
		
	#校验URL
	if not gitlab_url():
		print ("❌❌❌没有域名!!!\n请先执行如下命令配置本仓库gitlab的http域名,例如http://gitlab.xxx.cn")
		print CAMMAND_GIT_CONFIG_GITLAB_URL+" "+"xxx"
		exit(0)
			
			
	#校验token
	if not private_token():
		print ("❌❌❌无法登录!!!\n请参考网址(https://blog.csdn.net/bing900713/article/details/80222188)获取gitlab token,并在git仓库下执行如下命令配置登录gitlab的token后重试(token权限全勾选)")
		print CAMMAND_GIT_CONFIG_PRIVATE_TOKEN+" "+"xxx"
		exit(0)
	
def setup():
	print "正在初始化..."
	
	print "连接gitlab"
	privateToken = private_token()
	gitlabUrl = gitlab_url()
	
	global gl
	gl = gitlab.Gitlab(gitlabUrl, private_token=privateToken, api_version=4, per_page=20)
	
	print "获取项目ID"
	projectID = project_ID()
	
	print "获取项目"
	global project
	project = gl.projects.get(projectID)	
	
	#认证当前用户
	gl.auth()
	
	print "初始化完毕"

def case_normal_merge_push():
	
	#代码状态
	status = git_status()
	
	#检查代码状态,不能push则会直接退出程序
	check_git_status(status)
	
	#计数文件总数
	mark_count_of_files()
		
	#拉代码
	conflict = pull_target_branch()
	
	#是否有冲突,走不同流程
	if conflict:
		case_conflict()
	else:
		case_no_conflict()
	pass

def case_conflict():
	print "代码有冲突,走冲突流程"
	#放弃变基
	give_up_rebase()
	
	#获取本地提交的commit数量
	commitCount = ahead_target_branch_commit()
	
	#拉取目标分支的提交log
	commitLogs = target_branch_commit()
	
	#reset代码和暂存代码
	stashTitleList = reset_and_stash(commitCount,commitLogs)
	
	#重新rebase拉代码
	pull_target_branch()
	
	#恢复暂存代码(恢复代码 add代码 提交代码 删除暂存代码)
	pop_stash_with_titles(stashTitleList)
	
	#提示手动解决冲突后,重新提交代码并且push
	print "⚠️ ⚠️ ⚠️ 请手动解决冲突后,再提交代码"

def case_no_conflict():
	print "走没有冲突流程"
	#当前分支直接push 或者走merge流程
	pushImmediacy = can_push_branch_target()
	if pushImmediacy:
		print("当前分支可以直接push代码")
		push_branch_target()
	else:
		print("当前分支需要走gitlab的merge流程")
		merge_branch_target()
	
	print("✅✅✅提交代码已经完成,开始做剩下额外的工作\n")

	#执行pod install 并且 #build项目
	pod_install_if_need()
	
	#删除已经被合并的远程分支
	delete_source_branch_when_merged()
	
	#更新类前缀和组织名
	pjconfig.setup_class_prefix_if_need()
	
	pass


def merge_branch_target():
	
	#校验review人是否正确
	check_assignee_id()
	
	#创建本地分支
	create_branch_source()
	
	#推送新分支
	push_branch_source()

	#创建合并请求
	mr =  create_merge_request()

	#发送钉钉消息提醒TA
	send_dingding(mr)

	#处理合并请求
	deal_merge_request(mr)
	
	#切换到目标分支
	switch_target_branch()
	
	#拉目标分支代码
	pull_target_branch()
	
	#删除本地source分支
	delete_branch_source()
	
	#执行git fetch
	git_fetch()

	#打开网页
	open_web_merge_request(mr)
			
	pass
	
	
def check_current_branch():
	if target_branch() != current_select_branch():
		print("❌❌❌必须在目标分支"+target_branch()+"上操作")
		exit(0)
		
def git_status():
	return cammand_out_put("git status", True, None)
		
def check_origin_target_exist():
	print("获取远端分支列表:"+CAMMAND_REMOTE_BRANCHS)
	remoteBranchs = cammand_out_put(CAMMAND_REMOTE_BRANCHS, True, None)
	oirginTargetBranch = "origin/"+target_branch()
	
	if oirginTargetBranch in remoteBranchs:
		print("远端分支{branch}存在".format(branch=target_branch()))
		return True
	else:
		print("远端分支{branch}不存在".format(branch=target_branch()))
		return False

def mark_count_of_files():
	global GLOBAL_BEFORE_PULL_FILE_LIST
	GLOBAL_BEFORE_PULL_FILE_LIST = module_files_list()
	print "记录下被统计目录文件列表"
def check_git_status(status):
	needPull = MSG_PULL in status
	noChange = MSG_NOCHANGE in status
	changeNotAdd = MSG_CHANGE_NOTADD in status
	changeDidAdd = MSG_CHANGE_ADD in status
	needPush = MSG_NEEDPUSH1 in status or MSG_NEEDPUSH2 in status
	
	#无拉 无改动 无提交(无push)
	'''
	On branch dev
	Your branch is up to date with 'origin/dev'.

	nothing to commit, working tree clean
	'''
	if not needPull and noChange and not needPush:
		print("⚠️ ⚠️ ⚠️ 不需要拉取代码,没有代码改动,不能push")
		exit(0)
	
	#无拉 有改动但未add 无提交(无push)
	'''
	On branch dev
	Your branch is up to date with 'origin/dev'.

	Changes not staged for commit:
		(use "git add <file>..." to update what will be committed)
		(use "git checkout -- <file>..." to discard changes in working directory)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m

	no changes added to commit (use "git add" and/or "git commit -a")
	'''
	if not needPull and changeNotAdd and not needPush:
		print("不需要拉取代码,有代码改动但未add,不能push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
	
	#无拉 有改动且add 无提交(无push)
	'''
	On branch dev
	Your branch is up to date with 'origin/dev'.

	Changes to be committed:
	  (use "git reset HEAD <file>..." to unstage)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m
	'''
	if not needPull and changeDidAdd and not needPush:
		print("不需要拉取代码,有代码改动且已经add,不能push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
	
	#无拉 无改动 有一个提交(待push)
	'''
	On branch dev
	Your branch is ahead of 'origin/dev' by 1 commit.
		(use "git push" to publish your local commits)

	nothing to commit, working tree clean
	'''
	if not needPull and noChange and needPush:
		print("不需要拉取代码,没代码改动,有已经提交的,可以push")
	
	#无拉 有改动未add 有一个提交(待push)
	'''
	On branch dev
	Your branch is ahead of 'origin/dev' by 1 commit.
		(use "git push" to publish your local commits)

	Changes not staged for commit:
		(use "git add <file>..." to update what will be committed)
		(use "git checkout -- <file>..." to discard changes in working directory)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m

	no changes added to commit (use "git add" and/or "git commit -a")
	'''
	if not needPull and changeNotAdd and needPush:
		print("不需要拉取代码,有代码改动但是未add,需要push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
		
	#无拉 有改动未add 有一个提交(待push)
	'''
	On branch dev
	Your branch is ahead of 'origin/dev' by 1 commit.
		(use "git push" to publish your local commits)

	Changes to be committed:
		(use "git reset HEAD <file>..." to unstage)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m
	'''
	if not needPull and changeDidAdd and needPush:
		print("不需要拉取代码,有代码改动且已经add,不能push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)

	#有待拉取  无改动 无提交
	'''
	On branch dev
	Your branch is behind 'origin/dev' by 2 commits, and can be fast-forwarded.
		(use "git pull" to update your local branch)

	nothing to commit, working tree clean
	'''
	if needPull and noChange and not needPush:
		print("要拉取代码,没有代码改动,不能push")
		print("⚠️ ⚠️ ⚠️ 请手动拉取代码:git pull origin "+target_branch())
		exit(0)
		
	#有待拉取 有改动但未add 无提交
	'''
	On branch dev
	Your branch is behind 'origin/dev' by 2 commits, and can be fast-forwarded.
		(use "git pull" to update your local branch)

	Changes not staged for commit:
		(use "git add <file>..." to update what will be committed)
		(use "git checkout -- <file>..." to discard changes in working directory)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m

	no changes added to commit (use "git add" and/or "git commit -a")
	'''	
	if needPull and changeNotAdd and not needPush:
		print("需要拉取代码,有代码改动但是未add,不能push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
	
	#有待拉取 有改动且add 无提交
	'''
	On branch dev
	Your branch is behind 'origin/dev' by 2 commits, and can be fast-forwarded.
		(use "git pull" to update your local branch)

	Changes to be committed:
		(use "git reset HEAD <file>..." to unstage)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m
	'''
	if needPull and changeDidAdd and not needPush:
		print("需要拉取代码,有代码改动且已add,不能push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
		
	#有待拉取 无改动 有一个提交
	'''
	On branch dev
	Your branch and 'origin/dev' have diverged,
	and have 1 and 2 different commits each, respectively.
		(use "git pull" to merge the remote branch into yours)

	nothing to commit, working tree clean
	'''
	if needPull and noChange and needPush:
		print("需要拉取代码,无代码改动,需要push")
		
	#有待拉取 有改动但无add 有一个提交
	'''
	On branch dev
	Your branch and 'origin/dev' have diverged,
	and have 1 and 2 different commits each, respectively.
		(use "git pull" to merge the remote branch into yours)

	Changes not staged for commit:
		(use "git add <file>..." to update what will be committed)
		(use "git checkout -- <file>..." to discard changes in working directory)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m

	no changes added to commit (use "git add" and/or "git commit -a")
	'''
	if needPull and changeNotAdd and needPush:
		print("需要拉取代码,有代码改动但未add,需要push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
	
	#有待拉取 有改动且已add 有一个提交
	'''
	On branch dev
	Your branch and 'origin/dev' have diverged,
	and have 1 and 2 different commits each, respectively.
		(use "git pull" to merge the remote branch into yours)

	Changes to be committed:
		(use "git reset HEAD <file>..." to unstage)

		modified:   WSPModule/WSPModule/Classes/Module/PublishJourney/VC/WSPPassengerPublishJourneyController.m
	'''
	if needPull and changeDidAdd and needPush:
		print("需要拉取代码,有代码改动且已add,需要push")
		print("⚠️ ⚠️ ⚠️ 请先提交或者贮藏你的代码")
		exit(0)
		
def ahead_target_branch_commit():
	status = cammand_out_put("git status", True, None)
	
	needPull = MSG_PULL in status
	noChange = MSG_NOCHANGE in status
	needPush = MSG_NEEDPUSH1 in status or MSG_NEEDPUSH2 in status
	
	if needPull and noChange and needPush:
		print("正在解析本地已经提交的个数...")
		matcher = ".*and have [0-9].*"
		pattern1 = re.compile(matcher)
		resultList = pattern1.findall(status)
		print resultList
		print status
		if len(resultList):
			#从matcher里分割出来字符串数组
			matcherStr = resultList[0]
			countStr = matcherStr.split(" ")[2]
			print "本地提交的个数是"+countStr
			return int(countStr)
		else:
			print "解析失败"
			exit(0)
	return 0

def target_branch_commit():
	cammand = CAMMAND_GIT_LOG+" {branch} --oneline".format(branch=target_branch())
	print("获取target分支的提交记录"+cammand)
	logs = cammand_out_put(cammand, True, None)
	return logs.split("\n")
			
def reset_and_stash(commitCount,commitLogs):
	stashTitleList = []
	index = 0
	while(index<commitCount):
		#commit这样: 81280d25 输入昵称空字符串进行拦截
		commit = commitLogs[index] 
		farwardCommit = commitLogs[index+1]
		
		#reset的时候要用前一个的commitID  暂存的时候要使用当前的commitMsg
		commitID = farwardCommit.split(' ')[0]
		commitMsg = commit.split(' ')[1]
		print(commitMsg+"=="+commitID)
		
		#reset代码
		git_reset_with_commitID(commitID)
		
		#暂存代码
		title = str(commitCount-index)+"_"+commitMsg
		git_stash_with_title(title)
		stashTitleList.append(title)
		index+=1
	return stashTitleList
	
#stashTitleList为list类型
def pop_stash_with_titles(stashTitleList):
	print("拉取所有的暂存的列表:"+CAMMAND_GIT_STASH_LIST)
	stashs = cammand_out_put(CAMMAND_GIT_STASH_LIST, True, None)
	
	stashList = stashs.split("\n")
	tempStashTitleList = stashTitleList
	for stash in stashList:
		for stashTitle in tempStashTitleList:
			if stashTitle in stash:
				stashTitleList.remove(stashTitle)
				stashOK = pop_stash_with_stash(stash)
				if stashOK:
					commit_stash_with_msg(stashTitle)	
				else:
					print("⚠️ ⚠️ ⚠️ 终止恢复暂存,有冲突产生,接下来需要手动解决")
					log_next_stash_count(stashTitleList)
					exit(0)

def pop_stash_with_title(title):
	print("拉取所有的暂存的列表:"+CAMMAND_GIT_STASH_LIST)
	stashs = cammand_out_put(CAMMAND_GIT_STASH_LIST, True, None)

def log_next_stash_count(stashTitleList):
	for stashTitle in stashTitleList:
		print("如下暂存还未被恢复,请手动解决"+stashTitle)

def commit_stash_with_msg(msg):
	print("提交恢复暂存的代码")
	
	print("add变更:"+CAMMAND_GIT_ADD_ALL)
	cammand_out_put(CAMMAND_GIT_ADD_ALL, True, None)
	
	cammandCommit = CAMMAND_GIT_COMMIT_MSG+" \"{msg}\"".format(msg=msg)
	print("提交代码:"+cammandCommit)
	cammand_out_put(cammandCommit, True, None)
	
def pop_stash_with_stash(stash):
	stashID = stash.split(": On")[0]
	print("正在恢复已经暂存的代码:"+CAMMAND_GIT_STASH_POP+"  --->"+stash)
	return cammand_out_put(CAMMAND_GIT_STASH_POP, False, False)
	
def git_reset_with_commitID(commitID):
	cammand = CAMMAND_GIT_RESET+" "+commitID
	print("重置已经提交的代码:"+cammand)
	cammand_out_put(cammand, True, None)
	
def git_stash_with_title(stashTitle):
	cammand = CAMMAND_GIT_STASH+" \"{stashTitle}\"".format(stashTitle=stashTitle)
	print("暂存已经更改的代码:"+cammand)
	cammand_out_put(cammand, True, None)
				

def pull_target_branch():
	print("拉目标分支代码:"+CAMMAND_PULL_TARGET_BRANCE)
	conflict = cammand_out_put(CAMMAND_PULL_TARGET_BRANCE, False, True)
	return conflict==True 
		
def give_up_rebase():
	print("放弃变基:"+CAMMAND_GIT_REBASE_ABORT)
	cammand_out_put(CAMMAND_GIT_REBASE_ABORT, False, None)

def create_branch_source():
	cammand = CAMMAND_CHECKOUT_BRANCH+" "+source_branch()
	print("创建新分支:"+cammand)
	result = cammand_out_put(cammand, False, False)
	if result==False:
		print("检测到本地分支{branch}已经存在".format(branch=source_branch()));
		msg = "❓❓❓是否删除此本地分支继续提交? yes/no"
		put = input_with_expect(["yes","no"],msg)
		if put == "yes":
			switch_target_branch()
			delete_branch_source()
			create_branch_source()
		else:
			print("请手动处理");
			exit(0)		
		
		
def push_branch_source():
	cammand = CAMMAND_PUSH_BRANCH+" "+source_branch()
	print("推送新(源)分支:"+cammand)
	cammand_out_put(cammand, True, None)

def can_push_branch_target():
	#外部指定了reviewer的人,则强制走review流程
	if inputAssiness!=None:
		return False
		
	targetBranch = project.branches.get(target_branch())
	return targetBranch.can_push

def push_branch_target():
	cammand = CAMMAND_PUSH_BRANCH+" "+target_branch()
	print("推送目标分支:"+cammand)
	cammand_out_put(cammand, True, None)


def create_merge_request():	
	assignee_id = check_assignee_id()

	commitID = cammand_out_put(CAMMAND_LAST_MY_COMMITID, True, None)
	print("\n最后一次我的提交的ID是"+commitID)
	
	commit = project.commits.get(commitID)
	print("\n最后一次我的提交的信息是"+commit.author_name+commit.message+commit.title)
	
	mr = project.mergerequests.create({'source_branch':source_branch(),
									   'target_branch':target_branch(),
	                                   'title':commit.title,
									   'remove_source_branch':True,
									   'assignee_id':assignee_id,
									   'description':commit.message
									  })
	print "创建merge request,其ID是:"+str(mr.iid)
	return mr
	
def send_dingding(mr):
	try:
		reviewer = mr.assignee["name"]
	except Exception as e:
		print "❌❌❌获取review名字失败,不发送钉钉"
		return
	url = mr.web_url
	sender = mr.author["name"]
	avatar = mr.author["avatar_url"]
	message = mr.title
	send.sendToDingDing(reviewer, url, msg=message, sender=sender,icon=avatar)
	
def deal_merge_request(mr):
	mrID = str(mr.iid)
	if auto_merge():
		print "review人是自己,需要自动merge,merge request ID是:"+mrID
		try:
			mr.merge()
			print "merge完毕"
		except Exception as e:
			webbrowser.open(mr.web_url)
			print e
			print "❌❌❌merge失败,请手动处理"
	else:
		print "需要他人merge,存储本次的merge request ID,ID是:"+mrID

	#自动合并也许保存ID，后边删除远程分支使用
	save_merge_request_ID(mrID)
		
def delete_source_branch_when_merged():
	mrIDList = read_merge_request_IDs()
	if not len(mrIDList):
		return
	
	print("本地存储的ID有:"+str(mrIDList))
	
	for mrID in mrIDList:
		mr = merge_request_with_ID(mrID)
		if not mr:
			continue
		
		sourceBranch = mr.source_branch
		if not sourceBranch:
			print ("source branch不存在,不删除对应分支,,删除本地的此ID,对应ID:"+mrID)
			#删除本地存储ID
			delete_merge_request_ID(str(mr.iid))
			continue
		if mr.state == "open":
			print ("分支:{branch} ID:{mrIID} 的merge request未被合并,不删除对应分支".format(branch=sourceBranch,mrIID=mrID))
			continue
		if mr.state == "closed":
			print ("分支:{branch} ID:{mrIID} 的merge request已被关闭,不删除对应分支,删除本地的此ID".format(branch=sourceBranch,mrIID=mrID))
			#删除本地存储ID
			delete_merge_request_ID(str(mr.iid))
			continue
		if mr.state == "merged":
			print ("分支:{branch} ID:{mrIID} 的merge request已被合并,需删除对应分支".format(branch=sourceBranch,mrIID=mrID))
			#删除远程source分支
			delete_origin_branch(mr.source_branch)
			#删除本地存储ID
			delete_merge_request_ID(str(mr.iid))

def delete_origin_branch(branch):
	cammand =CAMMAND_DELETE_BRANCH_ORIGIN+" "+branch
	print("删除远程分支:"+cammand)
	result = cammand_out_put(cammand, False, None)
	if not result:
		print "远程分支已经不存在,无需删除分支:"+branch

def save_merge_request_ID(mrID):
	mrIDList = read_merge_request_IDs()
	mrIDList.append(mrID)
	store_merge_request_IDs(mrIDList)

def delete_merge_request_ID(mrID):
	mrIDList = read_merge_request_IDs()
	if not len(mrIDList):
		return
	print("删除本地存储的merge request ID:"+mrID)
	mrIDList.remove(mrID)
	store_merge_request_IDs(mrIDList)

#mrIDList为空则清空本地储存的值
def store_merge_request_IDs(mrIDList): 
	if mrIDList and len(mrIDList):
		mrIDs = ','.join(mrIDList)
	else:
		mrIDs = "\"\""
	cammand = CAMMAND_GIT_CONFIG_MERGEREQUEST_IDS+" "+mrIDs
	print("本地写入merge request ID:"+cammand)
	cammand_out_put(cammand, True, None)

def read_merge_request_IDs():
	print("读取本地存储的merge request ID:"+CAMMAND_GIT_CONFIG_MERGEREQUEST_IDS)
	mrIDs = cammand_out_put(CAMMAND_GIT_CONFIG_MERGEREQUEST_IDS, False, None)
	if not mrIDs:
		print "没有本地储存的merge request ID"
		return []
	mrIDList = mrIDs.split(",")
	return mrIDList

def merge_request_with_ID(mrID):
	mr = None
	try:
		mr = project.mergerequests.get(mrID)
	except Exception,e:
		print e
		print "没有此merge request ID="+mrID
	return mr
	
def switch_target_branch():
	cammand = CAMMAND_SWITCH_BRANCH+" "+target_branch()
	print("切换到目标分支:"+cammand)
	cammand_out_put(cammand, False, False)

def delete_branch_source():
	cammand = CAMMAND_FORCE_DELETE_LOCAL_BRANCH+" "+source_branch()
	print("强制删除本地分支:"+cammand)
	cammand_out_put(cammand, True, None)

def git_fetch():
	print("抓取仓库信息:"+CAMMAND_GIT_FETCH)
	cammand_out_put(CAMMAND_GIT_FETCH, True, None)

def open_web_merge_request(mr):
	if auto_merge():
		print "mr的URL是:"+mr.web_url
	else:
		print("打开浏览器:"+mr.web_url)
		webbrowser.open(mr.web_url)

def module_files_list():	
	return files_list_with_path(current_path())
def pod_install_if_need():
	if len(GLOBAL_BEFORE_PULL_FILE_LIST)==0:
		print("被标记的文件列表没有数据,不执行pod install")
		return
	
	afterPullFliesList = module_files_list()
	if GLOBAL_BEFORE_PULL_FILE_LIST == afterPullFliesList:
		print("无文件变更,不需要执行pod install")
		return
		
	podfilePath = podfile_path()
	if not podfilePath:
		print("Podfile文件不存在,无法执行pod install...")
		return
		
	os.chdir(podfilePath)
	print("需要重新部署文件,正在执行:"+CAMMAND_POD_INSTALL)
	print("请稍后...")
	os.system(CAMMAND_POD_INSTALL)
	os.chdir(current_path())
	
def podfile_path():
	podfile = "Podfile"
	for root,dirs,files in os.walk(current_path()): 
			for eachFile in files:
				if eachFile == podfile:
					return root
	return None
		
def files_list_with_path(path):
	#忽略统计的文件夹
	igonreDir1 = "/Pods"
	igonreDir2 = "/.git"
	igonreDir3 = "/Assets"
	igonreDir4 = ".xcworkspace"
	igonreDir5 = ".xcodeproj"
	igonreDir6 = ".idea"
	
	filtList = []
	
	for root,dirs,files in os.walk(path): 
		#忽略Pods文件夹
		if (igonreDir1 in root or
		 	igonreDir2 in root or
		 	igonreDir3 in root or
		 	igonreDir4 in root or
		 	igonreDir5 in root or
		 	igonreDir6 in root):
				continue
		
		for eachFile in files:
			endH = eachFile.endswith(".h")
			endM = eachFile.endswith(".m")
			endMM = eachFile.endswith(".mm")
			endPlist = eachFile.endswith(".plist")
			endDB = eachFile.endswith(".db")
			if endH or endM or endMM or endPlist or endDB:
			 	filtList.append(eachFile)
	return filtList

def project_ID():
	projectID = read_project_ID()

	#缓存逻辑
	if projectID:
		print ("读取缓存的当前项目ID是:"+projectID)
		return projectID
	
	#没缓存逻辑
	congif_url = git_config_remote_url()
	if not len(congif_url):
		print ("❌❌❌没有远程仓库的URL!!!\n请先执行如下命令配置本仓库远程仓库的URL")
		print CAMMAND_GIT_REMOTE_URL+" "+"xxx"
		exit(0)
	
	print "从远端读取所有项目来匹配ID"
	try:
		projects = gl.projects.list(all=True)
		for p in projects:
			if p.ssh_url_to_repo == congif_url or p.http_url_to_repo == congif_url:
				projectID = p.id
				break
		if projectID>0:
			save_project_ID(projectID)
		else:
			print("projectID={pID} projectID不存在,请联系开发者".format(pID=projectID))
			exit(0)
	except Exception,e:
		print e
		print("❌❌❌无法获gitlab远程仓库的本项目ID, 请检查网络是否正常")
		print("如仍然无法解决,可执行如下命令配置项目ID:"+CAMMAND_GIT_CONFIG_PROJECT_ID+" projectID")
		exit(0)
		
	return projectID
				
def save_project_ID(projectID):
	cammand = CAMMAND_GIT_CONFIG_PROJECT_ID+" "+str(projectID)
	print ("缓存当前项目ID:"+str(projectID))
	cammand_out_put(cammand, True, None)
	
def read_project_ID():
	return cammand_out_put(CAMMAND_GIT_CONFIG_PROJECT_ID, False, None)


def last_my_short_commitID():
	cammand = "git rev-parse --short HEAD" #获取最后一次的提交的ID(短)
	return cammand_out_put(cammand, False, "")

#源分支自动获取, 不支持外部指定输入
def source_branch():
	global GLOBAL_BRANCH_SOURCE
	if GLOBAL_BRANCH_SOURCE:
		return GLOBAL_BRANCH_SOURCE
	
	#外部指定了,就用外部指定的
	if inputSourceBranch:
		GLOBAL_BRANCH_SOURCE = inputSourceBranch+"_"+last_my_short_commitID()
		return GLOBAL_BRANCH_SOURCE
		
	#使用代码生成的
	cammand = "git config --global user.name"
	name = cammand_out_put(cammand, False, None)
	if not name:
		print("请先执行命令配置自己对应gitlab上的名字"+cammand+" xxx")
		exit(0)
	
	#转拼音
#	pin = Pinyin()
#	name = unicode(name, 'utf-8') 
#	name = pin.get_pinyin(name,"")
	
	#拼上时间
#	dateTime = datetime.datetime.now().strftime('%H时%M分')#现在
#	name = name+"_"+dateTime
	
	GLOBAL_BRANCH_SOURCE = name+"_"+last_my_short_commitID()
	return GLOBAL_BRANCH_SOURCE

#目标分支支持外部指定输入	
def target_branch():
	if inputTargetBranch:
		return inputTargetBranch
	
	localTargetBranch = cammand_out_put(CAMMAND_GIT_CONFIG_TARGET_BRANCH, False, None)
	if localTargetBranch:
		return localTargetBranch
		
	return DEFAULT_BRANCH_TARGET	

def private_token():
	return cammand_out_put(CAMMAND_GIT_CONFIG_PRIVATE_TOKEN, False, "")

def gitlab_url():	
	return cammand_out_put(CAMMAND_GIT_CONFIG_GITLAB_URL, False, "")
	
	
def git_config_remote_url(url = None):
	if url:
		if url.startswith("http://") or url.startswith("ssh://"):
			cammand = CAMMAND_GIT_REMOTE_URL+" "+url
			print ("写入当前仓库的URL:"+cammand)
			url = cammand_out_put(cammand, True, None)
			return url
		else:
			print ("无效URL,无法写入")
			return None
	else:
		print ("读取当前仓库的URL:"+CAMMAND_GIT_REMOTE_URL)
		url = cammand_out_put(CAMMAND_GIT_REMOTE_URL, False, "")
		print url
		return url
	

def auto_merge():
	return current_login_user_name() == get_assiness()

def get_assiness():
	if inputAssiness:
		return inputAssiness
	
	if ASSINESS:
		return ASSINESS
		
	return current_login_user_name()

def local_branchs():
	result = cammand_out_put(CAMMAND_CURRENT_LOCAL_BRANCHS, True, None)
	return result.split("\n")

def current_select_branch():
	branchs = local_branchs()
	for i, val in enumerate(branchs):
		if "*" in val:
			return val.replace("* ","")

def check_assignee_id():
	users = gl.users.list(all=True)
	assignessName = get_assiness()
	assignee_id = None
	for user in users:
		if assignessName ==  user.name:
			assignee_id = user.id
	if assignee_id:
		print ("review的人名字是{name} ID是{id}".format(name=get_assiness(),id=assignee_id))
		return assignee_id
	else:
		print ("❌❌❌ 未找到review者的名字是{name},已创建无review名字的MR".format(name=assignessName))
		return assignee_id
		
def current_login_user_name():
	try:
		return gl.user.name
	except Exception as e:
		return "未获取到用户名"	
	
# 基础方法
def current_time():
	return datetime.datetime.now().strftime('%m-%d_%H:%M:%S')

def current_path():
	#TODO:脚本执行所在路径
	return os.getcwd()
	#TODO:脚本文件所在路径
	currentPath = os.path.realpath(__file__);
	fileName = os.path.basename(__file__);
	return currentPath.replace(fileName,"");
	pass
	
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

#接收输入,入参为期望值数组和提示文案
def input_with_expect(expectList=[], mark="请输入"):	 
	val = raw_input(mark+"\n请输入:")
	
	#为空不处理
	if not expectList or expectList == []:
		return val
		
	#全部转字符串
	tempList = []
	for expect in expectList:
		tempList.append(str(expect))
		
	while not val in tempList:
		val = input_with_expect(expectList=expectList,mark="无效输入,请重新输入")
	else:
		return val

#处理参数
def deal_argv(arguments):
	#删掉本身的参数
	arguments.remove(arguments[0])
	tempList = list(arguments)
	
	#输出帮助
	if "-h" in arguments or "--help" in arguments:
		log_help()
		exit(0)
		
	#输出版本
	if "-v" in arguments or "--version" in arguments:
		print VERSION
		exit(0)	
			
	#输出版本
	if "update" in arguments:
		update.updatejob()
		exit(0)
			
	global inputAssiness
	global inputSourceBranch
	global inputTargetBranch

	for idx, argu in enumerate(arguments):			
		#指定review的人
		if argu.startswith("-r=") or argu.startswith("--review="):
			tempArgu = argu.replace("--review=", "")
			tempArgu = tempArgu.replace("-r=", "")
			inputAssiness = tempArgu.replace("\"", "")
			print "用户指定的review人是:"+inputAssiness
			tempList.remove(argu)
			
		#指定源分支
		elif argu.startswith("-s=") or argu.startswith("--source="):
			tempArgu = argu.replace("--source", "")
			tempArgu = tempArgu.replace("-s=", "")
			inputSourceBranch = tempArgu.replace("\"", "")
			print "用户指定的源分支是:"+inputSourceBranch
			tempList.remove(argu)
		
		#指定目标分支
		elif argu.startswith("-t=") or argu.startswith("--target="):
			tempArgu = argu.replace("--target", "")
			tempArgu = tempArgu.replace("-t=", "")
			inputTargetBranch = tempArgu.replace("\"", "")
			print "用户指定的目标分支是:"+inputTargetBranch
			tempList.remove(argu)
		
	#校验参数是否有误
	if len(tempList):
		log_help()
		print "参数有误,请重新输入,未识别参数是:"
		for value in tempList:
			print value
		exit(0)
	if len(arguments):
		print "---------------"
	pass
	
def log_help():
	print "帮助:(命令为push后加参数)"
	print "*  push后加参数update 更新升级"
	print "*  push后加参数-h 或者--help 输出帮助"
	print "*  push后加参数-r=xxx 或者--review=xxx 指定review的人"
	print "*  push后加参数-s=xxx 或者--source=xxx 指定source分支"
	print "*  push后加参数-t=xxx 或者--target=xxx 指定target分支"
	print "*  其他命令:新增/修改默认目标分支请执行:"+CAMMAND_GIT_CONFIG_TARGET_BRANCH+" xxx"
	print "*  其他命令:查看默认目标分支请执行:"+CAMMAND_GIT_CONFIG_TARGET_BRANCH
	print "*  其他命令:删除默认目标分支请执行:"+CAMMAND_GIT_CONFIG_DELETE_TARGET_BRANCH
	pjconfig.log_help()
#入口
if __name__ == '__main__':
	deal_argv(sys.argv)

	print("开始工作...")
	
	main()
	
	print("工作完毕。")
	
	pass
