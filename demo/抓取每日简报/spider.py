import random
import re
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPException
from urllib.parse import urlencode
import pymysql
from pyquery import PyQuery as pq
import requests

proxy = None
proxy_pool_url = 'https://hengyimonster.top/proxypool'
base_url = 'https://weixin.sogou.com/weixin?'
code = ''


# 分析页面
def parse_detail(html):
    doc = pq(html)
    content = ''
    items = doc('.rich_media_content').items()
    for item in items:
        content += str(item.text()).replace('\n', '').replace('/', '').replace('\xa0', ' ') + ' / '
    return content


def mysqlConnection(host='112.74.55.247', user='hengyi', passwd='kG7aiFMyJLDFCTdf', db='hengyi_service'):
    conn = pymysql.Connect(
        host=host,
        port=3306,
        user=user,
        passwd=passwd,
        db=db,
        charset='utf8')
    return conn


def send(text):
    """
    :param text: 邮件文本
    :return:
    """
    subject = f'每日新闻更新错误'
    sender = '2911567026@qq.com'  # 发件人邮箱
    receivers = '2911567026@qq.com'  # 收件人邮箱

    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receivers  # 处理多人邮箱
    content = MIMEText(text)
    message.attach(content)

    try:
        server = SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, "ivgovarvmzrldgdj")  # 授权码
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
    except SMTPException as e:
        print("发送邮件失败", e)


def handle_result(res: list):
    results = str(res).replace('[公众号：365资讯简报]', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace("'", '').split(',')
    return results


def search_time():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return now


def save_to_mysql(res, id):
    try:
        res = str(res).replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace("'", '').replace(" ", '').replace(",", '')
        now = search_time()[:10]
        sql = f"INSERT INTO `hengyi_service`.`daily_news` (`date`, `content`, `type`) VALUES ('{now}', '{res}', '{id}')"
        conn = mysqlConnection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)


