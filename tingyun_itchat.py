#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import requests
import itchat
from itchat.content import *
import logging
import commands
import random
from pyquery import PyQuery
import urllib
import os
import json
import chardet
user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]


def filter_str(str):
    return re.sub("[0-9\][\ \_\-\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*\%]","", str).lower()

def uni2utf8(uni_str):
    if isinstance(uni_str,unicode):
    	return uni_str.encode('utf8')
    logging.warning("编码不是unicode,不需要更改.")
    return uni_str

def sina_lbs():
    headers = {'User-Agent':random.choice(user_agent_list)}
    url = "http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json"
    recv_json = requests.get(url,headers=headers).json()
    lbs = {}
    lbs["country"] = recv_json["country"]
    lbs["province"] = recv_json["province"]
    return lbs


def get_locate_byip():
    url = "http://2017.ip138.com/ic.asp"
    content = requests.get(url).content
    content = content.decode("GB2312").encode("utf8")
    info = {}
    try:
        info['ip'] = re.search(r"\d+\.\d+\.\d+\.\d+",content).group()
        info['locate'] = re.findall(r"(?<=来自：).*(?=\</center)",content)[0]
    except Exception,e:
        info['locate'] = "获取地址位置失败"
        logging.warning("获取地理位置出错!")
    return info
#百度地图api接口,需要申请ak秘钥，并且一天会现在访问次数
#获取百度经纬度(&coor=bd09ll)，国家局(coor=gcj02)，设定coor即可
def get_locate_xy(ak):
    url = "http://api.map.baidu.com/location/ip?ak={ak}&coor=bd09ll".format(ak=ak)
    headers = {'User-Agent':random.choice(user_agent_list)}
    recv = requests.get(url,headers=headers)
    recv_json = recv.json()
    lbs_xy = {}
    if recv_json['status'] == 0:
        x = recv_json['content']['point']['x']
        y = recv_json['content']['point']['y']
        lbs_xy["x"] = x
        lbs_xy["y"] = y
        return lbs_xy
    else:
        logging.error("获取坐标失败!")
        return None
def baidu_lbs(ak):
    #can only locate the position to city at most
    lbs_xy = get_locate_xy(ak)
    url = "http://api.map.baidu.com/geocoder/v2/?coordtype=gcj02&location={y},{x}&output=json&pois=0&ak={ak}".format(x=lbs_xy['x'],y=lbs_xy['y'],ak=ak)
    headers = {'User-Agent':random.choice(user_agent_list)}
    recv = requests.get(url,headers=headers)
    recv_json = recv.json()
    return recv_json['result']['formatted_address']


#保存和关键词相关的文件，并返回文件路径
def get_doutu_picture(keyword):
    path = "./Img/"
    url = "https://www.doutula.com/search?type=photo&more=1&keyword={keyword}&page=1".format(keyword=urllib.quote(keyword))
    content = requests.get(url,headers={"User-Agent":random.choice(user_agent_list)}).content
    py_content = PyQuery(content)
    max_page = py_content('ul[class="pagination"] > li:last').prev().text()
    signal_img_dir = init_dirs(path,keyword)    #没有就 创建那个关键词的目录，有就返回路径
    print signal_img_dir
    page = random.choice(range(int(max_page)))
    random_url = re.sub("1$",str(page),url)     #随机选取一页

    random_content = requests.get(random_url,headers={"User-Agent":random.choice(user_agent_list)}).content
    py_content = PyQuery(random_content)
    all_img = list(py_content('.col-xs-6').items())
    signal_img = random.choice(all_img)
    #print signal_img
    img_url = list(signal_img('img[data-original]').items())[0].attr["data-original"]
    img_name = signal_img('p').text().encode('utf8').replace(" ","").replace("（","").replace("）","").replace("！","")
    img_name = re.sub("\w+","",img_name)
    type_img = re.findall("\w+$",img_url)[0]
    file_path = save_img(img_url,img_name+"."+type_img,signal_img_dir)
    return file_path




def init_dirs(path,name):
    signal_img_dir = path + name
    # 不存在即创建，再返回目录名，存在直接返回目录名
    if not os.path.exists(signal_img_dir):
        os.mkdir(signal_img_dir)
        return signal_img_dir+"/"
    return signal_img_dir+"/"

def save_img(img_url, img_name, work_dir):
    with open(work_dir + img_name, 'wb') as f:
        content = requests.get(img_url).content
        f.write(content)
        f.close()
    return work_dir+img_name

