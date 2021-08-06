import re
import time
from urllib.parse import urlencode
import openpyxl
import xlrd
import requests
from pyquery import PyQuery as pq
from requests import RequestException
from xpinyin import Pinyin


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
    res = ['', '', '', '', '', '']
    arr = ['外文名', '出生日期', '国籍', '婚姻状况']
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
    res = handleTime(res, name)
    res = handleName(res, name)
    return res


# @description: 处理时间
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: res:拿到的结果
# @Param: name:人物姓名
# @Return: array
def handleTime(res, name):
    if res[1] == '':
        res[5] = '未知'
        return res
    match = '(.*?)年(.*?)月(.*?)日'  # 处理存在年月日的
    results = re.findall(match, res[1], re.S)
    if results:
        results = list(results[0])
        results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
        results[2] = results[2] if len(results[2]) == 2 else '0' + results[2]
        res[1] = results[0] + '-' + results[1] + '-' + results[2]
    match = '(.*?)年(.*?)月'  # 处理存在年月的
    results = list(re.findall(match, res[1], re.S))
    if results:
        results = list(results[0])
        results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
        res[1] = results[0] + '-' + results[1] + '-00'
    match = '(.*?)年'  # 处理存在年的
    results = list(re.findall(match, res[1], re.S))
    if results:
        res[1] = results[0] + '-00-00'
    year = res[1].split('-')[0]
    if len(year) != 4:
        log('error.txt', f"{name} 年份格式错误，待处理 \n")
        print(f"{name} 年份格式错误，待处理")
        return res
    else:  # 过滤一定的年份
        if int(year) <= 1955:
            log('error.txt', f"{name} 百度百科人物不匹配 \n")
            print(f"{name} 百度百科人物不匹配")
            res = ['', '', '', '', '', '']
            return res
        if int(year) >= 1981:
            res[5] = '是'
            return res
        else:
            res[5] = '否'
            return res


# @description: 处理姓名（中文转英文）
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: res:拿到的结果
# @Param: name:人物姓名
# @Return: array
def handleName(res, name):
    if res[0] == '':
        p = Pinyin()
        s = p.get_pinyin(name).split('-')
        res[0] = s[0].capitalize() + ' ' + ''.join(s[1:]).capitalize()
        res[0] = res[0].replace(' ', '')
    return res


# @description: 写入表格
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: index:下标
# @Param: dic:字典
def write_excel(index, dic):
    index_num = [3, 8, 11, 13, 50, 56]
    flag = ['外文名', '出生日期', '国籍', '婚姻状况', '对中态度', '是否华裔新生代']
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    for x in range(len(index_num)):
        worksheet.cell(index+2, index_num[x], dic[flag[x]])
    workbook.save(filename="aim_test.xlsx")


if __name__ == '__main__':
    file = 'aim_test.xlsx'
    name_list = enumerate(get_info_excel(file, 1))
    connections = get_info_excel(file, 58)
    for index, name in name_list:
        dic = {}
        page = get_page(name)
        flag = ['外文名', '出生日期', '国籍', '婚姻状况', '对中态度', '是否华裔新生代']
        info = parse_page(page, name)
        # 处理对中态度
        if connections[index] != '':
            info[4] = f"根据存在与国内联系情况，固暂定为:亲中"
        else:
            info[4] = f"未知:中立"
        for flag, info in zip(flag, info):
            dic[flag] = info
        log('result.txt', f"{name} {dic} \n")
        write_excel(index, dic)
        print(f"{dic} 更新成功")


