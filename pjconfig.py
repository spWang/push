#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import subprocess

reload(sys)  
sys.setdefaultencoding('utf8')

CAMMAND_GIT_CONFIG_CLASSPREFIX = "git config pushconfig.classprefix" ##项目前缀
CAMMAND_GIT_CONFIG_ORGANIZATION = "git config pushconfig.organization" ##项目组织名


def main():
    
    setup_class_prefix_if_need()
    
    
def setup_class_prefix_if_need():
#    print "前缀还有问题,先不开启此功能"
#    return
    
    print "检查是否需要配置工程"
    pods_dir_exists()

def pods_dir_exists():
    #判断PODS文件夹是否存在
    pods_path = None
    for root,dirs,files in os.walk(current_path()):
        if "/Pods" in root:
            pods_path = root
            break
    if not pods_path:
        return
    
    #判断PODS配置文件是否存在
    podsConfgPath = None
    for podDir in os.listdir(pods_path):
        if podDir.endswith(".xcodeproj"):
            podsConfgPath = pods_path+"/"+podDir+"/project.pbxproj"
            break
    if not podsConfgPath:
        return
    
    #打开文件 读取匹配关键字
    content = ""
    with open(podsConfgPath, 'r') as f:
        content = f.read()
        
        keyPrefix = "CLASSPREFIX"
        keyOrganization= "ORGANIZATIONNAME"
        
        prefix = dealStrIfHaveChinese(class_prefix())
        organization = dealStrIfHaveChinese(organization_name())
        
        searchPrefix = keyPrefix+" = "+prefix
        searchOrganization = keyOrganization+" = "+organization
#        print searchPrefix
#        print searchOrganization
        if searchPrefix in content and searchOrganization in content:
            print "prefix和organization已经是正确的配置,无需设置"
            return
        
        result = re.findall(r"attributes = \{([\s\S]+?)\}\;",content)
        
        if len(result)==0:
            print "异常:未检索到attributes关键字"
            return
        

        
        #提取被替换的内容
        willBeReplaceStr = result[0]
        array = willBeReplaceStr.split(";")
        array.remove(array[-1])
        tempArray = []
        for value in array:
            if not keyPrefix in value and not keyOrganization in value:
                tempArray.append(value)
        
        prefix = "\n\t\t\t\tCLASSPREFIX = "+prefix
        organization = "\n\t\t\t\tORGANIZATIONNAME = "+organization
        lineBreak = "\n\t\t\t"
        
        tempArray.insert(0, prefix)
        tempArray.append(organization)
        replaceStr = ';'.join(tempArray)+";"
        replaceStr = replaceStr+lineBreak
        print "替换prefix和organization"
        content = content.replace(willBeReplaceStr,replaceStr)

    #写入改后的内容
    with open(podsConfgPath, 'w') as f:
        f.write(content)

    return  
    
def dealStrIfHaveChinese(prefix):
    regex = re.compile(r"^[a-zA-Z0-9]*$", re.S)
    result = regex.match(prefix)
    if result:
        return prefix
    else:
        return "\""+prefix+"\""
#        print "❌❌❌ 被忽略写入:class_prefix只支持英文,请重新设置:"+CAMMAND_GIT_CONFIG_CLASSPREFIX+" xxx"
       
def class_prefix():
    value = cammand_out_put(CAMMAND_GIT_CONFIG_CLASSPREFIX, False, None)
    if not value:
        return None
        
    print("配置的CLASS PREFIX:"+value)
    return value

def organization_name():
    value = cammand_out_put(CAMMAND_GIT_CONFIG_ORGANIZATION, False, None)
    if not value:
        return None
        
    print("配置的组织名字:"+value)
    return value
    
def log_help():
    print"*  配置CLASS PREFIX执行:"+CAMMAND_GIT_CONFIG_CLASSPREFIX+" xxx"
    print"*  配置组织名字执行:"+CAMMAND_GIT_CONFIG_ORGANIZATION+" xxx"

def current_path():
    return os.getcwd()

def job_file_path():
    currentPath = os.path.realpath(__file__);
    fileName = os.path.basename(__file__);
    return currentPath.replace(fileName,"");

def cammand_out_put(cammand, can_raise, return_value):
    try:
        return subprocess.check_output(cammand, shell=True).strip()
        pass
    except subprocess.CalledProcessError as e:
        if can_raise:
            raise(e)
        else:
            return return_value
            pass
    pass

#入口
if __name__ == '__main__':

    print ("开始")
    
    main()
    
    print ("完毕")
    
    pass