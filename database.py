import pymysql


class db:
    def __init__(self, host, user, pwd, dbname, port=3306, charset='utf8'):
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = dbname
        self.host = host
        self.charset = charset
        self.sql = ""
        self.conn = None

    def connect(self):  # 链接数据库
        try:
            self.conn = pymysql.Connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db, port=int(self.port),
                                        charset='utf8')
            cursor = self.conn.cursor()
            print("数据库链接成功")
            return cursor
        except pymysql.Error as e:
            print("数据库链接失败", e)

    def get_one(self, sql):  # 获取符合sql语句中的第一条
        try:
            cur = self.connect()
            cur.execute(sql)
            return cur.fetchone()
        except pymysql.Error as e:
            print('获取第一条操作错误', e)

    def get_all(self, sql):  # 获取符合sql语句的所有数据
        try:
            cur = self.connect()
            cur.execute(sql)
            return cur.fetchall()
        except pymysql.Error as e:
            print('获取所有数据操作错误', e)

    def get_many(self, sql, n):  # 获取符合sql语句中的部分
        try:
            cur = self.connect()
            cur.execute(sql)
            return cur.fetchmany(n)
        except pymysql.Error as e:
            print('获取部分数据操作错误', e)

    def operation(self, sql, describe):  # 符合提交事务
        try:
            cur = self.connect()
            num = cur.execute(sql)
            self.conn.commit()
            return num
        except pymysql.Error as e:
            print(f"{describe} 操作错误", e)
    
    def blob(self, sql, param, describe):  # 插入blob
        try:
            cur = self.connect()
            num = cur.execute(sql, param)
            self.conn.commit()
            return num
        except pymysql.Error as e:
            print(f"{describe} 操作错误", e)
