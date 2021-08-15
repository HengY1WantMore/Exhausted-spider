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

# browser = webdriver.Chrome('/Users/hengyi/Desktop/chromedriver')
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


class Selenium:
    def __init__(self, key, want, is_open=0, max_times=3):
        self.key = key  # 搜索的关键字
        self.max_times = max_times  # 最大尝试次数
        self.is_open = is_open  # 是否开启代理
        self.want = want  # 想找的关键词

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

    def get_url_info(self):  # 谷歌搜索页面存在的有效链接
        res = []
        data = {'keyword': self.key}
        one = str(urlencode(data)).split('=')[1]
        browser.get('https://www.google.com.hk/search?q=' + one)
        time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
        text = browser.find_elements_by_xpath("//a")
        for each in text:
            url = each.get_attribute("href")
            if not bool(re.search('google', str(url))) and url is not None:
                res.append(url)
        return res

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
        keyword_processor.add_keyword(self.want)
        keywords_found = keyword_processor.extract_keywords(str(page))
        if not keywords_found:
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

    def main_operation(self):
        log('./record.txt', f"当前进行为：{self.key}\n")
        url_array = self.get_url_info()
        for url_handle in url_array:
            res = self.get_each_page(url_handle)
            if res:
                log('./record.txt', f"获取到 {url_handle} 中存在关键字:{self.want}\n")
        log('./record.txt', f"##########################################\n")


if __name__ == '__main__':
    Selenium('淘宝', 'logo', 1).main_operation()
