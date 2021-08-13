import re
from urllib.parse import urlencode

import openpyxl
import requests
import xlrd
from requests import RequestException
from pyquery import PyQuery as pq


# @description: 定位某字符串在数组中的下标
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: arr:目标数组 item:元素
# @Return: int
def location_index(arr, item):
    index = [i for i, a in enumerate(arr) if a == item]
    if not index:
        return -1
    else:
        return index[0]


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


# @description: 百度百科请求人物页面
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: name:任务姓名
# @Return: str
def get_page(name):
    original_name = name
    data = {
        'keyword': name,
    }
    name = str(urlencode(data)).split('=')[1]
    url = 'https://baike.baidu.com/item/' + name
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


# @description: 分析页面
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: page:页面内容
# @Param: name:人物名字
# @Return: array
def parse_page(page, name):
    res = ['']
    arr = ['出生日期']
    doc = pq(page)
    info_left = doc('.basicInfo-block.basicInfo-left').text().replace('\n', ',').split(',')
    group = [info_left[i:i + 2] for i in range(0, len(info_left), 2)]
    for one in group:
        index = location_index(arr, one[0])
        if index != -1:
            res[index] = one[1]
    info_right = doc('.basicInfo-block.basicInfo-right').text().replace('\n', ',').split(',')
    group = [info_right[i:i + 2] for i in range(0, len(info_right), 2)]
    for one in group:
        index = location_index(arr, one[0])
        if index != -1:
            res[index] = one[1]
    res = handleTime(res[0], name)
    return res


# @description: txt记录
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: location:相对或者绝对位置
# @Param: text:记录的内容
def log(location, text):
    with open(location, "a+", encoding='utf-8') as f:
        f.write(text)


# @description: 处理时间
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: res:拿到的结果
# @Param: name:人物姓名
# @Return: array
def handleTime(res, name):
    match = '(.*?)年(.*?)月(.*?)日'  # 处理存在年月日的
    results = re.findall(match, res, re.S)
    if results:
        results = list(results[0])
        results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
        results[2] = results[2] if len(results[2]) == 2 else '0' + results[2]
        res = results[0] + '/' + results[1] + '/' + results[2]
        return res
    match = '(.*?)年(.*?)月'  # 处理存在年月的
    results = list(re.findall(match, res, re.S))
    if results:
        results = list(results[0])
        results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
        res = results[0] + '/' + results[1] + '/00'
        return res
    match = '(.*?)年'  # 处理存在年的
    results = list(re.findall(match, res, re.S))
    if results:
        res = results[0] + '/00/00'
    year = res.split('/')[0]
    if len(year) != 4:
        log('error.txt', f"{name} 年份格式错误，待处理 \n")
        print(f"{name} 年份格式错误，待处理{year}")
        return ''
    else:  # 过滤一定的年份
        if int(year) <= 1955:
            log('error.txt', f"{name} 百度百科人物不匹配 \n")
            print(f"{name} 百度百科人物不匹配{year}")
            return ''
        else:
            return res


# @description: 写入excel文件中
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: index: 编号（写入是从1开始）
# @Param: res: 内容
# @Param: col: 第几行
def write_excel(index, res, col):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    worksheet.cell(index + 2, col, res)
    workbook.save(filename="aim_test.xlsx")


if __name__ == '__main__':
    file = 'aim_test.xlsx'
    name_list = enumerate(get_info_excel(file, 1))
    for index, name in name_list:
        page = get_page(name)
        info = parse_page(page, name)
        print(f"{name} 的结果为 {info}")
        write_excel(index, info, 6)
    print('mission over')