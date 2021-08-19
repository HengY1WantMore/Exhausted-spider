from database import *
from tool.googleSelenium import Selenium
from tqdm import tqdm


if __name__ == '__main__':
    sql_name = 'select `组织中文名称` from `华文教育组织信息表`'
    name = list(db().get_all(sql_name))
    for one in tqdm(name):
        each = one[0]
        Selenium(each, 'logo', 1, 3).want_operation()


