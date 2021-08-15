from database import *
from tqdm import tqdm
from common import get_multiple_num
from common import urllib_download

if __name__ == '__main__':
    # name_list = []
    # sql_name = 'select `组织中文名称` from `华文教育组织信息表`'
    # name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))

    # 形成记录本
    # for each in name:
    #     name_list.append(each[0])
    # name_list = enumerate(name_list)
    # for index, name in name_list:
    #     log('./info.txt', f"下标为：{index}，名字为：{name} 英文名字为: logo地址: \n")

    # 处理数据
    # info = get_multiple_num('./info.txt', 1)[:100]
    # info_list = []
    # for index, each in enumerate(info):
    #     each = each.split(' ')
    #     name = each[2] if each[2] != '1' else ''
    #     url = each[4] if each[4] != '1' else ''
    #     info_list.append([name, url])

    # 链接数据库
    # foreign_name = []
    # sql_name = 'select `组织外文名称` from `华文教育组织信息表`'
    # name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))[:100]
    # for each in name:
    #     foreign_name.append(each[0])
    # foreign_name = enumerate(foreign_name)

    # 准备插入外文名字
    # for index, each in foreign_name:
    #     if each is None:
    #         new = info_list[index][0]
    #         id_index = int(index) + 1
    #         sql = f"UPDATE `华文教育组织信息表` SET `组织外文名称` = '{new}' WHERE `序号` = {id_index}"
    #         db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).operation(sql, '插入外文名字')
    # print('mission over')

    # 将链接下载为图片
    # for index, each in tqdm(enumerate(info_list)):
    #     if each[1] != '':
    #         name = str(index + 1)
    #         urllib_download(each[1], name)
    # print('mission over')

    # 链接数据库
    foreign_logo = []
    sql_name = 'select `组织logo` from `华文教育组织信息表`'
    name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))[:100]
    for each in name:
        foreign_logo.append(each[0])
    foreign_name = enumerate(foreign_logo)

    # 开始准备插入
    for index, each in foreign_name:
        id_index = int(index) + 1
        if each is None:
            try:
                with open(f"./img/{id_index}.jpg", 'rb') as f:
                    img = f.read()
                    f.close()
                    real_image_str = str(img)[2:len(str(img)) - 1]
                    sql = f"UPDATE `华文教育组织信息表` SET `组织logo` = '{real_image_str}' WHERE `序号` = {id_index}"
                    db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).operation(sql, '插入logo')
            except Exception as e:
                # print(f"{id_index} 错误/不存在")
                continue
    print('mission over')





