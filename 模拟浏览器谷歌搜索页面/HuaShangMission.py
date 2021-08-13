import re
import time
from urllib.parse import urlencode
import requests
import xlrd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import os
import shutil
from tqdm import tqdm


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


# @description: 获取文本某一倍数行的内容
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: location:文本相对位置或者绝对位置
# @Param: multiple:例如所有的3的倍数
# @Return: array
def get_multiple_num(location, multiple):
    res = []
    with open(location, 'r', encoding='utf-8') as f:
        for num, line in enumerate(f):
            if (num - 1) % multiple == 0:
                line = line.replace('\n', '')
                res.append(line)
    return res


# @description: 请求链接保存为指定图片
# @Author: Hengyi
# @Date: 2021/8/11
# @Param: url:请求链接
# @Param: name:想保存的名字
def urllib_download(url, name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }
        if bool(re.search('https', str(url))):  # 则是https请求
            proxies = {'https': 'http://127.0.0.1:7890'}
        else:
            proxies = {'http': 'http://127.0.0.1:7890'}
        r = requests.get(url, proxies=proxies, headers=headers, timeout=4)
        if r.status_code == 200:
            with open(f"./img/{name}.jpg", 'wb') as f:
                f.write(r.content)

        else:
            log('./error.txt', f"{url}\n")
    except Exception as e:
        log('./error.txt', f"{url}\n")


if __name__ == "__main__":
    # file = 'aim_test.xlsx'
    # name = enumerate(get_info_excel(file, 1))
    # country = get_info_excel(file, 8)
    # for index, info in name:
    #     info = '华商 ' + country[index] + ' ' + info
    #     get_info(info)
    # for index, info in name:
    #     log('./info.txt', f"{index} {info}{country[index]} 华商\n")

    # res_list = get_multiple_num('./info.txt', 1)
    # res_effective = []
    # for x in res_list:
    #     x = x.split(' ')
    #     if len(x) == 4:
    #         res_effective.append([x[0], x[3]])
    # for index, url in tqdm(res_effective):
    #     urllib_download(url, index)

    filelist = os.listdir('./img')
    print(filelist)
    for files in filelist:
        filename1 = os.path.splitext(files)[1]  # 读取文件后缀名
        filename0 = os.path.splitext(files)[0]  # 读取文件名
        print(filename0)
        new_name = str(int(filename0) + 1400)
        old_one = os.path.join('./img', files)
        new_one = './img' + new_name + filename1
        shutil.move(old_one, new_one)
    print('mission over')






