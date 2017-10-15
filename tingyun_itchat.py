#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import sys,os
import re
import requests
import itchat
import time
from itchat.content import *
import chardet
import logging
import commands
import random
import json


def filter_str(str):
    return re.sub("[0-9\][\ \_\-\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*\%]","", str).lower()

def uni2utf8(uni_str):
    if isinstance(uni_str,unicode):
    	return uni_str.encode('utf8')
    logging.warning("编码不是unicode,不需要更改.")
    return uni_str

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
    url = "http://api.map.baidu.com/location/ip?ak={ak}&coor=gcj02".format(ak=ak)
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
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

def get_locate_str(ak):
    lbs_xy = get_locate_xy(ak)
    #url = "http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&location={x},{y}&output=json&pois=0&ak={ak}".format(x=lbs_xy['x'],y=lbs_xy['y'],ak=ak)
    url = "http://api.map.baidu.com/geocoder/v2/?coordtype=gcj02&location={y},{x}&output=json&pois=0&ak={ak}".format(x=lbs_xy['x'],y=lbs_xy['y'],ak=ak)
    print url
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    recv = requests.get(url,headers=headers)
    recv_json = recv.json()
    return recv_json['result']['formatted_address']


#定义一个方法，针对不同的文本（TEXT）回应不同的内容，供text_reply调用
def response(str):
    recv_text = uni2utf8(str)
    if filter_str(recv_text) == "图片":
        return "图片，你怎么知道我的宝藏？(*￣3￣)╭\n" \
               "那么请发送：'关键词'+图片\n" \
               "获取对应的图图~~么么哒~~"
    elif filter_str(recv_text) == "位置":
        info = get_locate()
        word = "我在这里哟 : "+info['locate']
        return word
    elif re.match(".+图片",recv_text):
        word = re.sub("图片","",filter_str(recv_text))
        f = word_map_jpg(word)
        return '@img@'+f
    elif re.findall("好帅",filter_str(recv_text)):
        word = "不要这么夸人家啦~~~"
        return word
    elif re.findall("撒比|萨比",filter_str(recv_text)):
        word = "日尼玛个香蕉船，牛萨比，特地为你写了这一行代码，就是用来骂你的 ! 牛萨比!"
        return word
    elif re.findall("老板",filter_str(recv_text)):
        word = "老朋友，给你介绍下'听云'，我的非智能小机器人，你可以输入一些别的内容来和他互动~"
        return word
    elif re.findall("功能|你是|hello|hi|你好|嘿",filter_str(recv_text)):
        word = "Hello，我叫听云，暂时只是一段自动回复代码，性别男，居住地在日本～～\n" \
               "这是我的功能介绍:\n" \
               "\t1.获取图片\t\t:'关键词'+图片\n" \
               "\t2.获取金光同人小说\t:'关键词'+故事\n\n" \
               "我是个以后要称为AI的小程序哦~~"
        return word
    elif re.findall("早",filter_str(recv_text)):
        word = "你也早啊～～"
        return word
    elif re.findall("吃了吗",filter_str(recv_text)):
        word = "我吃饱了哟，你也要吃的饱饱的呀，每天都要元气满满～～"
        return word
    else:
        word = "啦啦啦，输入'功能'和我互动啦，我会告诉你我的名字哟~~"
        return word

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


@itchat.msg_register([TEXT])
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


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)


if __name__=="__main__":
    #itchat.auto_login(enableCmdQR=2,hotReload=True)
    #itchat.run(debug=True)
    ak = ""
    print get_locate_str(ak)

    #print get_locate()
    #b="功能"
    #print re.findall("功能|你是|hello|hi|你好|嘿",filter_str(b))

    #print word_map_jpg("金馆长")
    '''
    nima = {
        'a': 'a',
        'b': 'b',
        'd': 'c',
        'e': 'd',
    }.get("a", 'picture_5.jpg')
    print '@img@' + nima
    '''