#若当前路径下存在Img文件夹，且有保存检索关键词（对方输入）的文件夹，即在其中找，默认是在斗图网上找，找到下载存储在本地
def word_map_jpg(word):
    dir_names = commands.getoutput("ls ./Img").split("\n")
    checked_dirs = []
    for name in iter(dir_names):
        if re.search(word,name):
            checked_dirs.append(name)
    one_dir = random.choice(checked_dirs)
    recv_jpg = ""
    img_names = commands.getoutput("ls ./Img/{dir_name}".format(dir_name=one_dir)).split("\n")
    img_name = random.choice(img_names)
    path = "./Img/{dir_name}/{img_name}".format(dir_name=one_dir,img_name=img_name)
    print path
    #f = open("./Img/{dir_name}/{img_name}".format(dir_name=one_dir,img_name=img_name),'r').read()
    return path

#获取煎蛋网段子页面的随机内容，在前十页中
def get_jiandan():
    url = "https://jandan.net/duan"
    content = requests.get(url,headers={"User-Agent":random.choice(user_agent_list)}).content
    py_content = PyQuery(content)
    max_page = list(py_content('.current-comment-page').items())[0].text()
    max_page = int(re.search("\d+",max_page).group())

    random_page = random.choice(range(max_page-20,max_page))
    random_url = "https://jandan.net/duan/page-{page}#comments".format(page=random_page)
    content = requests.get(random_url,headers={"User-Agent":random.choice(user_agent_list)}).content
    py_content = PyQuery(content)
    all_comments = list(py_content('.commentlist > li > div > div').items())
    signal_comment = random.choice(all_comments)
    author = signal_comment('.author > strong').text()
    text = signal_comment('.text > p').text()
    info = []
    info.append(author)
    info.append(text)
    return info




#定义一个方法，针对不同的文本（TEXT）回应不同的内容，供text_reply调用
def response(str):
    recv_text = uni2utf8(str)
    if filter_str(recv_text) == "图片":
        return "图片，你怎么知道我的宝藏？(*￣3￣)╭\n" \
               "那么请发送：'关键词'+图片\n" \
               "获取对应的图图~~么么哒~~"
    elif filter_str(recv_text) == "位置":
        #info = get_locate_str()
        info = sina_lbs()
        word = "我在这里哟 : "+info["country"]+info["province"]
        return word
    elif re.match(".+图片",recv_text):
        word = re.sub("图片","",recv_text.encode("utf8"))
        try:
            f = get_doutu_picture(word)
        except Exception,e:
            f = "None"
        if f != "None":
            return '@img@'+f
        else:
            return "sorry，your keyword looks like something error ~"
    elif re.match("段子",recv_text):
        try:
            f = get_jiandan()
        except Exception,e:
            f = "None"
        if f != "None":
            return f[1]+"\n\n\nby\t"+f[0]
        else:
            return "sorry，there looks something error ~"
    elif re.findall("撒比|萨比",filter_str(recv_text)):
        word = "日尼玛个香蕉船，牛萨比，特地为你写了这一行代码，就是用来骂你的 ! 牛萨比!"
        return word
    elif re.findall("老板",filter_str(recv_text)):
        word = "老朋友，给你介绍下'tingyun'，我的非智能小机器人，你可以输入一些别的内容来和他互动~"
        return word
    elif re.findall("功能|你是|hello|hi|你好|嘿",filter_str(recv_text)):
        word = "Hi, my name is tingyun，now just an automatic reply code, a litter boy, living in the {location}\n" \
               "there is something i can do for you:\n" \
               "1. get picture   :'keyword'+图片\n" \
               "2. get some joke : 段子         \n" \
               "\nI would like to be something people called AI in the future, wait me!".format(location=sina_lbs()['country']+sina_lbs()['province'])
        return word
    elif re.findall("早",filter_str(recv_text)):
        word = "你也早啊～～"
        return word
    elif re.findall("吃了吗",filter_str(recv_text)):
        word = "我吃饱了哟，你也要吃的饱饱的呀，每天都要元气满满～～"
        return word
    else:
        word = "oh, you find me. then type \"功能\" play with me，i will tell you something secret~~"
        return word


@itchat.msg_register([TEXT,PICTURE])
def text_reply(msg):
    recv_content = msg['Text']
    word = response(recv_content)
    return word
    #itchat.send_file('./a.jpg',toUserName=msg['FromUserName'])


@itchat.msg_register([MAP])
def text_reply(msg):
    if msg['Type'] == 'Map':
        x, y, location = re.search(
        "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()  # 内容为详细的地址
        else:
            msg_content = r"" + location
        return "嘿，我找到你了～～你四不四在:\n"+msg_content.encode("utf8")

'''
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)
'''

if __name__=="__main__":
    itchat.auto_login(enableCmdQR=2,hotReload=True)
    itchat.run(debug=True)
    ak = ""


