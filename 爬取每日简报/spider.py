import random
import re
from urllib.parse import urlencode
from pyquery import PyQuery as pq
import requests
from config import *

proxy = None
proxy_pool_url = 'http://47.99.140.252:5555/random'
max_count = 5
base_url = 'https://weixin.sogou.com/weixin?'
true_url = ''


def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


def get_html(url, cookie, count=1):
    global proxy
    global max_count
    headers = {
        'Cookie': cookie,
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.101 Safari/537.36 '
    }
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
                return get_html(url, cookie)
            else:
                print('Get proxy failed')
                return None
    except ConnectionError as e:
        print('Error', e)
        proxy = get_proxy()
        count += 1
        return get_html(url, cookie, count)


def get_index(keyword, page, cookie):
    data = {
        'query': keyword,
        'type': 1,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url, cookie)
    return html


def parse_index(html):
    doc = pq(html)
    zixun = doc('#sogou_vr_11002301_box_0 > dl:nth-child(3) > dd > a').attr('href')
    weiyu = doc('#sogou_vr_11002301_box_1 > dl:nth-child(3) > dd > a').attr('href')
    return [zixun, weiyu]


def get_detail(url, cookie):
    global true_url
    header = {
        'Cookie': cookie
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
        content += str(item.text()).replace('\n', '').replace('/', '').replace('\xa0', ' ')+' / '
    date = re.compile('var.*?",n="(.*?)",.*?"publish_time".*?', re.S)
    if re.findall(date, html):
        result = int(re.findall(date, html)[0])
        date = turn_time(result)
    nickname = doc('.rich_media_meta_list .rich_media_meta_nickname').text().split('\n')
    wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
    return {
        # 'url': true_url,
        'title': title,
        'data': date,
        'content': content,
        'nickname': nickname,
        # 'wechat': wechat
    }


def handle_result(res: list):
    results = str(res).replace('[公众号：365资讯简报]', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace("'", '').split(',')
    return results


def save_to_mysql(res):
    res = str(res).replace('[','').replace(']', '').replace('(', '').replace(')', '').replace("'", '').replace(" ", '').replace(",", '')
    now =search_time()[:10]
    print(res)
    sql = f"INSERT INTO `hengyi_service`.`daily_news` (`date`, `content`) VALUES ('{now}', '{res}')"
    conn = mysqlConnection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print(f"插入成功")


def main(keyword, page, cookie):
    res_all = []
    html = get_index(keyword, page, cookie)
    if html:
        article_urls = parse_index(html)
        for article_url in article_urls:
            article_html = get_detail(article_url, cookie)
            if article_html:
                article_data = parse_detail(article_html)
                content = article_data['content']
                results = re.findall(".*?星期.*?1、(.*?)2、(.*?)3、(.*?)4、(.*?)5、(.*?)6、(.*?)7、(.*?)8、(.*?)9、(.*?)10、(.*?)11、(.*?)12、(.*?)。", content, re.S)
                res_all.append(handle_result(results))
    print(res_all)
    save_to_mysql(res_all)


if __name__ == '__main__':
    cookie_one = '#'
    main('365简报', 1, cookie_one)