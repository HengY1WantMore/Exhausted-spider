import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import urlencode
import requests
import time
from flashtext import KeywordProcessor


max_times = 3
# browser = webdriver.Chrome('/Users/hengyi/Desktop/chromedriver')
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


# @description: txt记录
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: location:相对或者绝对位置
# @Param: text:记录的内容
def log(location, text):
    with open(location, "a+", encoding='utf-8') as f:
        f.write(text)


# @description: 匹配所有符合的链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: info:文本
# @Return: mixed
def match_all_url(info):
    try:
        match = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
        pattern = re.compile(match)
        result = pattern.findall(info)
        return result
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


# @description: 进行网页请求
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: url_want:链接
# @Param: isOpen:默认关闭链接
# @Param: times:最大请求次数
# @Return: mixed
def get_each_page(url_want, isOpen=0, times=1):
    if times == max_times:
        print(f"{url_want} 无法请求")
        return -1
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    try:
        if isOpen == 1:
            if bool(re.search('http', str(url_want))):  # 则是http请求
                proxies = {'http': 'http://127.0.0.1:7890'}
            else:
                proxies = {'https': 'http://127.0.0.1:7890'}
            response = requests.get(url_want, proxies=proxies, headers=header)  # 使用代理
        else:
            response = requests.get(url_want, headers=header, timeout=5)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            if judge_js(response.text):
                return -1
            else:
                return response.text
        else:
            print(f"请求非200：{url_want}")
            return -1
    except Exception as e:
        times += 1
        return get_each_page(url_want, times)


# @description: 分析页面是不是js渲染
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: text:网页内容
# @Return: boolean
def judge_js(text):
    judge_fun = bool(re.search('function', str(text)))
    judge_p = bool(re.search('<p>', str(text)))
    if judge_fun and not judge_p:
        return True
    else:
        return False


# @description: 在该网页的源码中寻找是否存在关键字
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: page:网页内容
# @Param: key:关键字
# @Return: array
def parse_page(page, key):
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keyword(key)
    keywords_found = keyword_processor.extract_keywords(str(page))
    return keywords_found


# @description: 处理js渲染的链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: page_url:处理链接
# @Param: type:默认是在源码中寻找关键词
# @Param: key:默认关键词为logo
# @return array
def get_page_info(page_url, type=1, key='logo'):
    res = []
    try:
        browser.get(page_url)
        time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
        if type == 0:
            text = browser.find_elements_by_xpath("//a")
            for each in text:
                url = each.get_attribute("href")
                if not bool(re.search('google', str(url))) and url is not None:  # 添加过滤条件
                    res.append(url)
            return res
        elif type == 1:
            text = browser.page_source
            res = parse_page(text, key)
            return res
    except Exception as e:
        return -1


if __name__ == '__main__':
    want = '纽约华商'  # 可以是个数组进行for循环
    key = 'logo'
    url = get_info(want)[:5]
    log('./record.txt', f"请求的关键词为：{want}\n")
    for each in url:
        page = get_each_page(each, 1)  # 通过request来请求网页源代码 第二个参数默认是关闭了代理
        if page == -1:  # js动态渲染/无法请求
            print(f"{each} 为js动态渲染/无法请求")
            res_url = get_page_info(each, 1, key)  # 这里设置的是寻找关键词
        else:
            res_url = parse_page(page, key)
        if not res_url:
            print(f"不存在匹配内容于中{each}")
        elif res_url == -1:
            print(f"请求错误：{each}")
        else:
            print(f"**获取到 {each} 中存在关键字**")
            log('./record.txt', f"获取到 {each} 中存在关键字\n")
    log('./record.txt', f"#######################################\n")
    browser.quit()
    exit()
