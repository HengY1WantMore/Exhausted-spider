import json
import re
import time
import requests
from urllib.parse import urlencode
from selenium import webdriver
from flashtext import KeywordProcessor
from selenium.webdriver.support.wait import WebDriverWait


def log(location, text):
    with open(location, "a+", encoding='utf-8') as f:
        f.write(text)


def judge_js(text):
    judge_fun = bool(re.search('function', str(text)))
    judge_p = bool(re.search('<p>', str(text)))
    if judge_fun and not judge_p:
        return True
    else:
        return False


class Selenium:
    def __init__(self, port, is_open, max_times, ip, page, record, black, black_want, source=None):
        self.source = source  # 搜索语法
        self.black = black  # 黑名单
        self.black_want = black_want  # 黑名单过滤词
        self.port = port  # 代理端口
        self.max_times = max_times  # 最大尝试次数
        self.is_open = is_open  # 是否开启代理,默认开启
        self.ip = ip  # 代理ip
        self.page = page  # 查看页数
        self.record = record  # 记录位置
        self.start = 0  # 拼凑翻页参数
        self.option = webdriver.ChromeOptions()
        self.option.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.option.add_argument('headless')  # 设置option
        self.browser = webdriver.Chrome(options=self.option)
        self.wait = WebDriverWait(self.browser, 10)

    def filter_url(self, url):  # 过滤有效链接
        domain = re.match(r'http.*?//(.*?)/.*?', url, re.M | re.I).group()
        if self.black is not None:
            black_list = []
            for k, v in self.black.items():
                black_list.append(v)
            for one_black in black_list:
                if one_black in domain:
                    return False
                else:
                    return True
        return True

    def get_url_info(self, page):
        self.start = page * 10
        res, real, repeat, final = [], [], [], []
        data = {'keyword': self.source}
        one = str(str(urlencode(data)).split('=')[1]).replace('%3A', ':') + (
            f'&start={str(self.start)}' if self.start != 0 else '')
        url = f"https://www.google.com.hk/search?q={one}"
        self.browser.get(url)  # 再打开新的一个
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
        for each in real:  # 过滤黑名单
            if self.filter_url(each):
                final.append(each)
        return final

    def get_each_page(self, url_want, times=1):  # 获取每一页的源码
        if times >= self.max_times:
            log('./record/error.txt', f"{url_want} 无法请求\n")
            return False
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
        try:
            if self.is_open:
                proxies = {
                    'http': f'http://{self.ip}:{self.port}',
                    'https': f'https://{self.ip}:{self.port}'
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
                return False
        except Exception as e:
            times += 1
            self.get_each_page(url_want, times)

    def parse_page(self, page):  # 该网页的源码中寻找是否存在过滤关键字
        keyword_processor = KeywordProcessor()
        filter_list = []
        for key, value in self.black_want.items():
            filter_list.append(value)
        for each in filter_list:
            keyword_processor.add_keyword(each)
        keywords_found = keyword_processor.extract_keywords(str(page))
        keywords_found = list(set(keywords_found))
        res_len = len(keywords_found)
        if res_len > 0:
            return False
        else:
            return True

    def get_page_info(self, page_url):  # 处理js渲染的链接
        try:
            self.browser.get(page_url)
            time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
            text = self.browser.page_source
            return self.parse_page(text)
        except Exception as e:
            log('./record/error.txt', f"处理js渲染的链接错误：{page_url}\n")
            return False

    def want_operation(self, black_want_flag):  # 单线程主程序
        for x in range(self.page):
            url_array = self.get_url_info(x)
            if not black_want_flag:
                info = dict()
                info['source'] = self.source
                info['page'] = x + 1
                info['url'] = dict(enumerate(url_array))
                print(f"The Mission {info['source']} page: {info['page']} is done")
                if info['url'] != {}:
                    log(self.record, str(json.dumps(info, ensure_ascii=False) + ',\n'))
                else:
                    continue
            else:
                sort_res = []
                for url_handle in url_array:
                    res = self.get_each_page(url_handle)
                    if res:
                        sort_res.append(url_handle)
                    info = dict()
                    info['source'] = self.source
                    info['page'] = x + 1
                    info['url'] = dict(enumerate(sort_res))
                print(f"The Mission {info['source']} page: {info['page']} is done")
                if info['url'] != {}:
                    log(self.record, str(json.dumps(info, ensure_ascii=False) + ',\n'))
                else:
                    continue


def thread_find(each, max_times, port, is_open, ip, pages, record):
    search_way = ''
    if 'key' in each.keys() and 'want' not in each.keys():
        key_str = ''
        value = each['key']
        for k, v in value.items():
            key_str += v
        search_way = key_str
    elif 'want' in each.keys() and 'key' not in each.keys():
        want_str = ''
        value = each['want']
        for k, v in value.items():
            want_str += v
        search_way = 'allintext:' + want_str
    elif 'key' in each.keys() and 'want' in each.keys():
        value_key = each['key']
        value_want = each['want']
        key_str = ''
        want_str = ''
        for k, v in value_key.items():
            key_str += v
        for k, v in value_want.items():
            want_str += v
        search_way = key_str + ' intext:' + want_str
    black_domain = each['black_domain'] if ('black_domain' in each.keys()) else None
    black_want = each['black_want'] if ('black_want' in each.keys()) else None
    Selenium(port, is_open, max_times, ip, pages, record, black_domain, black_want, search_way).want_operation(each['black_want_flag'])
