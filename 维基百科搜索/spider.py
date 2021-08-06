import random
from urllib.parse import urlencode
import openpyxl
import requests
import xlrd
from pyquery import PyQuery as pq
from langconv import *

max_times = 5


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


# @description: 处理书名号
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: one:文本
# @Return: res:array
def handle_symbol(one):
    return one.replace('《', '').replace('》', '')


# @description: 进行维基百科请求
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: index:编号
# @Param: one:内容
# @Return: str
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


# @description: 分析页面
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: page:网页内容
# @Return: array
def parse_page(page):
    try:
        doc = pq(page)
        directory_info = doc('.toc').text().replace('\n', ' ')
        labels = doc('.mw-parser-output p').text()
        return[labels, directory_info]
    except Exception as e:
        directory_info = '错误'
        labels = '错误'
        return [labels, directory_info]


# @description: 处理每一行字数（防止记录一行字数过多）
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: text:内容
# @Return: string
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


# @description: 处理繁体字转简体字
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: sentence:内容
# @Return: string
def handleText(sentence):
    res = []
    for x in sentence:
        x = str(Converter('zh-hans').convert(x))
        res.append(x)
    return res


# @description: 处理标注
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: text:内容
# @Return: string
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


# @description: 写入excel文件中
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: index: 编号（写入是从1开始）
# @Param: res: 内容
# @Param: col: 第几行
def write_excel(res, col):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    for x in range(len(res)):
        worksheet.cell(x+2, col, res[x])
    workbook.save(filename="aim_test.xlsx")


if __name__ == "__main__":
    file = 'aim_test.xlsx'
    name = enumerate(list(map(handle_symbol, get_info_excel(file, 3))))
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
