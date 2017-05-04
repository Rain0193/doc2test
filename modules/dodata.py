# -*- coding: utf-8 -*-

####################  本文件用于进行基本的 xml     json    urlencode 操作

import sys,re


"""
对应发行版中查找安装libxml2
debian: apt install python-libxml2 python3-libxml2

windows: http://xmlsoft.org/sources/win32/python/libxml2-python-2.7.7.win32-py2.7.exe

"""
import libxml2


"""
lxml ：
linux:  pip2/pip3  install  lxml   ， 或 apt-get install python3-lxml （python3)

windows ：
http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml  下载对应的 whl,  如 lxml‑3.6.4‑cp27‑cp27m‑win32.whl，  pip install lxml‑3.6.4‑cp27‑cp27m‑win32.whl
（若提示安装VC9.0 编译环境，可安装 Micorsoft Visual C++ Compiler for Python 2.7    http://www.microsoft.com/en-us/download/details.aspx?id=44266）
pip install six
pip install ply

"""

from lxml import etree   


import json
from jsonpath_rw import jsonpath, parse    # pip2/pip3 install jsonpath_rw



import platform
sysstr = platform.system()   ### 判断操作系统类型   Windows   Linux    .   本脚本函数入口, 统一以 LINUX 为准, 其后在函数内进行转换

if sysstr == "Linux":
        import hues   ## pip install hues

if sysstr == "Windows":
        import winhues as hues



####################################### XML

xmldoc=None

##################### 返回对应节点  firefox  xpath 可以通过  firebug -  firepath  插件获得

def xmlnode(xmlstr, xpath):

	if sys.version_info.major==2:   ## 3 默认 utf-8
		reload(sys)
		sys.setdefaultencoding('utf-8')

	global xmldoc

	xmldoc = libxml2.parseMemory(xmlstr,int(len(xmlstr)*1.2))   # libxml2.parseFile("test.xml")    考虑到解析情况长度会发生变化  所以增加一些长度
	#print (xmldoc)

	if xpath[0:1]=="@":   ## 唯一叶子的表示法
		xpath="//"+xpath[1:]

	if  xpath[0:1]!="/":   ## 增加一个 根
		xpath="/"+ xpath

	if "xmlns=" in xmlstr:     ##   存在 xmlns

		#### 判断是否　xpath 中已经有命名空间, 转为普通　xpath

		if ":" in xpath:
			pos1=xpath.find(":")
			namespace=xpath[1:pos1]
			#print(namespace)
			xpath=xpath.replace("/"+namespace+":", "/")
			#print(xpath)

		####  插入命名空间

		xpath=xpath.replace("/","/namespace:")
		xpath=xpath.replace("/namespace:/namespace:","//namespace:")         #对于 // 直接寻找叶子的情况
		#print(xpath)

		pos1=xmlstr.find("xmlns=")
		#print(pos1)
		pos2=xmlstr.find("\"",pos1+6+1)
		#print(pos2)
		xmlns=xmlstr[pos1+6+1:pos2]
		#print(xmlns)
		
		XPathDoc = xmldoc.xpathNewContext()
		XPathDoc.xpathRegisterNs('namespace',xmlns)
		
		try:
			nodes=XPathDoc.xpathEval(xpath)
		except:
			hues.error(u"XML 命名空间设置失败:" + xpath)
			node=None   #### 供后续抛出异常	
		#print(node)

	else:
		nodes=xmldoc.xpathEval(xpath)   ### 普通 xml, 没有命名空间

	#print(node)

	try:
		node=nodes[0]
	except:
		hues.error(u"没有找到XML节点:" + xpath)
		node=None   #### 供后续抛出异常

	return node



##################### XML 读取指定节点 

def readxml(xmlstr, xpath):   ## 返回对应值

	node=xmlnode(xmlstr, xpath)

	value=""
	
	try:
		value=node.content
	except:	
		pass
	
	return value


##################### XML 写入指定节点 

## 编码转换
def convert(s):

	s = s.strip('&#x;')  # 把'&#x957f;'变成'957f'
	s=r'\u'+ s

	if sys.version_info.major==2:   
		return s.decode('unicode_escape')
	else:
		s=bytes(s, encoding = "utf8").decode('unicode_escape')
		return s

	

## 全篇编码转换

def convertall(strs):

	res=re.sub(r'&#x....;',
			lambda match: convert(match.group()),
			strs)
	return str(res)


def writexml(xmlstr, xpath, value):    ## 返回 xml 字符串

	node=xmlnode(xmlstr, xpath)

	try:
		node.setContent(value)
		#print(node)
	except:	
		pass
	
	xmlstr=convertall(str(xmldoc))   # 模块公共变量
	return xmlstr      


def writexml_ffile(files, xpath, value):      ###  从xml文件读取  并修改对应的值

	data=open(files).read()
	xmlstr=writexml(data, xpath, value)
	
	return xmlstr


