import base64
import os
import urllib.request

import openpyxl
import xlrd


# 记录
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


def get_url(location):
    res = []
    with open(location, 'r', encoding='utf-8') as f:
        for num, line in enumerate(f):
            if (num - 1) % 3 == 0:
                line = line.replace('\n', '')
                res.append(line)
    return res


def base():
    f = open('./index.jpg', 'rb')
    image_base = base64.b64encode(f.read())
    f.close()
    image_str = str(image_base)
    real_image_str = image_str[2:len(image_str) - 1]
    os.remove('./index.jpg')
    return 'data:image/jpg;base64,' + real_image_str


def get_image(index, one, name):
    try:
        if one == '':
            log('info_base.txt', f"第{index+1} {name} \n")
            log('info_base.txt', f"#####################\n")
            print(f"第{index+1} {name} 完成")
            return 0
        else:
            urllib.request.urlretrieve(one, f"./resImg/{index+1}+{name}.jpg")
            log('info_base.txt', f"第{index + 1} {name} \n")
            log('info_base.txt', f"Success\n")
            log('info_base.txt', f"#####################\n")
            print(f"第{index+1} {name} 完成")
            return 2
    except Exception as e:
        log('info_base.txt', f"第{index + 1} {name} \n")
        log('info_base.txt', f"Error\n")
        log('info_base.txt', f"#####################\n")
        print(f"**第{index + 1} {name} 错误**")
        return 1


# 写入数据
def write_excel(index, res, col):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    worksheet.cell(index + 2, col, res)
    workbook.save(filename="aim_test.xlsx")


def get_error(location):
    res = []
    with open(location, 'r', encoding='utf-8') as f:
        for num, line in enumerate(f):
            line = line.replace('\n', '')
            res.append(line)
    return res


def get_error_index(name_list, error):
    res = []
    for one in error:
        for index, name in name_list:
            if one == name:
                res.append(index)
    return res


if __name__ == "__main__":
    info = get_url('./info2.txt')
    name = get_info_excel('aim_test.xlsx', 2)
    # name_list = list(enumerate(get_info_excel('aim_test.xlsx', 2)))
    # error = get_error('./error.txt')
    for index, one in enumerate(info):
        one_name = name[index]
        res = get_image(index, one, one_name)
        # if res != 0 and res != 1:
            # write_excel(index, res, 4)
    # print(f"全部完成")
    # index_list = get_error_index(name_list, error)
    # for x in range(len(index_list)):
    #     try:
    #         index = index_list[x]
    #         name = error[x]
    #         f = open(f"./img/{name}.jpg", 'rb')
    #         image_base = base64.b64encode(f.read())
    #         f.close()
    #         image_str = str(image_base)
    #         real_image_str = 'data:image/jpg;base64,' + image_str[2:len(image_str) - 1]
    #         write_excel(index, real_image_str, 4)
    #         print(f"{index} {name} 完成")
    #     except Exception as e:
    #         print(f"{x}错误")
