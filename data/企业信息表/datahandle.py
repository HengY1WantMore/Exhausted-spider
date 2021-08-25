from database import *
from tool.seleImitation import *
from common import log


if __name__ == '__main__':
    sql_name = 'select `中文名`,`官网网址` from `企业信息表(经济学院)`'
    res = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))
    # for index, each in enumerate(res):
    #     index = index + 1
    #     name = each[0]
    #     online = each[1]
    #     record = f"{index} {name}: \n"
    #     log('./record.txt', record)
    # print('Mission Over')

    # for index, each in enumerate(res):
    #     index = index + 1
    #     log('./screen.txt', f"{index}\n")
    #     log('./screen.txt', f"{each[1]}\n")
    #     log('./screen.txt', f"--##########################################\n")
    # print('Mission Over')

    for x in range(169):
        x = x + 91
        imitation('./screen.txt', x).operation()

