import requests
from multiprocessing import Pool
import json
import re
from requests.exceptions import RequestException


def get_one_page(url):
    # 添加header模拟浏览器请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '__mta=150384905.1582810902350.1582851008081.1582903763385.27; uuid_n_v=v1; uuid=E229D4F0596611EA8C59B911A475C6194043CEAFD70443CBB99565456091BB14; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1582810902,1582812465,1582903748,1582903754; _lxsdk_cuid=17086e1ae9dc8-0268096f3823d-4c302879-100200-17086e1ae9ec8; _lxsdk=E229D4F0596611EA8C59B911A475C6194043CEAFD70443CBB99565456091BB14; mojo-uuid=9e2f23e3eb876013213568b9c5d73808; __mta=150384905.1582810902350.1582851008081.1582903760911.27; _csrf=779a03a5d4d24cac5f331ac8fc925d5db0c65c86d1d00e61cf48519ee02402f3; mojo-trace-id=7; mojo-session-id={"id":"ca67840304fabcc8e5bcc706d2eadd1c","time":1582903747168}; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1582903763; _lxsdk_s=1708c6a661c-0b5-348-bf3%7C%7C11; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic',
        'Host': 'maoyan.com',
        'Referer': 'https://maoyan.com/board',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return "错误"
    except RequestException:
        print('请求失败')


def parse_one_page(html):
    # 正表达式匹配爬取的内容
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name">'
                         '<a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)'
                         '</p>.*?integer">(.*?)</i>.*?fraction">(\d)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    # 将列表定义成字典
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]

        }


# 写入文件操作
def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


# 多页爬取
def main(offset):
    url = 'https://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    for i in range(10):
        main(i * 10)