#########################################  JSON

#  jsonpath 可以通过 firefox  JSON-handle  插件获得

jsondoc=None

##################### 返回对应 json 节点

def jsonnode(jsonstr,jsonpath):

	if jsonpath[0:5]=="JSON.":    ## 适应  JSON-handle 的  json path
		jsonpath="$." + jsonpath[5:]


	if jsonpath[:1]=="@":    ## 直接叶子写法
		jsonpath="$.." + jsonpath[1:] + "[0]"

	#print(jsonpath)

	try:
		jsonpath_expr = parse(jsonpath)
	except:
		return None

	global jsondoc
	jsondoc = json.loads(jsonstr)

	for match in jsonpath_expr.find(jsondoc):		
		node=match
		return node



##################### JSON 读取指定节点 

def readjson_old(jsonstr,jsonpath):            #####   jsonpath_rw  中文内容节点的取值有点问题, 原始方法弃用

	node=jsonnode(jsonstr,jsonpath)

	try:
		value=node.value
	except:
		hues.error(u"没有找到JSON节点: " + jsonpath)
		value=""
	
	return value


def initjson(jsonstr,jsonpath):   # 初始化 json 字符串

	node=jsonnode(jsonstr,jsonpath)

	###  jsonpath_rw 中对应功能未实现写操作
	###  node.value=value

	#############  使用正则处理
	#print(dir(jsondoc))
	
	if sys.version_info.major==2:   
		jsonstr=str(jsondoc).decode('unicode_escape')
	else:
		jsonstr=str(jsondoc)

	
	jsonstr=jsonstr.replace("u'","'")
	
	return(jsonstr,node)



def leftjsonpos(jsonstr,jsonpath):    #  对应jsonpath值前的左侧位置

	(jsonstr,node)=initjson(jsonstr,jsonpath)

	try:
		repath=str(node.full_path)
	except:
		hues.error(u"没有找到JSON节点: " + jsonpath)
		return(-1,"")

	#print(repath)

	### 通过正则表达式
	if repath[len(repath)-4:]==".[0]":      # 叶子节点的 .[0]          
		repath=repath[:len(repath)-4]

	#print(jsonstr)

	repathlist=repath.split(".")
	#print(repathlist)
	
	#左侧特征举例   (.*l1('|\"):(.*).*('|\")l1_1('|\"): ('|\"|\[\"|\[\'))
	#{'l2': {'l2_3': {}, 'l2_2': True, 'l2_1': None}, 'l1': {'l1_1': ['中文测试', 'l1_1_2'], 'l1_2': {'l1_2_1': 121}}}

	repath= "('|\"):(.*).*('|\")".join(repathlist)                 ## 单引号或双引号

	repath=".*" + repath + "('|\"): ('|\"|\[\"|\[\')"     ### 几种可能   '   "  ["   ['
	#repath=".*" + repath + "('|\"): ('|\")"

	repath="(" + repath + ")"     ## 左侧特征
	#print(repath)

	matchs=re.match(repath,jsonstr,re.DOTALL)   ### 最后一个参数解决换行问题
	if matchs!=None:
		leftstr=matchs.groups()[0]  ## 左侧串
		#print(leftstr)
		return(len(leftstr),leftstr)
	else:
		### 没找到
		hues.warn("没有找到JSON节点左侧边缘:" + jsonpath)
		return -1


def rightjsonpos(jsonstr,jsonpath):   #  对应jsonpath值后的右侧位置

	
	(left,leftstr)=leftjsonpos(jsonstr,jsonpath)    ## 左侧串位置
	if left==-1:
		hues.warn("没有找到JSON节点左侧边缘:" + jsonpath)
		return -1
		
	(jsonstr,node)=initjson(jsonstr,jsonpath)       ## 格式化总体串(取位置,必须按格式化串操作)

	### 右侧单引号或双引号
	pos1=jsonstr.find("'", left+1)   
	pos2=jsonstr.find("\"", left+1)

	if pos2==-1:
		rightstr=jsonstr[pos1:]	## 右侧串
		pos=pos1
	elif pos1==-1:
		rightstr=jsonstr[pos2:]
		pos=pos2
	elif pos1<pos2:
		rightstr=jsonstr[pos1:]
		pos=pos1 
	else:
		rightstr=jsonstr[pos2:]
		pos=pos2
	
	return(pos,rightstr)
	

def readjson(jsonstr,jsonpath):   

	(left,leftstr)=leftjsonpos(jsonstr,jsonpath)   ## 左侧串位置
	if left==-1:
		return ""

	(right,rightstr)=rightjsonpos(jsonstr,jsonpath)    ## 右侧串位置
	if right==-1:
		return ""
		
	(jsonstr,node)=initjson(jsonstr,jsonpath)    ## 格式化总体串(取位置,必须按格式化串操作)

	#print(left)
	#print(right)
	ret=jsonstr[left:right]

	return ret


