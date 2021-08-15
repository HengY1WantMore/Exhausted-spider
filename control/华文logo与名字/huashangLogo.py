from database import *
from tool.googleSelenium import *
from tqdm import tqdm

if __name__ == '__main__':
    sql_name = 'select `组织中文名称` from `华文教育组织信息表`'
    name = list(db('219.130.114.4', 'user12', 'user12*#21USER', 'user12_db', 9210).get_all(sql_name))[480:]
    for one in tqdm(name):
        each = one[0]
        Selenium(each, 'logo', 1, 3).main_operation()

