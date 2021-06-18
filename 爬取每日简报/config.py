import time
import pymysql


def mysqlConnection(host='47.99.140.252', user='hengyiS', passwd='y3PAh4CPzNmRZiDi', db='hengyi_service'):
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