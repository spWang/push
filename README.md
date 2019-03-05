## push.py

#### 本脚本地址:
https://github.com/spWang/push

### 功能
1.对git  push命令的封装,在git  push命令之前增加了诸多校验,在之后增加了额外的功能<br>
2.对要提交代码检查,防止漏掉要提交的文件<br>
3.从commit完毕开始,一键发布merge request,命令 push -r=xxx<br>
4.一键推送,命令 push<br>
5.iOS项目设置公司名字和类前缀<br>
6.更多设置和帮助 命令 push -h<br>
 

### 配置方法
1.拉取master分支代码,在~/.bash_profile文件里增加如下配置:<br>
```objc
alias push="python '这里换成脚本的全路径/push.py'"<br>
```
2.刷新窗口:source ~/.bash_profile<br>
3.cd到需要提交的仓库下面,执行push根据提示继续操作即可完成push代码<br>
4.默认设定的push分支是dev,可以试用push -h命令按提示自助修改

-----------------------------------------------分割线----------------------------------------------------------------

### 常见问题(接入时无需执行这里,脚本出问题时可参考这里)

####备忘
python setup.py sdist bdist_wheel
twine upload dist/*
https://blog.csdn.net/qq_38486203/article/details/83659287
