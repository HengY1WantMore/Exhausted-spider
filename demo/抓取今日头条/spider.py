from pyquery import PyQuery as pq
from urllib.parse import urlencode
import requests
from requests.exceptions import RequestException
from config import *
import pymongo


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def get_page_index(keyword, page_num):
    data = {
        'keyword': keyword,
        'pd': 'information',
        'source': 'aladdin',
        'dvpf': 'pc',
        'aid': 4916,
        'page_num': page_num,
        'search_json': '{"from_search_id": "202106111450480101510440281A111AAD"}'
    }
    url = 'https://so.toutiao.com/search?' + urlencode(data)
    response = requests.get(url)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求出错')
        return None


def parse_page_url(html):
    urls = []
    doc = pq(html)
    items = doc('.text-darker')
    a_s = items.find('a').items()
    for a in a_s:
        data = a.attr('href')
        url = 'https://so.toutiao.com' + data
        urls.append(url)
    return urls


def get_page_detail(url):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    }
    response = requests.get(url, headers=header)
    Location = response.history[1].headers['Location']
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'cookie': 'MONITOR_WEB_ID=ea59629f-01a6-439d-8874-cc8b7cd5753a; tt_webid=6972174752517834277; '
                  'ttcid=999598b8d4e041fd9f3430799ddd46fb40; csrftoken=4275442e0e2606d73174f88366a704f5; '
                  'tt_webid=6972174791597327884; _S_DPR=1; _S_IPAD=0; FRM=new; PIXIEL_RATIO=1; WIN_WH=1920_258; '
                  '_S_WIN_WH=1920_607; __ac_nonce=060c31ee100e439b83679; '
                  '__ac_signature=_02B4Z6wo00f01X3xdcwAAIDAqjdYtuVUaMV91XFAAD'
                  '.DoOUxpWK4q7ID81tjZ3dof5JEe5TXezk6bmCBsfBWp7dyIiEzVB'
                  '-oES80VpJSPZW2KaVLXyy158jscrGnT7bDVlzUhPHY2kjSrEKhef; '
                  's_v_web_id=verify_kps2nerm_BD5KmYF5_SpIY_40oU_Ax1O_uBMkzj9ilAY5; '
                  'ttwid=1%7CsvA4DAjzDo2S1tCI3XlLmW8UXaVg70o-H-NKvnoBlpY%7C1623400346'
                  '%7C40078901d5dd652c35345368cee2611f90d66189a7e0069c7d823173d401441c; '
                  'tt_scid=58wlylcC46FFZhmNU6KavcoEwTcrcIWcItR6lOB9jYgqMiXRQRvix479F6hQsk4gba2c '
    }
    response = requests.get(Location, headers=header)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求出错')
        return None


def parse_page_detail(html, url):
    images = []
    doc = pq(html)
    title_str = doc('title').text().split()[0]
    img_s = doc.find('img').items()
    for img in img_s:
        data = img.attr('src')
        begin = data[:5]
        if begin == 'https':
            images.append(data)
    images = ('images', str(images))
    title = ('title', title_str)
    url = ('url', url)
    result = dict([title, url, images])
    return result


def save_to_mongo(result):
    if db[MONGO_TABLE].insert_one(result):
        print('存储成功', result)
        return True
    return False


def main():
    html = get_page_index('街拍', 0)
    urls = parse_page_url(html)
    html_detail = get_page_detail(urls[0])
    result = parse_page_detail(html_detail, urls[0])
    save_to_mongo(result)


if __name__ == '__main__':
    main()
