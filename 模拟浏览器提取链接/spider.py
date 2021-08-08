import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlencode
import requests
import time


max_times = 3
browser = webdriver.Chrome('/Users/hengyi/Desktop/chromedriver')
# browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


# @description: 匹配所有符合的链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: info:文本
# @Return: array
def match_all_url(info):
    try:
        match = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
        pattern = re.compile(match)
        result = pattern.findall(info)
        return result
    except Exception as e:
        return -1


# @description: 匹配图片链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: info:文本
# @Param: key:关键字
# @Return: array
def match_all_image(info, key):
    res = []
    pattern1 = '.*?{0}.*?url: "(http.*?jpg)"'
    pattern2 = '.*?{0}.*?{url: "(http.*?webp)"'
    pattern3 = '.*?{0}.*?{url: "(http.*?gif)"'
    pattern4 = '.*?{0}.*?{url: "(http.*?ico)"'
    pattern5 = '.*?{0}.*?g{url: "(http.*?png)"'
    pattern6 = '.*?{0}.*?<img src="(http.*?jpg)".*?'
    pattern7 = '.*?{0}.*?<img src="(http.*?webp)".*?'
    pattern8 = '.*?{0}.*?<img src="(http.*?gif)".*?'
    pattern9 = '.*?{0}.*?<img src="(http.*?ico)".*?'
    pattern10 = '.*?{0}.*?<img src="(http.*?png)".*?'
    pattern11 = '.*?{0}.*?<a.*?href="(http.*?jpg)".*?'
    pattern12 = '.*?{0}.*?<a.*?href="(http.*?webp)".*?'
    pattern13 = '.*?{0}.*?<a.*?href="(http.*?gif)".*?'
    pattern14 = '.*?{0}.*?<a.*?href="(http.*?ico)".*?'
    pattern15 = '.*?{0}.*?<a.*?href="(http.*?png)".*?'
    rule = [
        pattern1, pattern2, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8,
        pattern9, pattern10, pattern11, pattern12, pattern13, pattern14, pattern15
    ]
    try:
        for x in rule:
            x = x.format(key)
            pattern = re.compile(x, re.I)
            result = pattern.findall(info)
            for y in result:
                res.append(y)
        return res
    except Exception as e:
        return -1


# @description: 谷歌请求某页面中含有的链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: want:搜索内容
# @return array
def get_info(want):
    res = []
    data = {'keyword': want}
    one = str(urlencode(data)).split('=')[1]
    browser.get('https://www.google.com.hk/search?q=' + one)
    time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
    text = browser.find_elements_by_xpath("//a")
    for each in text:
        url = each.get_attribute("href")
        if not bool(re.search('google', str(url))) and url is not None:
            res.append(url)
    return res


# @description: 进行维基百科请求
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: url_want:链接
# @Return: mixed
def get_each_page(url_want, times = 1):
    if times >= max_times:
        print(f"{url_want} 无法请求 ，请及时处理")
        return False
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    if bool(re.search('http', str(url_want))):  # 则是http请求
        proxies = {'http': 'http://127.0.0.1:7890'}
    else:
        proxies = {'https': 'http://127.0.0.1:7890'}
    try:
        response = requests.get(url_want, proxies=proxies, headers=header)  # 使用代理
        if response.status_code == 200:
            if judge_js(response.text):
                return -1
            else:
                return response.text
    except Exception as e:
        times += 1
        return get_each_page(url_want, times)


# @description: 分析页面是不是js渲染
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: text:网页内容
# @Return: boolean
def judge_js(text):
    judge_fun = bool(re.search('function()', str(text)))
    judge_div= bool(re.search('div', str(text)))
    judge_p = bool(re.search('p', str(text)))
    if judge_fun and not judge_p and not judge_div:
        return True
    else:
        return False


# @description: 分析页面所有存在的链接/图片地址
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: page:网页内容
# @Return: array
def parse_page(page, type, key=''):
    if type == 0:
        res = match_all_url(page)
        if res == -1:
            print('分析网页匹配所有链接时出错')
            return -1
        else:
            return res
    elif type == 1:
        res = match_all_image(page, key)
        if res == -1:
            print('分析网页匹配所有图片')
            return -1
        else:
            return res


# @description: 处理js渲染的链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: page_url:处理链接
# @return array
def get_url_info(page_url):
    res = []
    browser.get(page_url)
    time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
    text = browser.find_elements_by_xpath("//a")
    for each in text:
        url = each.get_attribute("href")
        if not bool(re.search('google', str(url))) and url is not None:
            res.append(url)
    return res


if __name__ == '__main__':
    url = get_info('陈卓然泰国 华商')
    for each in url:
        print(f"开始处理：{each}")
        page = get_each_page(each)
        if page == -1:  # js动态渲染
            print(f"{each} 为js渲染")
            res_url = get_url_info(each)
            print(f"获取到{each}中所有的链接")
        else:
            res_url = parse_page(page, 1, 'logo')  # 0是匹配链接(2个参数)，1是匹配图片(3个参数)
            print(f"获取到{each}中匹配内容{res_url}")
        if res_url != -1:
            for one in res_url:
                if bool(re.search('logo', str(one))):
                    print(f"发现logo字眼 {one}")


