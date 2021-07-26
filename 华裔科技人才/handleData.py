import re

import openpyxl
import xlrd
from xpinyin import Pinyin


def get_info_excel(file, col):
    res = []
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet = wb.sheet_by_index(0)  # 通过索引获取表格
    col = sheet.col(col)[1:]  # 获取到目标
    for one in col:
        res.append(one.value)
    return res


def write_name(handleName):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    for x in range(len(handleName)):
        worksheet.cell(x + 2, 3, handleName[x])
    workbook.save(filename="aim_test.xlsx")
    print('名字更新完成')


def write_time(handleTime):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    for x in range(len(handleName)):
        worksheet.cell(x + 2, 8, handleTime[x])
    workbook.save(filename="aim_test.xlsx")
    print('年份更新完成')


def handleName(english, name):
    for x in range(len(english)):
        if english[x] == '':
            p = Pinyin()
            s = p.get_pinyin(name[x]).split('-')
            english[x] = s[0].capitalize() + ' ' + ''.join(s[1:]).capitalize()
    return english


def handleTime(time):
    for x in range(len(time)):
        if time[x] != '':
            match = '(.*?)年(.*?)月(.*?)日'
            results = re.findall(match, time[x], re.S)
            if results:
                results = list(results[0])
                results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
                results[2] = results[2] if len(results[2]) == 2 else '0' + results[2]
                time[x] = results[0] + '-' + results[1] + '-' + results[2]
            match = '(.*?)年(.*?)月'
            results = list(re.findall(match, time[x], re.S))
            if results:
                results = list(results[0])
                results[1] = results[1] if len(results[1]) == 2 else '0' + results[1]
                time[x] = results[0] + '-' + results[1] + '-00'
            match = '(.*?)年'
            results = list(re.findall(match, time[x], re.S))
            if results:
                time[x] = results[0] + '-00-00'
    return time


if __name__ == '__main__':
    english = get_info_excel('aim_test.xlsx', 2)
    name = get_info_excel('aim_test.xlsx', 1)
    time = get_info_excel('aim_test.xlsx', 7)
    handleName = handleName(english, name)
    write_name(handleName)
    handleTime = handleTime(time)
    write_time(handleTime)
