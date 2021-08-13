from pyquery import PyQuery as pq
from urllib.parse import urlencode
import requests
from common import log


class wiki:
    def __init__(self, index, key, max_times):
        self.index = index  # 请求下标
        self.key = key  # 请求关键词
        self.max_times = max_times  # 外网代理最多尝试的次数
        self.res = dict()

    def get_page(self, times=1):  # 进行维基百科请求
        if times >= self.max_times:
            log('record.txt', f"Error! {self.key} 脚本无法请求 \n")
            return ''
        data = {
            'keyword': self.key,
        }
        one = str(urlencode(data)).split('=')[1]
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
        proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'https://127.0.0.1:7890'
        }
        url = 'https://zh.wikipedia.org/wiki/' + one
        try:
            response = requests.get(url, proxies=proxies, headers=header)  # 使用代理
            if response.status_code == 200:
                return response.text
        except Exception as e:
            times += 1
            self.get_page(times)

    def parse_page(self):  # 分析页面
        page = self.get_page()
        try:
            doc = pq(page)
            directory_info = doc('.toc').text().replace('\n', ' ')
            labels = doc('.mw-parser-output p').text()
            self.res['labels'] = labels
            self.res['directory_info'] = directory_info
            return self.res
        except Exception as e:
            self.res['labels'] = '错误'
            self.res['directory_info'] = '错误'
            return self.res
