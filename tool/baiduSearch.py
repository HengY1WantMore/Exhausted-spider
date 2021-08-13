import re
from urllib.parse import urlencode
import requests
from requests import RequestException
from pyquery import PyQuery as pq
from xpinyin import Pinyin
from common import location_index
from common import log


class baidu:
    def __init__(self, index, name, key_array, bottom_year=1900):
        self.name = name  # 搜索人物姓名
        self.index = index  # 搜索人物下标
        self.key_array = key_array  # 关键词数组
        self.bottom_year = bottom_year  # 过滤年限 默认1900
        self.res = dict()  # 结果为一个空字典

    def get_page(self):  # 百度百科请求人物页面
        data = {
            'keyword': self.name,
        }
        name_encode = str(urlencode(data)).split('=')[1]
        url = 'https://baike.baidu.com/item/' + name_encode
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
        response = requests.get(url, headers=header)
        try:
            if response.status_code == 200:
                return response.text.replace('&nbsp;', '')
        except RequestException:
            print('请求出错')
            return None

    def filter_year(self):  # 过滤年份
        if '出生日期' in self.res:
            match = '(.*?)年(.*?)月(.*?)日'  # 处理存在年月日的
            results = re.findall(match, self.res['出生日期'], re.S)
            if results:
                results = list(results[0])
                results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
                results[2] = results[2] if len(results[2]) == 2 else '0' + results[2]
                self.res['出生日期'] = results[0] + '/' + results[1] + '/' + results[2]
                return self.res
            match = '(.*?)年(.*?)月'  # 处理存在年月的
            results = list(re.findall(match, self.res['出生日期'], re.S))
            if results:
                results = list(results[0])
                results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
                self.res['出生日期'] = results[0] + '/' + results[1] + '/00'
                return self.res
            match = '(.*?)年'  # 处理存在年的
            results = list(re.findall(match, self.res['出生日期'], re.S))
            if results:
                self.res['出生日期'] = results[0] + '/00/00'
            year = self.res['出生日期'].split('/')[0]
            if len(year) != 4:
                log('./error.txt', f"{self.name} 年份格式错误，待处理 \n")
                print(f"{self.name} 年份格式错误，待处理")
                return self.res
            else:  # 过滤一定的年份
                if int(year) <= self.bottom_year:
                    log('error.txt', f"{self.name} 百度百科年份不匹配 \n")
                    print(f"{self.name} 百度百科年份不匹配")
                    self.res = {}
                    return self.res

    def handle_name(self):  # 处理英文名字
        if '外文名' not in self.res and '外文名' in self.key_array:
            p = Pinyin()
            s = p.get_pinyin(self.name).split('-')
            self.res['外文名'] = s[0].capitalize() + ' ' + ''.join(s[1:]).capitalize()
            self.res['外文名'] = self.res['外文名'].replace(' ', '')
            return self.res

    def parse_page(self):  # 分析页面(主方法)
        page = self.get_page()
        doc = pq(page)
        info_left = doc('.basicInfo-block.basicInfo-left').text().replace('\n', ',').split(',')
        group = [info_left[i:i + 2] for i in range(0, len(info_left), 2)]
        for one in group:
            index = location_index(self.key_array, one[0])
            if index != -1:
                self.res[one[0]] = one[1]
        info_right = doc('.basicInfo-block.basicInfo-right').text().replace('\n', ',').split(',')
        group = [info_right[i:i + 2] for i in range(0, len(info_right), 2)]
        for one in group:
            index = location_index(self.key_array, one[0])
            if index != -1:
                self.res[one[0]] = one[1]
        self.res = self.handle_name()
        self.res = self.filter_year()
        return self.res
