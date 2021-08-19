import json
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException, SMTP_SSL
import pymongo
import requests

headers = {
    "Host": "stuhealth.jnu.edu.cn",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://stuhealth.jnu.edu.cn",
    "Referer": "https://stuhealth.jnu.edu.cn/",  # 必须带这个参数，不然会报错
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
url = "https://stuhealth.jnu.edu.cn/api/write/main"
error_id = []
repeat = []


def send(subject, text, email):
    """
    :param subject: 邮件标题
    :param text: 邮件文本
    :param email: 邮箱
    :return:
    """
    Subject = subject
    sender = '2911567026@qq.com'  # 发件人邮箱
    receivers = email  # 收件人邮箱

    message = MIMEMultipart('related')
    message['Subject'] = Subject
    message['From'] = sender
    message['To'] = receivers  # 处理多人邮箱
    content = MIMEText(text)
    message.attach(content)

    try:
        server = SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, "ivgovarvmzrldgdj")  # 授权码
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
    except SMTPException as e:
        send(subject, f"发送邮件失败, {e}", '18946973@qq.com')


class mongo:
    def __init__(self, collection, server, db_name, port=27017, user=None, pwd=None):
        self.server = server
        self.collection = collection
        self.db_name = db_name
        self.port = port
        self.user = user
        self.pwd = pwd
        self.collection = pymongo.MongoClient(f"mongodb://{user}:{pwd}@{server}:{port}/{db_name}")[self.db_name][
            self.collection]

    def fine_one(self, order_dic):
        result = self.collection.find_one(order_dic)
        return result

    def insert_one(self, order_dic):
        result = self.collection.insert_one(order_dic)
        return result.inserted_id

    def delete_one(self, order_dic):
        result = self.collection.delete_one(order_dic)
        return result.deleted_count

    def find_all(self, order_dic=None):
        result = self.collection.find(order_dic)
        return result


if __name__ == '__main__':
    data = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    collections = mongo('ClockIn', '112.74.55.247', 'main', 27017, 'main', 'Nbxx17520')
    res_info = collections.find_all()

    for each in res_info:
        time.sleep(0.5)
        body = dict()
        each['mainTable']['declareTime'] = data
        body['mainTable'] = each['mainTable']
        body['secondTable'] = each['secondTable']
        body['jnuid'] = each['jnuid']
        body_new = json.dumps(body)
        results = requests.post(url, data=body_new, headers=headers).text
        false = False
        true = True
        results = eval(results)
        print(results)
        if results['meta']['code'] == 6666:
            note = f"{each['mainTable']['personName']}， 成功打卡于{data}。 感谢支持~"
            send('打卡成功', note, each['email'])
            print(f"{each['mainTable']['personName']} 打卡成功")
        elif results['meta']['code'] == 1111:
            repeat.append([each['email'], each['mainTable']['personName']])
            print(f"{each['mainTable']['personName']} 重复打卡")
        else:
            note = f"{each['mainTable']['personName']}， 于{data}的打卡失败，请手动打卡。 已经收到反馈，全力抢修，十分抱歉~"
            error_id.append(each['email'])
            send('打卡失败', note, each['email'])
            print(f"{each['mainTable']['personName']} 打卡失败")
    if error_id:
        note = f"{error_id} 的打卡失败"
        send('程序发生错误', note, '18946973@qq.com')
    else:
        note = f"打卡程序运行成功，{repeat} 为已经打过卡的"
        send('打卡程序运行成功', note, '18946973@qq.com')
