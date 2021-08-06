import re
import time
from urllib.parse import urlencode
import xlrd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

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


# @description: 读取excel文件内容
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: file:相对或者绝对的excel文件
# @Param: col:列
# @Return: res:array
def get_info_excel(file, col):
    res = []
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet = wb.sheet_by_index(0)  # 通过索引获取表格
    col = sheet.col(col)[1:]  # 获取到目标
    for one in col:
        res.append(one.value)
    return res


# @description: 匹配网站
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: info:文本
# @Return: str
def match_url(info):
    try:
        match = '.*?(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)./?'
        return re.match(match, info, re.M | re.I).group(1)
    except Exception as e:
        return ''


# @description: 模拟浏览器请求
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: want:搜索内容
def get_info(want):
    data = {'keyword': want}
    one = str(urlencode(data)).split('=')[1]
    browser.get('https://www.google.com.hk/search?q=' + one)
    time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
    p = browser.find_elements_by_css_selector('.g')
    for x in p:
        content = str(str(x.text).split('\n')).replace('\'', '')
        url = match_url(content)
        log('./record.txt', content + '\n')
        log('./record.txt', url + '\n')
    log('record.txt', '################################################################## \n')


if __name__ == "__main__":
    # file = 'aim_test.xlsx'
    # name = enumerate(get_info_excel(file, 2))
    get_info('你好')


