# !usr/bin/env/python
# -*- coding: utf-8 -*-
"""
# version: 1.0
# author : guoxunqiang
# file   : spider_cartoon
# time   : 2020/6/29 0:21
"""
import re
import os
import requests
from bs4 import BeautifulSoup
# from urllib.request import urlretrieve

"""
爬取背景：爬取动漫《妖神记》
网站反爬策略有:(1)点击右键无法element查看网页源代码,解决方法:F12或URL地址最前面添加"view-source:"
               (2)Header反爬机制,添加Referer
动态加载：(1)如何判断是否是动态加载，element能目标href,但网页源代码中不能找到。网页源代码是不管动态加载的内容。如这里面没有图片             链接，就说明图片是动态加载的。  
          (2)动态加载不外乎两种一种是外部加载，内部加载
            外部加载:外部加载就是在html页面中，以引用的形式，加载一个js，例如这样：<script type="text/javascript" src="https://cuijiahua.com/call.js"></script>
            内部加载：就是Javascript脚本内容写在html内，例如这个漫画网站。
            
beautifulSoup + requests
"""


class CartoonDownLoader(object):
    def __init__(self):
        self.targe = r'https://www.dmzj.com/info/yaoshenji.html'
        self.server = r'https://www.dmzj.com'
        self.chapter_names = []
        self.chapter_urls = []
        
    def _get_chapter_urls(self):
        response = requests.get(self.targe)
        response.encoding = 'utf-8'
        bf = BeautifulSoup(response.text, 'lxml')
        list_con_li = bf.find('ul', class_='list_con_li autoHeight')
        # print(list_con_li.prettify())
        chapters = list_con_li.find_all('li')
        for chapter in chapters:
            chapter_url = chapter.a.get('href')
            chapter_name = chapter.get_text()
            self.chapter_names.insert(0, chapter_name)
            self.chapter_urls.insert(0, chapter_url)
    
    def _get_pic_urls(self, chapter_url):
        response = requests.get(chapter_url)
        html = BeautifulSoup(response.text, 'lxml')
        script_info = html.script
        pic_url_top = re.findall(r'\|(\d{4})\|', str(script_info))[0]
        pic_url_tail = re.findall(r'\|(\d{5})\|', str(script_info))[0]
        pics = re.findall(r'(\d{13,14})', str(script_info))
        for idx, pic in enumerate(pics):
            if len(pic) == 13:
                pics[idx] = pic + '0'
        pics = sorted(pics, key=lambda x: int(x))
        # print(pics)
        pic_urls = []
        for pic in pics:
            if pic[-1] == '0':
                pic_url = 'https://images.dmzj.com/img/chapterpic/' + pic_url_top + '/' + pic_url_tail + '/' + pic[:-1] + '.jpg'
            else:
                pic_url = 'https://images.dmzj.com/img/chapterpic/' + pic_url_top + '/' + pic_url_tail + '/' + pic + '.jpg'
            pic_urls.append(pic_url)
        return pic_urls

    def downloader(self, save_path):
        # 创建保存目录
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        
        # 获取漫画的章节名和链接信息 
        self._get_chapter_urls()
        print('开始下载漫画%s,总共有%s章节' % (save_path, len(self.chapter_names)))
        print('开始下载...........................................................')
        for chapter_name, chapter_url in zip(self.chapter_names, self.chapter_urls):
            # 获取每个章节 漫画的url
            pic_urls = self._get_pic_urls(chapter_url)

            chapter_save_path = os.path.join(save_path, chapter_name)
            if not os.path.exists(chapter_save_path):
                os.mkdir(chapter_save_path)

            # 每下载一个章节的漫画需要更换Referer，针对网站的反扒机制
            downloader_headers = {
                'Referer': chapter_url,
            }

            for idx, pic_url in enumerate(pic_urls, 1):
                pic_name = str(idx)+'.jpg'
                pic_path = chapter_save_path + '/' + pic_name
                res = requests.get(pic_url, headers=downloader_headers)
                if res.status_code == 200:
                    with open(pic_path, 'wb') as f:
                        f.write(res.content)
                else:
                    print("链接异常")
            print('%s  下载完成' % chapter_name)


if __name__ == '__main__':
    save_path = r'妖神记'
    # 创建类CartoonDownLoader的实例 cartoon
    cartoon = CartoonDownLoader()
    # 调用cartoon的下载函数开始下载
    cartoon.downloader(save_path)


