import random
import re
import time
from urllib.parse import urlencode
import requests
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
import pymongo
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
proxy = None
proxy_pool_url = 'http://localhost:5555/random'
max_count = 5
base_url = 'https://weixin.sogou.com/weixin?'
keyword = '暨南大学'
headers = {
    'Cookie': 'IPLOC=CN4401; SUID=02A2EC78374A910A0000000060C4B4F8; SUV=1623504119771992; ABTEST=8|1623504121|v1; SNUID=2A85C4502822E3B6A55053C82870B8A3; weixinIndexVisited=1; JSESSIONID=aaaRaFUXgE9HF5XL9uHGx; ppinf=5|1623504399|1624713999|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlODElOTIlRTYlQUYlODV8Y3J0OjEwOjE2MjM1MDQzOTl8cmVmbmljazoxODolRTYlODElOTIlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA; pprdig=XZ3HxnAZSWiQhrg_1a3-nEZ3RlpJzKlZRHhCbONEVho3CSlowj1ZYUkk0JsJCZRF-XMoDbcPDAqCMzORqyPh4s6Tq2GcrL-R_MDunlvnTUKXDrCczbJ99inPchCal_760ZyjPwjCO2XMGCxH2VJcU2l_S-T_rDbyqqj-xy8Gax8; ppinfo=5242908421; passport=5|1623504399|1624713999|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlODElOTIlRTYlQUYlODV8Y3J0OjEwOjE2MjM1MDQzOTl8cmVmbmljazoxODolRTYlODElOTIlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA|d1b16715fc|XZ3HxnAZSWiQhrg_1a3-nEZ3RlpJzKlZRHhCbONEVho3CSlowj1ZYUkk0JsJCZRF-XMoDbcPDAqCMzORqyPh4s6Tq2GcrL-R_MDunlvnTUKXDrCczbJ99inPchCal_760ZyjPwjCO2XMGCxH2VJcU2l_S-T_rDbyqqj-xy8Gax8; sgid=14-52771287-AWDEtgibic6TKKib6tAQVbS0AA; ppmdig=1623504401000000ac830f8f0eb26cdf2f2c0f9ed4087b98',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.101 Safari/537.36 '
}
true_url = ''


def get_html(url, count=1):
    print('Crawing', url)
    # print('Trying Count', count)
    global proxy
    global max_count
    if count >= max_count:
        print('tried so many')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy,
                'https': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            proxy = get_proxy()
            if proxy:
                print('Using proxy', proxy)
                count += 1
                return get_html(url)
            else:
                print('Get proxy failed')
                return None
    except ConnectionError as e:
        print('Error', e)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)


def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')


def get_detail(url):
    global true_url
    header = {
        'Cookie': 'IPLOC=CN4401; SUID=02A2EC78374A910A0000000060C4B4F8; SUV=1623504119771992; ABTEST=8|1623504121|v1; weixinIndexVisited=1; JSESSIONID=aaaRaFUXgE9HF5XL9uHGx; ppinf=5|1623504399|1624713999|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlODElOTIlRTYlQUYlODV8Y3J0OjEwOjE2MjM1MDQzOTl8cmVmbmljazoxODolRTYlODElOTIlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA; pprdig=XZ3HxnAZSWiQhrg_1a3-nEZ3RlpJzKlZRHhCbONEVho3CSlowj1ZYUkk0JsJCZRF-XMoDbcPDAqCMzORqyPh4s6Tq2GcrL-R_MDunlvnTUKXDrCczbJ99inPchCal_760ZyjPwjCO2XMGCxH2VJcU2l_S-T_rDbyqqj-xy8Gax8; ppinfo=5242908421; passport=5|1623504399|1624713999|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlODElOTIlRTYlQUYlODV8Y3J0OjEwOjE2MjM1MDQzOTl8cmVmbmljazoxODolRTYlODElOTIlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA|d1b16715fc|XZ3HxnAZSWiQhrg_1a3-nEZ3RlpJzKlZRHhCbONEVho3CSlowj1ZYUkk0JsJCZRF-XMoDbcPDAqCMzORqyPh4s6Tq2GcrL-R_MDunlvnTUKXDrCczbJ99inPchCal_760ZyjPwjCO2XMGCxH2VJcU2l_S-T_rDbyqqj-xy8Gax8; sgid=14-52771287-AWDEtgibic6TKKib6tAQVbS0AA; PHPSESSID=hdttbdcme3s7flj265ov7ut9k2; SNUID=C0602FBBC3C706502026E720C3A338BA; ppmdig=16235128640000004856e4d423d6c56f7a899c23d07e120b'
    }
    b = int(random.random() * 100) + 1
    a = url.find("url=")
    result_url = url + "&k=" + str(b) + "&h=" + url[a + 4 + 21 + b: a + 4 + 21 + b + 1]
    url = "https://weixin.sogou.com" + result_url
    response_html = requests.get(url, headers=header).text.replace(' ', '')
    pattern = re.compile('url\+=\'(.*?);', re.S)
    items = re.findall(pattern, response_html)
    true_url = ''.join(items).replace('\'', '')
    try:
        response = requests.get(true_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def turn_time(time_stamp):
    timeStamp = int(time_stamp)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def parse_detail(html):
    doc = pq(html)
    title = doc('#activity-name').text()
    content = ''
    items = doc('.rich_media_content').items()
    for item in items:
        content += str(item.text()).replace('\n', '').replace('/', '').replace('\xa0', ' ')
    date = re.compile('var.*?",n="(.*?)",.*?"publish_time".*?', re.S)
    if re.findall(date, html):
        result = int(re.findall(date, html)[0])
        date = turn_time(result)
    nickname = doc('.rich_media_meta_list .rich_media_meta_nickname').text().split('\n')
    wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
    return {
        'url': true_url,
        'title': title,
        'content': content,
        'data': date,
        'nickname': nickname,
        'wechat': wechat
    }


def save_to_mongo(data):
    if db[MONGO_TABLE].update_one({'title': data['title']}, {'$set': data}, True):
        print('Saved', data['title'])
    else:
        print('Saved Failed', data['title'])


def main():
    for page in range(1, 20):
        html = get_index(keyword, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                get_detail(article_url)
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    save_to_mongo(article_data)


if __name__ == '__main__':
    main()