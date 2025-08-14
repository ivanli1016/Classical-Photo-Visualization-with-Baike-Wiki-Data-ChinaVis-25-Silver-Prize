#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 22:42:04 2024

@author: liyifan
"""
import re
import requests
from bs4 import BeautifulSoup

# 目标网址
url = 'https://baike.baidu.com/item/萨本栋'

# 发送请求获取页面内容
response = requests.get(url)

# 解析页面内容
soup = BeautifulSoup(response.content, 'html.parser')

# 提取所有文本信息
raw_text = soup.get_text(separator=" ")

# 删除不需要的短语和词汇
unwanted_phrases = [
    "网页", "新闻", "贴吧", "知道", "网盘", "图片", "视频", "地图", "文库", "资讯", "采购", 
    "百科", "百度首页", "登录", "注册", "进入词条", "全站搜索", "帮助", "首页", 
    "秒懂百科", "特色百科", "知识专题", "加入百科", "百科团队", "权威合作", "个人中心", 
    "播报", "讨论", "收藏", "查看", "我的收藏", "有用+1", "上传视频", "编辑", 
    "新手上路", "成长任务", "编辑入门", "编辑规则", "本人编辑", "我有疑问", 
    "内容质疑", "在线客服", "官方贴吧", "意见反馈", "投诉建议", "举报不良信息", 
    "未通过词条申诉", "投诉侵权信息", "封禁查询与解封", "©2024 Baidu", "使用百度前必读", 
    "百科协议", "隐私政策", "百度百科合作平台", "京ICP证030173号", "京公网安备11000002000001号", 
    "_百度", "秒懂", "特色", "加入", "团队", "我的", "上传", "入门", "规则", "本人", 
    "官方", "2024", "Baidu", "协议", "百度合作平台"
]

for phrase in unwanted_phrases:
    raw_text = raw_text.replace(phrase, "")

# 去除引用数字如 [1], [2] 等
clean_text = re.sub(r'\[\d+\]', '', raw_text)

# 去除所有标点符号
clean_text = re.sub(r'[^\w\s]', '', clean_text)

# 去除多余的空白字符，使所有内容挤在一起
clean_text = re.sub(r'\s+', ' ', clean_text)

# 打印清洗后的结果
print(clean_text)