class WeixinSpider:
    def __init__(self, key, cookie, type=2, max_count=3, error=''):
        self.key = key  # 搜索的关键词
        self.cookie = cookie  # 定时更新的cookie
        self.type = type  # 默认位搜索公众号
        self.max_count = max_count  # 最大重试次数
        self.error = error  # 错误消息
        self.true_url = ''  # 微信内部的url

    # 请求内容
    def get_html(self, url, count=1):
        global proxy
        headers = {
            'Cookie': self.cookie,
            'Host': 'weixin.sogou.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.101 Safari/537.36 '
        }
        if count >= self.max_count:
            self.error = 'tried so many'
            return None
        try:
            if proxy:
                proxies = {
                    'http': 'http://' + proxy,
                    'https': 'http://' + proxy
                }
                response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
            else:
                response = requests.get(url, allow_redirects=False, headers=headers)
            if response.status_code == 200:
                return response.text
            if response.status_code == 302:
                proxy = self.get_proxy()
                if proxy:
                    print('Using proxy', proxy)
                    count += 1
                    return self.get_html(url, count)
                else:
                    self.error = 'Get proxy failed'
                    return None
        except ConnectionError as e:
            self.error = 'Error 获取页面'
            proxy = self.get_proxy()
            count += 1
            return self.get_html(url, count)

    # 处理代理
    def get_proxy(self):
        try:
            response = requests.get(proxy_pool_url)
            if response.status_code == 200:
                return response.text
        except ConnectionError:
            self.error = 'Get proxy failed'
            return None

    # 拿到默认的第一页
    def get_index_html(self, page=1):
        data = {
            'query': self.key,
            'type': type,
            'page': page
        }
        queries = urlencode(data)
        url = base_url + queries
        html = self.get_html(url)
        return html

    # 分析页面
    def parse_page(self, html):
        doc = pq(html)
        items = doc('.news-list2 li .gzh-box2 .txt-box').text().replace('\n', ' ').split(' ')
        if self.key in items:
            index = int(items.index(self.key) / 2)
        else:
            return -1
        a = doc(f"#sogou_vr_11002301_box_{index} > dl:nth-child(3) > dd > a").attr('href')
        return a

    # 拿到目标源码
    def get_detail(self, url):
        header = {
            'Cookie': self.cookie
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
            else:
                return -1
        except Exception as e:
            self.error = '请求微信错误'
            return -1

    # 主操作函数
    def main_spider(self):
        global code
        try:
            html = self.get_index_html()
            if html:
                a = self.parse_page(html)
                if a == -1:
                    self.error = '分析页面错误'
                else:
                    text = self.get_detail(a)
                    if text == -1:
                        self.error = '获取页面源码错误'
                    else:
                        content = parse_detail(text)
                        results = re.findall(
                            ".*?星期.*?1、(.*?)2、(.*?)3、(.*?)4、(.*?)5、(.*?)6、(.*?)7、(.*?)8、(.*?)9、(.*?)10、(.*?)11、(.*?)12、(.*?)。",
                            content, re.S)
                        return handle_result(results)
        except Exception as e:
            code += f"原因为：{self.error}；报错为：{e}"


if __name__ == "__main__":
    cookie = 'IPLOC=CN4401; SUID=02A2EC78374A910A0000000060C4B4F8; SUV=1623504119771992; weixinIndexVisited=1; ABTEST=0|1626703789|v1; ppinf=5|1628762979|1629972579|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyMTolRTYlODElOTIlMjAlRTYlQUYlODV8Y3J0OjEwOjE2Mjg3NjI5Nzl8cmVmbmljazoyMTolRTYlODElOTIlMjAlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA; pprdig=QT1EWAFoGKjaN_hGOYXCxMWaR-bhV0Jc-v-gGwTCY46x1YSRddyFAiLAQ82XkiMvkiJx-55IjbwdDwOEr2Hy0NjXBgwh9ahhRRvD26xc2eoURlkXw0Tz91T_cUByqA4RarkWQeqaLM04XH9kq_JqTDVps7gCC4rioj_bc61-juk; ppinfo=f846e9aeb6; passport=5|1628762979|1629972579|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyMTolRTYlODElOTIlMjAlRTYlQUYlODV8Y3J0OjEwOjE2Mjg3NjI5Nzl8cmVmbmljazoyMTolRTYlODElOTIlMjAlRTYlQUYlODV8dXNlcmlkOjQ0Om85dDJsdUp6NHhVMGdVVW1ad0xwc3ZES2xHdm9Ad2VpeGluLnNvaHUuY29tfA|a44b013b5e|QT1EWAFoGKjaN_hGOYXCxMWaR-bhV0Jc-v-gGwTCY46x1YSRddyFAiLAQ82XkiMvkiJx-55IjbwdDwOEr2Hy0NjXBgwh9ahhRRvD26xc2eoURlkXw0Tz91T_cUByqA4RarkWQeqaLM04XH9kq_JqTDVps7gCC4rioj_bc61-juk; sgid=14-52771287-AWEU82PKwnvMPMbOAV875Hs; SNUID=92034FDAA3A66B35C706165AA30FAC25; ppmdig=1629036179000000ad9615c64ff19008c3b434288df9eebf; JSESSIONID=aaa6OnasWQ8xR6dmGZhTx'

    def main(count=1):
        global code
        if count >= 3:
            send(code)
            exit()
        try:
            # 爬虫
            flag1 = WeixinSpider('每日微语简报', cookie).main_spider()
            time.sleep(1)
            flag2 = WeixinSpider('365微语简报', cookie).main_spider()
            # 处理每日微语简报
            handle = flag1[-1].replace('13、', '').replace('14、', '').replace('15、', '').split('；')[:-1]
            for extend in handle:
                flag1.append(extend)
            # 保存信息
            save_to_mysql(str(flag1), 0)
            save_to_mysql(str(flag2), 1)
            print('mission over')
        except Exception as e:
            count += 1
            code += f"发生在main函数中，报错原因为：{e}"
            main(count)
    main()



