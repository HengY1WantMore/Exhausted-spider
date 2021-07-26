import time
from urllib.parse import urlencode
import openpyxl
import xlrd
import requests
from pyquery import PyQuery as pq
from requests import RequestException


def find_all_index(arr, item):
    index = [i for i, a in enumerate(arr) if a == item]
    if not index:
        return -1
    else:
        return index[0]


def log(text):
    with open('log.txt', "a+") as f:
        f.write(text)


def get_info_excel(file):
    res = []
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet = wb.sheet_by_index(0)  # 通过索引获取表格
    col = sheet.col(1)[1:]  # 获取到目标
    for one in col:
        res.append(one.value)
    return res


def get_page(name):
    original_name = name
    data = {
        'keyword': name,
    }
    name = str(urlencode(data)).split('=')[1]
    url = 'https://baike.baidu.com/item/' + name
    localtime = str(time.asctime(time.localtime(time.time())))
    log(f"对象名字：{original_name} :  采集地址{url}  采集时间：{localtime} \n")
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    response = requests.get(url, headers=header)
    try:
        if response.status_code == 200:
            return response.text.replace('&nbsp;', '')
    except RequestException:
        print('请求出错')
        return None


def parse_page(page):
    res = ['', '', '', '']
    arr = ['外文名', '出生日期', '国籍', '婚姻状况']
    doc = pq(page)
    info_left = doc('.basicInfo-block.basicInfo-left').text().replace('\n', ',').split(',')
    group = [info_left[i:i + 2] for i in range(0, len(info_left), 2)]
    for one in group:
        index = find_all_index(arr, one[0])
        if index != -1:
            res[index] = one[1]
    info_right = doc('.basicInfo-block.basicInfo-right').text().replace('\n', ',').split(',')
    group = [info_right[i:i + 2] for i in range(0, len(info_right), 2)]
    for one in group:
        index = find_all_index(arr, one[0])
        if index != -1:
            res[index] = one[1]
    return res


def write_excel(index, dic):
    index_num = [3, 8, 11, 13]
    flag = ['外文名', '出生日期', '国籍', '婚姻状况']
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    for x in range(len(index_num)):
        worksheet.cell(index+2, index_num[x], dic[flag[x]])
    workbook.save(filename="aim_test.xlsx")


if __name__ == '__main__':
    file = 'aim_test.xlsx'
    name_list = enumerate(get_info_excel(file))
    for index, one in name_list:
        dic = {}
        page = get_page(one)
        flag = ['外文名', '出生日期', '国籍', '婚姻状况']
        info = parse_page(page)
        for flag, info in zip(flag, info):
            dic[flag] = info
        write_excel(index, dic)
        dic_x = {'外文名': '', '出生日期': '', '国籍': '', '婚姻状况': ''}
        if dic != dic_x:
            print(index, dic)


