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
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait as thread_wait

# executable_path = '/Users/hengyi/Desktop/chromedriver'
all_info = []


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
        self.protect = []  # 白名单的保护名单（即使打不开任然保存）
        # option = webdriver.ChromeOptions()
        # option.add_argument('headless')  # 设置option
        # self.browser = webdriver.Chrome(options=option)  # 申请一个浏览器
        self.browser = webdriver.Chrome()  # 申请一个浏览器
        self.wait = WebDriverWait(self.browser, 10)  # 浏览器等待时间

    def get_all_info(self):  # 模拟浏览器请求
        data = {'keyword': self.key}
        one = str(urlencode(data)).split('=')[1]
        self.browser.get('https://www.google.com.hk/search?q=' + one)
        time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
        p = self.browser.find_elements_by_css_selector('.g')
        for info_one in p:
            content = str(str(info_one.text).split('\n')).replace('\'', '')
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

    def get_url_info(self):  #
        res, real, repeat, final = [], [], [], []
        data = {'keyword': self.key}
        one = str(urlencode(data)).split('=')[1]
        self.browser.get(f"https://www.google.com.hk/search?q={one}")
        time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
        text = self.browser.find_elements_by_xpath("//a")  # 拿到该页所有的链接
        for each in text:  # 具体链接
            url = each.get_attribute("href")
            if not bool(re.search('google', str(url))) and url is not None:
                res.append(url)
        for each in res:  # 重复筛选
            repeat.append(re.match(r'http.*?//(.*?)/.*?', each, re.M | re.I).group())
        repeat = list(set(repeat))
        for each in res:
            if re.match(r'http.*?//(.*?)/.*?', each, re.M | re.I).group() in repeat:
                real.append(each)
                repeat.pop(repeat.index(re.match(r'http.*?//(.*?)/.*?', each, re.M | re.I).group()))
        for each in real:  # 白黑名单筛选
            if self.filter_url(each, 1):
                self.protect.append(each)
                real.pop(real.index(each))
        for each in real:
            if self.filter_url(each, 0):
                final.append(each)
        return final[:self.length]

    def get_each_page(self, url_want, times=1):  # 获取每一页的源码
        if times == self.max_times:
            log('./error.txt', f"{self.index} {self.key}{url_want} 无法请求\n")
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
                log('./error.txt', f"{self.index} {self.key} 请求非200：{url_want}\n")
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
            self.browser.get(page_url)
            time.sleep(1)  # 2秒的休眠给网络一个缓冲时间
            text = self.browser.page_source
            return self.parse_page(text)
        except Exception as e:
            log('./error.txt', f"{self.index} {self.key} 处理js渲染的链接错误：{page_url}\n")
            return False

    def want_operation(self):  # 单线程主程序
        sort_res = []
        url_array = self.get_url_info()
        for url_handle in url_array:
            res = self.get_each_page(url_handle)
            if res:
                sort_res.append(url_handle)
        all_info.append({'index': self.index, 'res': sort_res, 'protect': self.protect})
        log('./record.txt', f"{self.index}\n")
        for url_handle in sort_res:
            log('./record.txt', f"{url_handle}\n")
        for url_protect in self.protect:
            log('./record.txt', f"{url_protect}\n")
        log('./record.txt', f"--##########################################\n")


def multithreading(info):
    Selenium(info['index'], info['key'], info['want'], info['num'], info['withe'], info['black']).want_operation()
    print(f"下标为：{info['index']}, {info['key']} 完成")


# 希尔排序
def shellSort(all_info_list):
    length = len(all_info_list)
    gap = length // 2
    while gap >= 1:
        for i in range(length):
            j = i
            while j >= gap and all_info_list[j - gap]['index'] > all_info_list[j]['index']:  # 在每一组里面进行直接插入排序
                all_info_list[j], all_info_list[j - gap] = all_info_list[j - gap], all_info_list[j]
                j -= gap
        gap = gap // 2  # 更新步长
    return all_info_list


if __name__ == '__main__':
    # 参数模块
    white_list = [
        'facebook',  # 脸书
        'youtube'  # 油管
    ]
    black_list = [
        'sohu',  # 搜狐
        'taobao'
    ]
    length = None
    is_open = 1
    max_times = 3
    # 列表模块
    list_info = ['俄罗斯中华文化教育促进会', '阿根廷华文教育基金会', '南非中文教师协会', '中韩子女教育协会', '德国华达中文学校', '内卡河畔华文学堂', '全美中文学校协会']
    print('Mission Start')
    executor = ThreadPoolExecutor(max_workers=5)
    f_list = []
    for index, each_index in enumerate(list_info):
        one_info = {
            'index': index,
            'key': each_index,
            'want': ['logo'],
            'num': 1,
            'withe': white_list,
            'black': black_list,
            'length': length,
            'is_open': is_open,
            'max_times': max_times,
        }
        future = executor.submit(multithreading, one_info)
        f_list.append(future)
    thread_wait(f_list)
    # 进行重新排序
    all_info = shellSort(all_info)
    for each_one in all_info:
        log('./record_sort.txt', f"{each_one['index']}\n")
        for url_handle in each_one['res']:
            log('./record_sort.txt', f"{url_handle}\n")
        for url_protect in each_one['protect']:
            log('./record_sort.txt', f"{url_protect}\n")
        log('./record_sort.txt', f"--##########################################\n")
    print('Mission Over')
