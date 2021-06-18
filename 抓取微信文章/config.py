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