##################### JSON 写入指定节点   -----------------  多个节点 [n] 暂时不能处理

def writejson(jsonstr, jsonpath, value):

	(left,leftstr)=leftjsonpos(jsonstr,jsonpath)   ## 左侧串
	if left==-1:
		return jsonstr

	(right,rightstr)=rightjsonpos(jsonstr,jsonpath)   ## 右侧串
	if right==-1:
		return jsonstr

	#print(left)
	#print(right)
	#print("left: " + leftstr)
	#print("right: " +rightstr)

	res=leftstr +value  + rightstr      ## 左右拼加

	###  json 单引号变双引号
	res=res.replace("'","\"")

	return res


def writejson_ffile(files, jsonpath, value):      ###   从 json 文件读取  并修改对应的值

	data=open(files).read()
	jsonstr=writejson(data, jsonpath, value)
	
	return jsonstr


###################################  URLCODE

def writeurlcode(data, path, value):        #####  修改某个值

	vardata=path+"=" + readurlcode(data, path)
	
	urlcodestr=data.replace(vardata, path+"=" + value)

	urlcodestr=urlcodestr.replace("\n","")
	urlcodestr=urlcodestr.replace("\r","")

	return urlcodestr


def readurlcode(data, path):       ##### 读取某个值

	value=""
	pos1=data.find(path+"=")
	#print(pos1)
	
	if pos1>=0 and pos1+4<len(data):   ##  找到且不在末尾
		pos2=data.find("&",pos1+4)
		#print(pos2)
		
		if pos2<0:
			value=data[pos1+4:]
		else:
			value=data[pos1+4:pos2]			

	return value


def writeurlcode_ffile(files, path, value):        ####### 从文件读取, 然后修改某个值

	data=open(files).read()
	data=data.replace("\n","")
	data=data.replace("\r","")

	urlcodestr=writejson(data, path, value)

	return urlcodestr

#################################### HTML

def readhtml(data,xpath):

	etrees=etree.HTML(data)

	##### lxml 处理 xpath 特点
	xpath=xpath.replace("html/body/","//")   ### 不能写 html/body/ ，这是 firebug 的写法特点	
	xpaths=xpath.replace("/tbody/","/")   ### 去掉所有 tbody

	#print(xpaths)

	ele= etrees.xpath(xpaths)
	if len(ele)==0:   		### 不能用 None 判断
		xpaths=xpath 		### 不去掉
		ele= etrees.xpath(xpaths)

	
	#####

	types=""  ## 暂时只支持取 text

	#####

	try:
		if types=="":
			values=ele[0].text		### 元素的 text
		else:
			values=str(etrees.xpath(xpaths+ "/@" + types)[0])   ### 元素的对应属性
		#print(values)
	
	except:
		#print(u"** 数据截获异常 **")
		values=""      ## 没有这个元素则返回为空


	if  values==None or len(ele)==0:
		hues.warn("HTML节点: " +xpath +" 查找失败.")
		values=""
	return values



###################################  自动区分类型

def whichtypes(data):

	## 判断类型
	#print(data)

	xmlre=data.count('<')
	jsonre=data.count('{')
	urlcodere=data.count('=')

	data=data.strip()

	types=""

	if data[:6]=="<?xml ":
		types="xml"
	elif data.find("<html")>=0 and data.find("</html>")>0:
		types="html"
	elif  xmlre>jsonre and xmlre>urlcodere:
		types="xml"			
	elif jsonre>xmlre and jsonre>urlcodere:
		types="json"		
	elif urlcodere>xmlre and  urlcodere>jsonre:		
		types="urlcode"


	#print(types)
	return types


def writenode(data, path,value):

	## 判断类型
	types=whichtypes(data)

	if types=="xml":
		data=writexml(data, path, value)
	if types=="json":
		data=writejson(data, path, value)
	if types=="urlcode":
		data=writeurlcode(data, path, value)
	if types=="html":
		hues.error("html格式只支持读节点")

	return data

def readnode(data,path):

	## 判断类型
	types=whichtypes(data)

	if types=="":
		hues.error("数据类型识别错误")
		return ""

	value=""

	if types=="xml":
		value=readxml(data,path)
	if types=="json":
		value=readjson(data,path)
	if types=="urlcode":
		value=readurlcode(data, path)
	if types=="html":
		value=readhtml(data,path)

	return value

def writenode_ffile(files, path, value):

	## 判断类型
	data=open(files).read()
	types=whichtypes(data)

	if types=="":
		hues.error("文件类型识别错误")
		return ""

	if types=="xml":
		data=writexml_ffile(files, path, value)
	if types=="json":
		data=writejson_ffile(files, path, value)
	if types=="urlcode":
		data=writeurlcode_ffile(files, path, value)
	if types=="html":
		hues.error("html格式只支持读节点")

	return data









