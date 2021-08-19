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
    # info = get_multiple_num('./info.txt', 1)[350:519]
    # info_list = []
    # for index, each in enumerate(info):
    #     index_new = index + 350
    #     each_new = each.split(' ')
    #     # print(index_new, each_new)
    #     # print(len(each_new))
    #     # if len(each_new) != 5:
    #     #     print(index_new, each_new)
    #     name = each_new[2] if each_new[2] != '1' else ''
    #     url = each_new[4] if each_new[4] != '1' else ''
    #     info_list.append([name, url])
    #     # print(name, url)
    #
    # print(info_list)

    # 链接数据库
    # foreign_name = []
    # sql_name = 'select `组织外文名称` from `华文教育组织信息表`'
    # name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))[350:519]
    # for each in name:
    #     foreign_name.append(each[0])
    #     # print(each[0])
    # foreign_name = enumerate(foreign_name)

    # 准备插入外文名字
    # for index, each in foreign_name:
    #     if each is None:
    #         new = info_list[index][0]
    #         id_index = int(index) + 351
    #         sql = f"UPDATE `华文教育组织信息表` SET `组织外文名称` = '{new}' WHERE `序号` = {id_index}"
    #         db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).operation(sql, '插入外文名字')
    # print('mission over')

    # 将链接下载为图片
    for index, each in tqdm(enumerate(info_list)):
        if each[1] != '':
            name = str(index + 351)
            urllib_download(each[1], name)
    print('mission over')

    # 链接数据库
    foreign_logo = []
    sql_name = 'select `组织logo` from `华文教育组织信息表`'
    name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))[350:519]
    for each in name:
        foreign_logo.append(each[0])
    foreign_name = enumerate(foreign_logo)

    # 开始准备插入
    for index, each in foreign_name:
        id_index = int(index) + 351
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

    # 处理空格
    # name_list = []
    # sql_name = 'select `组织外文名称` from `华文教育组织信息表`'
    # name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))
    # for each in name:
    #     name_list.append(each[0])
    # name_list = enumerate(name_list)
    # for index, name in name_list:
    #     index = index + 1
    #     name = str(name).replace('_', ' ')
    #     sql = f"UPDATE `华文教育组织信息表` SET `组织外文名称` = '{name}' WHERE `序号` = {index}"
    #     db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).operation(sql, '去除_')

    # time_handle = []
    # error = []
    # sql_name = 'select `组织成立时间` from `华文教育组织信息表`'
    # time = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))[456:]
    # for each in time:
    #     time_handle.append(each[0])
    # time_handle = enumerate(time_handle)
    # for index, time in time_handle:
    #     index = index + 457
    #     time = time.split('/')
    #     if len(time) != 3:
    #         error.append(index)
    #         continue
    #     if time[1] == '00':
    #         new = time[0]
    #         sql = f"UPDATE `华文教育组织信息表` SET `组织成立时间` = '{new}' WHERE `序号` = {index}"
    #         db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).operation(sql, '更新年份')
    #         continue
    #     if time[2] == '00':
    #         new = time[0] + '/' + time[1]
    #         sql = f"UPDATE `华文教育组织信息表` SET `组织成立时间` = '{new}' WHERE `序号` = {index}"
    #         db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).operation(sql, '更新年份')
    #         continue
    # print(error)
    # print('mission over')




