import time
import pymysql


def mysqlConnection(host='#', user='#', passwd='#', db='#'):
    conn = pymysql.Connect(
        host=host,
        port=3306,
        user=user,
        passwd=passwd,
        db=db,
        charset='utf8')
    return conn


def search_time():
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return now