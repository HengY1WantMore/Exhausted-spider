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
    news_1 = res[0]
    news_2 = res[1]
    now =search_time()
    sql = f"INSERT INTO `hengyi_service`.`daily_news` (`date`, `num_1`, `num_2`, `num_3`, `num_4`, `num_5`, `num_6`, `num_7`, `num_8`, `num_9`, `num_10`, `num_11`, `num_12`, `num_13`, `num_14`, `num_15`, `num_16`, `num_17`, `num_18`, `num_19`, `num_20`, `num_21`, `num_22`, `num_23`, `num_24`) VALUES ('{now}', '{news_1[0]}', '{news_1[1]}', '{news_1[2]}', '{news_1[3]}', '{news_1[4]}', '{news_1[5]}', '{news_1[6]}', '{news_1[7]}', '{news_1[8]}', '{news_1[9]}', '{news_1[10]}', '{news_1[11]}', '{news_2[0]}', '{news_2[1]}', '{news_2[2]}', '{news_2[3]}', '{news_2[4]}', '{news_2[5]}', '{news_2[6]}', '{news_2[7]}', '{news_2[8]}', '{news_2[9]}', '{news_2[10]}', '{news_2[11]}')"
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
    cookie_one = 'IPLOC=CN4401; SUID=02A2EC78374A910A0000000060C4B4F8; SUV=1623504119771992; ABTEST=8|1623504121|v1; weixinIndexVisited=1; ppinf=5|1623757982|1624967582|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlODElOTIlRTYlQUYlODV8Y3J0OjEwOjE2MjM3NTc5ODJ8cmVmbmljazoxODolRTYlODElOTIlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA; pprdig=xXJ8dwJX-d7kpfVUb-G5_LHJeknha--oX_2rNy17LQWbJ1dxNCX7wF89ZOW5l7L2HAhcBweQOURAmw3o5UmmV10ovram4LgQ9dPCEbxODzbGwpGEJMJ1L4XpSopb2KIsxREqDm299olSZ-s3CoMURbXIjMrP3B8Bn6vTBvNqgKc; ppinfo=fa4abf89cb; passport=5|1623757982|1624967582|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTYlODElOTIlRTYlQUYlODV8Y3J0OjEwOjE2MjM3NTc5ODJ8cmVmbmljazoxODolRTYlODElOTIlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA|a4347c7cf5|xXJ8dwJX-d7kpfVUb-G5_LHJeknha--oX_2rNy17LQWbJ1dxNCX7wF89ZOW5l7L2HAhcBweQOURAmw3o5UmmV10ovram4LgQ9dPCEbxODzbGwpGEJMJ1L4XpSopb2KIsxREqDm299olSZ-s3CoMURbXIjMrP3B8Bn6vTBvNqgKc; sgid=14-52771287-AWDIlJ4VBIA4wkjcv9dXFDE; SNUID=1ABBF461181CDCD4879BC8DA199F54AB; ld=nkllllllll2khGcQlllllpRw8AUlllllnsA80kllllGlllllRZlll5@@@@@@@@@@; LCLKINT=5577; LSTMV=294%2C155; ppmdig=16238368370000007f27d59ae365f472538120d7406eca0a'
    main('365简报', 1, cookie_one)