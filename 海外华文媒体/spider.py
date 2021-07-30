import random
from urllib.parse import urlencode

import openpyxl
import requests
import xlrd
from pyquery import PyQuery as pq
from langconv import *

max_times = 5


# 日志记录
def log(location, text):
    with open(location, "a+", encoding='utf-8') as f:
        f.write(text)


# 获取数据
def get_info_excel(file, col):
    res = []
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet = wb.sheet_by_index(0)  # 通过索引获取表格
    col = sheet.col(col)[1:]  # 获取到目标
    for one in col:
        res.append(one.value)
    return res


# 处理书名号
def handleName(one):
    return one.replace('《', '').replace('》', '')


# 进行维基百科的请求
def get_page(index, one, times=1):
    if times >= max_times:
        log('record.txt', f"Error! {one} 脚本无法请求 \n")
        return -1
    original_name = one
    data = {
        'keyword': one,
    }
    one = str(urlencode(data)).split('=')[1]
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    proxies = [
        # {'http': 'http://127.0.0.1:7890'},
        {'https': 'http://127.0.0.1:7890'}
    ]
    proxies = random.choice(proxies)
    url = 'https://zh.wikipedia.org/wiki/' + one
    log('record.txt', f"编号：{index}  {original_name} {times} 次请求该地址{url} \n")
    try:
        response = requests.get(url, proxies=proxies, headers=header)  # 使用代理
        if response.status_code == 200:
            return response.text
    except Exception as e:
        times += 1
        return get_page(original_name, times)


# 分析页面
def parse_page(page, name):
    try:
        doc = pq(page)
        directory_info = doc('.toc').text().replace('\n', ' ')
        labels = doc('.mw-parser-output p').text()
        return[labels, directory_info]
    except Exception as e:
        directory_info = '错误'
        labels = '错误'
        return [labels, directory_info]


# 处理每行字数
def handleNum(text):
    text = str(text)
    a = 0
    res = []
    container = ''
    for x in text:
        container += x
        a += 1
        if a == 100:
            res.append(container)
            a = 0
            container = ''
    res = '\n'.join(res)
    return res


# 处理文字
def handleText(sentence):
    res = []
    for x in sentence:
        x = str(Converter('zh-hans').convert(x))
        res.append(x)
    return res


# 处理注释
def handleAnnotation(text):
    text = text.replace('[1]', '')
    text = text.replace('[2]', '')
    text = text.replace('[3]', '')
    text = text.replace('[4]', '')
    text = text.replace('[5]', '')
    text = text.replace('[6]', '')
    text = text.replace('[7]', '')
    text = text.replace('[8]', '')
    text = text.replace('[9]', '')
    text = text.replace('[10]', '')
    text = text.replace('[11]', '')
    return text


# 写入数据
def write_excel(res, col):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    for x in range(len(res)):
        worksheet.cell(x+2, col, res[x])
    workbook.save(filename="aim_test.xlsx")


if __name__ == "__main__":
    file = 'aim_test.xlsx'
    name = enumerate(list(map(handleName, get_info_excel(file, 3))))
    one = get_info_excel(file, 45)
    two = get_info_excel(file, 46)
    one = handleText(one)
    for x in range(len(one)):
        one[x] = handleAnnotation(one[x])
    write_excel(one, 46)
    two = handleText(two)
    for x in range(len(two)):
        two[x] = handleAnnotation(two[x])
    write_excel(two, 47)

    # for index, info in name:
    #     page_res = get_page(index, info)
    #     if page_res == -1:
    #         break
    #     list_res = parse_page(page_res, info)
    #     content = handleNum(list_res[0])
    #     directory = handleNum(list_res[1])
    #     log('record.txt', '\n \n')
    #     log('record.txt', content)
    #     log('record.txt', '\n \n')
    #     log('record.txt', directory)
    #     log('record.txt', '\n \n')
    #     print(f"{index} {info} 搞定")
