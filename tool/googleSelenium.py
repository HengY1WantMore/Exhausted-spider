import re
import time
import requests
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from common import match_url
from common import log
from common import judge_js
from flashtext import KeywordProcessor

browser = webdriver.Chrome('/Users/hengyi/Desktop/chromedriver')
# browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


class Selenium:
    def __init__(self, index, key, want: list, num, withe: list, black: list, length=None, is_open=1, max_times=3):
        self.index = index  # 下标
        self.key = key  # 搜索的关键字
        self.want = want  # 想找的关键词
        self.num = num  # 接受的最少存在的关键词个数
        self.withe = withe  # 白名单
        self.black = black  # 黑名单
        self.length = length  # 默认为筛选的全部
        self.max_times = max_times  # 最大尝试次数
        self.is_open = is_open  # 是否开启代理,默认开启

    def get_all_info(self):  # 模拟浏览器请求
        data = {'keyword': self.key}
        one = str(urlencode(data)).split('=')[1]
        browser.get('https://www.google.com.hk/search?q=' + one)
        time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
        p = browser.find_elements_by_css_selector('.g')
        for x in p:
            content = str(str(x.text).split('\n')).replace('\'', '')
            url = match_url(content)
            log('./record.txt', f"该网址为：{url} 详细信息为：{content}\n")
        return True

    def filter_url(self, url, want):  # 过滤有效链接
        domain = re.match(r'http.*?//(.*?)/.*?', url, re.M | re.I).group()
        if want == 0:
            for one_black in self.black:
                if one_black in domain:
                    return False
            return True
        elif want == 1:
            for one_withe in self.withe:
                if one_withe in domain:
                    return True
            return False

    def get_url_info(self):  # 谷歌搜索页面存在的有效链接
        res, real, repeat, final = [], [], [], []
        data = {'keyword': self.key}
        one = str(urlencode(data)).split('=')[1]
        browser.get('https://www.google.com.hk/search?q=' + one)
        time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
        text = browser.find_elements_by_xpath("//a")  # 拿到该页所有的链接
        for each in text:
            url = each.get_attribute("href")  # 具体链接
            if not bool(re.search('google', str(url))) and url is not None:
                res.append(url)
        for each in res:  # 黑名单筛选
            if self.filter_url(each, 0):
                real.append(each)
        for each in real:  # 重复筛选
            repeat.append(re.match(r'http.*?//(.*?)/.*?', each, re.M | re.I).group())
        repeat = list(set(repeat))
        for each in real:
            if re.match(r'http.*?//(.*?)/.*?', each, re.M | re.I).group() in repeat:
                final.append(each)
                repeat.pop(repeat.index(re.match(r'http.*?//(.*?)/.*?', each, re.M | re.I).group()))
        return final[:self.length]

    def get_each_page(self, url_want, times=1):  # 获取每一页的源码
        if times == self.max_times:
            log('./error.txt', f"{url_want} 无法请求\n")
            return False
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
        try:
            if self.is_open == 1:
                proxies = {
                    'http': 'http://127.0.0.1:7890',
                    'https': 'https://127.0.0.1:7890'
                }
                response = requests.get(url_want, proxies=proxies, headers=header, timeout=5)  # 使用代理
            else:
                response = requests.get(url_want, headers=header, timeout=5)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                if judge_js(response.text):
                    return self.get_page_info(url_want)
                else:
                    return self.parse_page(response.text)
            else:
                log('./error.txt', f"请求非200：{url_want}\n")
                return False
        except Exception as e:
            times += 1
            self.get_each_page(url_want, times)

    def parse_page(self, page):  # 该网页的源码中寻找是否存在关键字
        keyword_processor = KeywordProcessor()
        for each in self.want:
            keyword_processor.add_keyword(each)
        keywords_found = keyword_processor.extract_keywords(str(page))
        keywords_found = list(set(keywords_found))
        res_len = len(keywords_found)
        if res_len < self.num:
            return False
        else:
            return True

    def get_page_info(self, page_url):  # 处理js渲染的链接
        try:
            browser.get(page_url)
            time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
            text = browser.page_source
            return self.parse_page(text)
        except Exception as e:
            log('./error.txt', f"处理js渲染的链接错误：{page_url}\n")
            return False

    def want_operation(self):
        final_res = []
        sort_res = []
        log('./record.txt', f"{self.index}\n")
        url_array = self.get_url_info()
        for url_handle in url_array:
            res = self.get_each_page(url_handle)
            if res:
                sort_res.append(url_handle)
        for sort in sort_res:  # 白名单排序
            if self.filter_url(sort, 1):
                final_res.append(sort)
                sort_res.pop(sort_res.index(sort))
        for sort in sort_res:
            final_res.append(sort)
        for url_handle in final_res:
            log('./record.txt', f"{url_handle}\n")
        log('./record.txt', f"--##########################################\n")


if __name__ == '__main__':
    # 默认黑白名单
    white_list = [
        'facebook',  # 脸书
        'youtube'  # 油管
    ]
    black_list = [
        'sohu',  # 搜狐
        'taobao'
    ]
    Selenium(2, '淘宝', ['logo', '服装'], 2, white_list, black_list).want_operation()


