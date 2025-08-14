#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 11:26:55 2024

@author: liyifan
"""

import re
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw, ImageFont
import random
import time

# 设置文件夹路径
image_folder = "/Users/liyifan/Desktop/PNG/"
font_path = "/Users/liyifan/Library/Fonts/方正清刻本悦宋简体.ttf"
font_size = 10  # 根据需要调整字体大小
wait_time = 5  # 请求间隔时间

unwanted_phrases = [
    # 百度百科部分
    "网页", "新闻", "贴吧", "知道", "网盘", "图片", "视频", "地图", "文库", "资讯", "采购",
    "百科", "百度首页", "登录", "注册", "进入词条", "全站搜索", "帮助", "首页",
    "秒懂百科", "特色百科", "知识专题", "加入百科", "百科团队", "权威合作", "个人中心",
    "播报", "讨论", "收藏", "查看", "我的收藏", "有用+1", "上传视频", "编辑",
    "新手上路", "成长任务", "编辑入门", "编辑规则", "本人编辑", "我有疑问",
    "内容质疑", "在线客服", "官方贴吧", "意见反馈", "投诉建议", "举报不良信息",
    "未通过词条申诉", "投诉侵权信息", "封禁查询与解封", "©2024 Baidu", "使用百度前必读",
    "百科协议", "隐私政策", "百度百科合作平台", "京ICP证030173号", "京公网安备11000002000001号",
    "_百度", "秒懂", "特色", "加入", "团队", "我的", "上传", "入门", "规则", "本人",
    "官方", "2024", "Baidu", "协议", "百度合作平台",
    
    # 维基百科常见操作词组和冗余信息（颗粒度细化）
    "维基", "自由的全书", "跳转到内容", "主菜单", "移至侧栏", "隐藏", "导航", "分类索引",
    "内容", "动态", "最近更改", "随机条目", "社群", "方针", "指引", "互助客栈", "知识问答",
    "字词转换", "即时聊天", "联络", "关于", "资助", "外观", "创建账号", "个人工具", "未者的页面",
    "了解详情", "贡献", "序言", "开关目录", "添加语言", "条目", "简体", "繁體", "大陆简体", 
    "香港繁體", "澳門繁體", "大马简体", "新加坡简体", "臺灣正體", "阅读", "历史", "工具", "操作",
    "常规", "链入页面", "相关更改", "文件", "特殊页面", "固定链接", "页面信息", "引用此页",
    "获取短链接", "下载二维码", "打印导出", "下载为PDF", "打印页面", "维基共享资源", "维基数据",
    "隐藏分类", "本站的全部文字", "附加条款", "使用条款", "维基标志", "维基媒体基金会", "商标",
    "非营利", "慈善机构", "免责声明", "行为准则", "开发者", "统计", "Cookie声明", "手机版视图",
    "本站", "最后修订", "下载二维码", "失效链接", "永久失效", "含有hCards", "本地相关", 
    "维基数据相同", "包含FAST标识符", "包含ISNI标识符", "包含VIAF标识符", "包含WorldCat",
    "实体标识符", "包含CYT标识符", "包含GND标识符", "包含LCCN标识符", "包含ZBMATH标识符", 
    "包含HKCAN标识符", "标识符", "带有失效链接", "条目有失效链接",

    # 新增维基百科特定冗余词汇
    "本页面", "本页面最后修订", "星期六", "知识共享", "署名相同方式共享", "条款下提供", "附加条款",
    "参阅", "Wikipedia", "标志", "是", "的", "按", "美国", "国內稅收法", "登记", "搜索", 
    "添加链接", "不转换", "打印导出", "星期", "日", "年", "月", "日", "小时", "分钟", 
    "互联网档案馆", "在其他项目中", "维基共享", "基金会", "版本""Main page", "Contents", "Current events", "Random article", "About Wikipedia", "Contact us", 
    "Donate", "Help", "Contribute", "Talk", "View history", "Edit", "Create account", 
    "Log in", "Navigation menu", "Personal tools", "Community portal", "Recent changes", 
    "Upload file", "Special pages", "Permanent link", "Page information", "Cite this page", 
    "Related changes", "Printable version", "Download as PDF", "What links here", 
    "Wikipedia policies", "Terms of Use", "Privacy policy", "Disclaimers", "Cookie statement", 
    "Mobile view", "Non-profit organization", "Wikimedia Foundation", "Powered by MediaWiki", 
    "Search", "Languages", "Discussion", "Article", "View source", "Learn more", 
    "Not logged in", "Jump to navigation", "Jump to search", "Special pages", 
    "Page not found", "Category", "Portal", "Project page", "Tools", "Printable version", 
    "Download PDF", "Authority control", "Navigation", "External links", "References", 
    "Further reading", "Additional resources", "Cite this article", "Last edited"
    "Jump to content", "Main menu", "move to sidebar", "hide Navigation", "Main page", 
    "Contents", "Current events", "Random article", "About", "Contact us", "Contribute", 
    "Help", "Learn to edit", "Community portal", "Recent changes", "Upload file", 
    "Search", "Donate", "Appearance", "Create account", "Log in", "Personal tools", 
    "Pages for logged out editors", "learn more", "Contributions", "Talk", 
    "Toggle the table of contents", "Edit links", "Read", "Edit", "View history", 
    "Tools", "Actions", "What links here", "Related changes", "Permanent link", 
    "Page information", "Cite this page", "Get shortened URL", "Download QR code", 
    "Printable version", "In other projects", "Wikimedia Commons", "Wikidata item", 
    "From the free encyclopedia", "Retrieved from", "Categories", "Hidden categories", 
    "Articles with short description", "Short description matches Wikidata", 
    "Articles containing simplified Chinese-language text", "This page was last edited on", 
    "Text is available under the Creative Commons Attribution-ShareAlike 4.0 License", 
    "By using this site you agree to the Terms of Use and Privacy Policy", 
    "Privacy policy", "Disclaimers", "Contact", "Code of Conduct", "Developers", 
    "Statistics", "Cookie statement", "Mobile view", "is a registered trademark of the Wikimedia Foundation", 
    "additional terms may apply", "Authority control databases", "ISNI", "VIAF", "FAST", 
    "WorldCat", "National", "Germany", "United States", "Japan", "Australia", 
    "Netherlands", "Taiwan", "Poland", "Israel", "Academics", "People", "Trove", 
    "Other", "IdRef"

]


# 用户手动输入 URL 和对应的 PNG 文件名
url = input("请输入百科的URL地址: ")
image_name = input("请输入对应PNG图片的名字（不带扩展名）: ")

if not url:
    print("URL为空，将生成空白图像。")
    clean_text = ""  # 如果URL为空，文本内容也为空
else:
    try:
        # 发送请求获取页面内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 解析页面内容
        soup = BeautifulSoup(response.content, 'html.parser')

        # 检查是否是多义项页面
        polysemant_text = soup.find('div', class_='polysemantText_n6DKZ J-polysemantText')
        if polysemant_text:
            print(f"检测到多义项页面：{image_name}")

            # 获取多义项个数
            num_options = int(re.search(r'(\d+)', polysemant_text.get_text()).group(1))

            # 如果有多个词条，尝试获取所有可选项
            polysemant_list = soup.find_all('a', class_='contentItemchild')
            if polysemant_list:
                print(f"以下是可供选择的多义项，请输入编号选择：")
                for i, option in enumerate(polysemant_list):
                    title = option.get_text().strip()
                    href = option['href']
                    print(f"{i + 1}. {title} - {href}")

                # 用户选择
                choice = input(f"请输入你要选择的选项编号 (1-{len(polysemant_list)}): ")

                # 检查用户输入是否合法
                if choice.isdigit() and 1 <= int(choice) <= len(polysemant_list):
                    selected_option = polysemant_list[int(choice) - 1]['href']
                else:
                    print("无效输入，默认选择第一个选项。")
                    selected_option = polysemant_list[0]['href']

                # 构建完整的 URL
                full_url = f"https://baike.baidu.com{selected_option}"
                print(f"已选择：{full_url}")

                # 发送请求到选定的词条页面
                response = requests.get(full_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

        # 提取所有文本信息
        raw_text = soup.get_text(separator=" ")

        # 删除不需要的短语和词汇
        for phrase in unwanted_phrases:
            raw_text = raw_text.replace(phrase, "")

        # 去除引用数字如 [1], [2] 等
        clean_text = re.sub(r'\[\d+\]', '', raw_text)

        # 去除所有标点符号
        clean_text = re.sub(r'[^\w\s]', '', clean_text)

        # 去除多余的空白字符，使所有内容挤在一起
        clean_text = re.sub(r'\s+', ' ', clean_text)

        # 打印清洗后的结果
        print(f"爬取到的文本（{image_name}）:", clean_text)

    except requests.exceptions.RequestException as e:
        print(f"请求 {image_name} 时出错: {e}")
        clean_text = ""

# 加载PNG图片
input_image_path = os.path.join(image_folder, f"{image_name}.PNG")
mask_image = Image.open(input_image_path).convert("RGBA")
mask = mask_image.split()[-1]  # 使用alpha通道作为掩码

# 定义字体
font = ImageFont.truetype(font_path, font_size)

# 创建新的图像用于文本填充
img = Image.new('RGBA', mask.size, (0, 0, 0, 0))  # 透明背景
draw = ImageDraw.Draw(img)

# 动态调整步长，以确保文字均匀填充
def calculate_filled_area(mask):
    return sum(1 for y in range(mask.size[1]) for x in range(mask.size[0]) if mask.getpixel((x, y)) == 0)

def adjust_step_to_fill(filled_pixels, char_count):
    if char_count == 0:
        return 1  # 如果文本为空，默认步长为 1
    return max(1, int((filled_pixels ** 0.5) / (char_count ** 0.5)))

# 计算可填充的区域
total_filled_area = calculate_filled_area(mask)
total_chars = len(clean_text)
step = adjust_step_to_fill(total_filled_area, total_chars)

# 填充横版文字，从左到右，从上到下
def fill_text_horizontally(draw, text, mask, step):
    idx = 0
    for y in range(0, mask.size[1], step):  # 从上到下
        for x in range(0, mask.size[0], step):  # 从左到右
            if mask.getpixel((x, y)) == 0:  # 填充在透明区域
                if text:
                    draw.text((x, y), text[idx % len(text)], font=font, fill=(255, 255, 255, 255), anchor="lt")
                    idx += 1
    return idx


# 执行文本填充
filled_chars = fill_text_horizontally(draw, clean_text, mask, step)


# 创建输出文件夹
desktop_path = "/Users/liyifan/Desktop/Output"
os.makedirs(desktop_path, exist_ok=True)

# 保存透明PNG
output_filename = f"{image_name}_{total_chars}chars_{font_size}_{step}px.png"
output_path = os.path.join(desktop_path, output_filename)
img.save(output_path, 'PNG')

# 创建黑色背景版本
black_background_img = Image.new('RGBA', img.size, (0, 0, 0, 255))
black_background_img.paste(img, (0, 0), img)
output_demo_filename = f"{image_name}_demo.png"
output_demo_path = os.path.join(desktop_path, output_demo_filename)
black_background_img.save(output_demo_path, 'PNG')

print(f"保存成功: {output_path}, {output_demo_path}")

print("任务完成！")
